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

    if (not defined $self->{config}{hosts}{$hostname}) {
        $hostname = 'self';
    }

    if (any { m/^$role$/ } @{$self->{config}{hosts}{$hostname}{role}}) {
        return 1;
    }

    return 0;
}

sub get_hostname
{
    my $self = shift;

    # Do not trust hostname(1) as this might differ from the hostname of
    # the system which runs the installer, instead rely on /etc/hostname
    open my $hh, '<', '/etc/hostname' or die "Error opening /etc/hostname";
    my $hostname = <$hh>;
    close $hh;
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

    if (defined $self->{config}{hosts}{self} and
        not defined $self->{config}{hosts}{$nodename}) {
        $nodename = 'self';
    }

    $self->{nodename} = $nodename;

    return $nodename;
}

sub get_peername
{
    my ($self, $hostname) = @_;

    if (not defined $self->{config}{hosts}{$hostname}) {
        $hostname = 'self';
    }

    return $self->{config}{hosts}{$hostname}{peer};
}

sub get_firstname
{
    my ($self, $hostname) = @_;

    if (not defined $self->{config}{hosts}{$hostname}) {
        return 'self';
    } else {
        my $peername = $self->get_peername($hostname);
        my @hosts = ($hostname, $peername);

        return (sort @hosts)[0];
    }
}

sub get_mgmt_name
{
    my ($self) = shift;
    my $filename = '/etc/ngcp_mgmt_node';

    open my $hh, '<', $filename or die "Error opening $filename";
    my $mgmt_name = <$hh>;
    close $hh;
    chomp $mgmt_name;
    die "Fatal error retrieving mgmt_name [$mgmt_name]" unless length $mgmt_name;

    return $mgmt_name;
}

sub get_mgmt_node
{
    my ($self) = shift;

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

=item $hostname = $t->get_hostname()

Returns the hostname of the node calling this function.

=item $nodename = $t->get_nodename()

Returns the nodename of the node calling this function.

=item $peername = $t->get_peername($hostname)

Returns the peer name for a given $hostname.

=item $firstname = $t->get_firstname($hostname)

Returns the (alphabetically) first hostname of a node pair for a given
$hostname.

=item $mgmtname = $t->get_mgmt_name()

Returns the name of the management node calling this function.

=item $mgmtnode = $t->get_mgmt_node()

Returns the NGCP management node shared name.

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
