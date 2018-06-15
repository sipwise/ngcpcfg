package NGCP::Template 1.000;

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
    my ($self, $host, $role) = @_;

    if (not defined $self->{config}{hosts}{$host}) {
        $host = 'self';
    }

    if (any { $_ eq $role } @{$self->{config}{hosts}{$host}{role}}) {
        return 1;
    }

    return 0;
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
    my ($self, $host) = @_;

    if (not defined $self->{config}{hosts}{$host}) {
        $host = 'self';
    }

    return $self->{config}{hosts}{$host}{peer};
}

1;

__END__

=encoding UTF-8

=head1 NAME

NGCP::Template - NGCP module for the Template::Tolkit framework

=head1 VERSION

Version 1.000

=head1 DESCRIPTION

This module provides the methods for the ngcp object that can be used within
the NGCP templates. This makes it easier to use instead of the old library
of code executed via the C<PROCESS> directive.

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
