package NGCP::Template::Plugin::Utils 1.000;

use strict;
use warnings;

use parent qw(Template::Plugin);

use MIME::Base64 ();
use Data::Dumper ();
use Config::General ();
use YAML::XS ();

sub new {
    my ($class, $context, @params) = @_;

    bless {
        _CONTEXT => $context,
    }, $class;
}

sub encode_base64 {
    my ($self, @params) = @_;
    return MIME::Base64::encode($params[0], '');
}

sub to_perl {
    my ($self, @params) = @_;
    my $d = Data::Dumper->new([ $params[0] ]);
    $d->Purity(1)->Terse(1)->Sortkeys(1)->Deepcopy(1);
    return $d->Dump;
}

sub to_config_general {
    my ($self, @params) = @_;
    my $conf = Config::General->new(
        SaveSorted  => 1,
    );
    return $conf->save_string($params[0]);
}

sub to_yaml {
    my ($self, @params) = @_;
    return q{} unless $params[0];
    return YAML::XS::Dump($params[0]);
}

sub get_ref {
    my ($self, @params) = @_;
    return ref $params[0];
}

sub file_exists {
    my ($self, @params) = @_;
    return -e $params[0];
}

sub file_readable {
    my ($self, @params) = @_;
    return -r $params[0];
}

sub quote_meta {
    my ($self, $str) = @_;
    return quotemeta($str);
}

1;

__END__

=encoding UTF-8

=head1 NAME

NGCP::Template::Plugin::Utils - Utils plugin

=head1 VERSION

Version 1.000

=head1 DESCRIPTION

This module provides common, stateless utility methods for NGCP templates
using Template::Plugin mechanism.

[% USE Utils %]

=head1 METHODS

=over 8

=item [% encoded = Utils.encode_base64(unencoded) %]

Converts the given input String to base64.

=item [% serialized = Utils.to_perl(object) %]

Serializes the given input object to string (perl syntax).

=item [% serialized = Utils.to_config_general(object) %]

Serializes the given input object to string (Config::General syntax).

=item [% serialized = Utils.to_yaml(object) %]

Serializes the given input object to string (YAML syntax).

=item [% Utils.get_ref(object) %]

Get the variable type.

=item [% Utils.quote_meta(string) %]

Escape all non-ASCII characters in the string with a backslash.

=back

=head1 AUTHOR

Rene Krenn, C<< <rkrenn@sipwise.com> >>

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
