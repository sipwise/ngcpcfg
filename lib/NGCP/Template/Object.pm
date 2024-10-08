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

sub get_online_cpus
{
    my $self = shift;

    my $nproc = qx(nproc);
    $nproc = qx(getconf _NPROCESSORS_ONLN 2>/dev/null) if $?;
    chomp $nproc;

    return $nproc // 1;
}

sub get_supported_roles
{
    return [ qw(
        db
        lb
        li
        li_dist
        mgmt
        proxy
        rtp
        storage
    ) ];
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
    my ($self, $hostname) = @_;

    # If we are asked about the nodename for a matching hostname, try to fetch
    # that.
    if (defined $hostname) {
        if (exists $self->{config}{hosts}{$hostname} &&
            exists $self->{config}{hosts}{$hostname}{nodename}) {
            return $self->{config}{hosts}{$hostname}{nodename};
        } else {
            # Fallback to inferring the nodename from the hostname.
            if ($hostname eq 'self' or $hostname eq 'spce') {
                return 'spce';
            } elsif ($hostname =~ m/^sp[1-9]$/) {
                return $hostname;
            } elsif ($hostname =~ m/^\w+\d+([a-i])$/) {
                my $char = $1;
                my $nodeindex = ord($char) - ord('a') + 1;

                return "sp$nodeindex";
            } else {
                die "Fatal error generating nodename for $hostname\n";
            }
        }
    }

    # Otherwise, get the nodename for this host.
    return $self->{nodename} if exists $self->{nodename};

    my $nodename = qx(ngcp-nodename);
    chomp $nodename;
    die "Fatal error retrieving nodename [$nodename]" unless length $nodename;

    $self->{nodename} = $nodename;

    return $nodename;
}

sub get_pairname
{
    my ($self, $hostname) = @_;

    my $ngcp_type = $self->{config}{general}{ngcp_type};
    if ($ngcp_type eq 'carrier') {
        if ($hostname =~ m/^(\w+\d+)[a-i]?$/) {
            return $1;
        }
    } elsif ($ngcp_type eq 'sppro') {
        if ($hostname =~ m/^(sp)[1-9]$/) {
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

sub get_sibnames
{
    my ($self, $hostname) = @_;
    my $pairname = $self->get_pairname($hostname);
    my @sibnames;

    foreach my $thishost (keys %{$self->{config}{hosts}}) {
        next if $thishost eq $hostname;

        my $thispair = $self->get_pairname($thishost);
        next if $thispair ne $pairname;

        push @sibnames, $thishost;
    }

    my @res = sort @sibnames;
    return @res;
}

sub get_firstname
{
    my ($self, $hostname) = @_;

    if (not exists $self->{config}{hosts}{$hostname}) {
        return 'self';
    } else {
        my @hosts = ($hostname, $self->get_sibnames($hostname));

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
                $hostname =~ m/^(\w+\d+)[a-i]?$/)
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

sub get_hosts
{
    my ($self, $filter) = @_;

    my $site = $filter->{site} // 'current';
    $filter->{status} //= [ qw(online inactive) ];
    my %status = (
        online => 0,
        offline => 0,
        inactive => 0,
    );
    $status{$_} = 1 foreach @{$filter->{status}};

    my $hosts = $self->{config}{sites}{$site}{hosts};

    my @hosts;
    foreach my $host (sort keys %{$hosts}) {
        next unless $status{$hosts->{$host}{status}};

        push @hosts, $host;
    }

    my @res = sort @hosts;
    return @res;
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
            # data coming from $hostname
            foreach my $iface (@{$instance->{interfaces}}) {
                my $ifname = $iface->{name};
                $iface->{netmask} = $self->{config}{hosts}{$hostname}{$ifname}{netmask};
                if( exists $self->{config}{hosts}{$hostname}{$ifname}{cluster_set}) {
                    $iface->{cluster_set} = $self->{config}{hosts}{$hostname}{$ifname}{cluster_set};
                }
            }
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

Create a new object that can be used from within the Template Toolkit, via
the B<ngcp> internal variable, such as C<ngcp.some_method(argument)>.

The $config argument contains the deserialized ngcp-config YAML configuration.

=item $cpus = $t->get_online_cpus()

Returns the number of online CPUs on the system.

This can be used to compute values in templates that depend on the amount
of cores.

=item $bool = $t->get_supported_roles()

Returns the list of roles supported by NGCP.

=item $bool = $t->has_role($hostname, $role)

Checks whether the $hostname node has the $role.

=item $version = $t->get_version()

Returns the NGCP version.

=item $hostname = $t->get_hostname()

Returns the hostname of the node calling this function.

=item $nodename = $t->get_nodename([$hostname])

Returns the nodename of the node calling this function, or of $hostname
if specified.

=item $pairname = $t->get_pairname($hostname)

Returns the pair name for a given $hostname. This is the shared HA name for
a pair of nodes (for example 'db01' for 'db01a').

=item $peername = $t->get_peername($hostname)

Returns the peer name for a given $hostname.

=item @sibnames = $t->get_sibnames($hostname)

Returns a sorted list of sibling names for the pair of a given $hostname.
This is all other hostnames that are part of the same pair, except for
$hostname.

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

=item @hosts = $t->get_hosts($filter)

Returns an array of hosts that match the %filter criteria.
If no %filter has been specified, it returns all hosts.
The current filter options are:

=over

=item B<site>

This is a scalar that specifies the site name to use.
It defaults to B<current>.

=item B<status>

This is an arrayref that contains a list of the status names to filter on,
from one of B<online>, B<offline> and B<inactive>.
The default status list is B<online> and B<inactive>.

=back

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
