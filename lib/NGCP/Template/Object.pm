package NGCP::Template::Object 1.000;

use strict;
use warnings;

use List::Util qw(any);

sub new
{
    my ($this, $config) = @_;
    my $class = ref $this || $this;

    my $self = {
        config => $config,
    };

    return bless $self, $class;
}

sub has_role
{
    my ($self, $hostname, $role) = @_;

    if (not exists $self->{config}{hosts}{$hostname}) {
        $hostname = 'self';
    }

    my %roles = map { $_ => 1 } @{$self->{config}{hosts}{$hostname}{role}};

    # We need to handle the LI case specially, because it is conditional on
    # other keys, so we cannot make it match on wildcards unconditionally.
    if (exists $roles{li}) {
        if ($self->{config}{intercept}{enable} ne 'yes') {
            delete $roles{li};
        } elsif ($self->{config}{cluster_sets}{type} eq 'distributed') {
            # The LI role has a virtual role companion, which is active only
            # in distributed mode.
            $roles{li_dist} = 1;
        }
    }

    return 1 if any { m/^$role$/ } keys %roles;
    return 0;
}

sub get_version
{
    my $self = shift;

    my $filename = '/etc/ngcp_upgrade_version';
    unless (-e $filename) {
        $filename = '/etc/ngcp_version';
    }

    open my $hh, '<', $filename or die "Error opening $filename";
    my $version = <$hh>;
    close $hh;
    chomp $version;
    die "Fatal error retrieving ngcp_version [$version]" unless length $version;

    return $version;
}

sub get_hostname
{
    my $self = shift;

    my $hostname = qx(ngcp-hostname);
    chomp $hostname;
    die "Fatal error retrieving hostname [$hostname]" unless length $hostname;

    return $hostname;
}

sub get_nodename
{
    my $self = shift;

    return $self->{nodename} if exists $self->{nodename};

    my $filename = '/etc/ngcp_ha_node';
    $filename = '/etc/ngcp_nodename' unless -f $filename;
    open my $hh, '<', $filename or die "Error opening $filename";
    my $nodename = <$hh>;
    close $hh;
    chomp $nodename;

    die "Fatal error retrieving nodename [$nodename]" unless length $nodename;

    if (exists $self->{config}{hosts}{self} and
        not exists $self->{config}{hosts}{$nodename}) {
        $nodename = 'self';
    }

    $self->{nodename} = $nodename;

    return $nodename;
}

sub get_pairname
{
    my ($self, $hostname) = @_;

    my $ngcp_type = $self->{config}{general}{ngcp_type};
    if ($ngcp_type eq 'carrier') {
        if ($hostname =~ m/^(\w+[0-9])[ab]?$/) {
            return $1;
        }
    } elsif ($ngcp_type eq 'sppro') {
        if ($hostname =~ m/^(sp)[12]$/) {
            return $1;
        }
    } elsif ($ngcp_type eq 'spce') {
        return 'spce';
    }

    die "Error: unknown hostname format $hostname for this host type\n";
}

sub get_peername
{
    my ($self, $hostname) = @_;

    if (not exists $self->{config}{hosts}{$hostname}) {
        $hostname = 'self';
    }

    return $self->{config}{hosts}{$hostname}{peer};
}

sub get_firstname
{
    my ($self, $hostname) = @_;

    if (not exists $self->{config}{hosts}{$hostname}) {
        return 'self';
    } else {
        my @hosts = ($hostname);
        my $peername = $self->get_peername($hostname);
        push @hosts, $peername if defined $peername;

        return (sort @hosts)[0];
    }
}

sub get_dbnode
{
    my ($self, $hostname) = @_;

    if (not exists $self->{config}{hosts}{$hostname}) {
        return 'self';
    }
    return $self->{config}{hosts}{$hostname}{dbnode};
}

sub get_mgmt_pairname
{
    my $self = shift;

    my $ngcp_type = $self->{config}{general}{ngcp_type};

    if ($ngcp_type eq 'carrier') {
        foreach my $hostname (keys %{$self->{config}{hosts}}) {
            if ($self->has_role($hostname, 'mgmt') and
                $hostname =~ m/^(\w+[0-9])[ab]?$/)
            {
              return $1;
            }
        }
    } else {
        return 'sp';
    }

    return;
}

sub get_mgmt_node
{
    my $self = shift;

    warnings::warnif('deprecated', 'deprecated alias for get_mgmt_pairname()');
    return $self->get_mgmt_pairname();
}

sub get_instances
{
    my ($self, $hostname) = @_;
    my $res = [];

    if (not exists $self->{config}{hosts}{$hostname}) {
        return $res;
    }
    if (not exists $self->{config}{instances}) {
        return $res;
    }
    my $peername = $self->{config}{hosts}{$hostname}{peer};
    foreach my $instance (@{$self->{config}{instances}}) {
        if ($instance->{host} eq $hostname or $instance->{host} eq $peername) {
            push @{$res}, $instance;
        }
    }
    return $res;
}

sub get_ssh_pub_key
{
    my ($self, $key_type) = @_;

    my $ssh_keys_dir = '/etc/ngcp-config/shared-files/ssh/';
    my $ssh_key_file = "$ssh_keys_dir/id_${key_type}.pub";
    open my $fh, '<', $ssh_key_file or die "Error opening $ssh_key_file";
    my $ssh_pub_key = <$fh>;
    close $fh;
    chomp $ssh_pub_key;
    die "Fatal error retrieving SSH public key" unless length $ssh_pub_key;

    return $ssh_pub_key;
}

sub net_ip_expand
{
    my ($self, $ip) = @_;

    while ($ip =~ m/::/ && (() = $ip =~ m/:/g) < 8) {
        $ip =~ s/::/::0:/;
    }
    $ip =~ s/::/:/;
    $ip =~ s/^:/0:/;
    $ip =~ s/:$/:0/;

    return $ip;
}

sub replace_metavars
{
    my ($self, $string) = @_;

    my $version = $self->get_version();
    my %metavars = (
        '%' => '%',
        'v' => $version,
    );

    my $subst_metavar = sub {
        my $var = shift;

        if (exists $metavars{$var}) {
            return $metavars{$var};
        } else {
            warn "unknown metavar in hook: %%$var\n";
            return "\%$var";
        }
    };

    $string =~ s/\%(.)/$subst_metavar->($1)/eg;

    return $string;
}

1;

__END__

=encoding UTF-8

=head1 NAME

NGCP::Template::Object - NGCP object variable for Template::Toolkit framework

=head1 VERSION

Version 1.000

=head1 DESCRIPTION

This module provides the methods for the ngcp object that can be used within
the NGCP templates. This makes it easier to use instead of the old library
of code executed via the C<PROCESS> directive.

=head1 METHODS

=over 8

=item $t = NGCP::Template::Object->new($config)

Create a new object that can be used from within the Tamplate Toolkit, via
the B<ngcp> internal variable, such as C<ngcp.some_method(argument)>.

The $config argument contains the deserialized ngcp-config YAML configuration.

=item $bool = $t->has_role($hostname, $role)

Checks whether the $hostname node has the $role.

=item $version = $t->get_version()

Returns the NGCP version.

=item $hostname = $t->get_hostname()

Returns the hostname of the node calling this function.

=item $nodename = $t->get_nodename()

Returns the nodename of the node calling this function.

=item $pairname = $t->get_pairname($hostname)

Returns the pair name for a given $hostname. This is the shared HA name for
a pair of nodes (for example 'db01' for 'db01a').

=item $peername = $t->get_peername($hostname)

Returns the peer name for a given $hostname.

=item $firstname = $t->get_firstname($hostname)

Returns the (alphabetically) first hostname of a node pair for a given
$hostname.

=item $dbname = $t->get_dbname($hostname)

Returns the database name for this node.

=item $mgmtnode = $t->get_mgmt_pairname()

Returns the NGCP management node pairname.

=item $mgmtnode = $t->get_mgmt_node()

This function is a deprecated alias for $t->get_mgmt_pairname(). It will be
removed in the future.

=item $ssh_pub_keye = $t->get_ssh_pub_key($key_type)

Returns the SSH public key with $key_type ('rsa', 'ed25519', etc.) from
the ngcpcfg shared-files storage.

=item $ip = $t->net_ip_expand($ipaddr)

Returns the expanded form of the IP address. Supports IPv4 and IPv6.

=item $str = $t->replace_metavars($str)

Returns the string $str with the %-style meta-variables expanded.

Current known meta-variables are:

=over 4

=item %v

The NGCP version.

=back

=back

=head1 AUTHOR

Guillem Jover, C<< <gjover@sipwise.com> >>

=head1 LICENSE

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

=cut
