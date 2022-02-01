package NGCP::Template 1.000;

use strict;
use warnings;

use Carp;
use NGCP::Template::Object;

use parent qw(Template);

sub new
{
    my ($this, @args) = @_;
    my $class = ref $this || $this;

    # The config can be passed as a hash ref or as a hash.
    my $config;
    if (ref $args[0] eq 'HASH') {
        $config = $args[0];
    } else {
        $config = { @args };
    }

    my $self = Template->new({
        ENCODING => 'utf8',
        ABSOLUTE => 1,
        RELATIVE => 1,
        EVAL_PERL => 1,
        PLUGIN_BASE => 'NGCP::Template::Plugin',
        %{$config},
    });

    return bless $self, $class;
}

sub process
{
    my ($self, $template, $vars, $output, @opts) = @_;

    croak('missing required template variables') unless defined $vars;

    # Inject our ngcp object variable.
    $vars->{ngcp} = NGCP::Template::Object->new($vars);

    return $self->SUPER::process($template, $vars, $output, @opts);
}

1;

__END__

=encoding UTF-8

=head1 NAME

NGCP::Template - Custom NGCP Template Toolkit module

=head1 VERSION

Version 1.000

=head1 DESCRIPTION

This module provides a custom instance of the Template Toolkit so that it can
be used to expose all the necessary functionality expected from within the NGCP
template files, including our ngcp object variable.

=head1 METHODS

=over 8

=item $tt = NGCP::Template->new($config)

Create a new Template compatible object that can be used in place of the stock
Template module.

The $config argument contains any additional arguments for the Template
constructor.

=item $tt->process($input, \%vars, $output, %options)

This method injects the ngcp object variable into the %vars, and calls the
parent Template process() method.

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
