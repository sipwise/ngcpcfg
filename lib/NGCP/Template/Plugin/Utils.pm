package NGCP::Template::Plugin::Utils 1.000;

use strict;
use warnings;

use parent qw(Template::Plugin);

use MIME::Base64 ();
use Data::Dumper ();
use Config::General ();
use Crypt::PK::RSA ();

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
    return Data::Dumper::Dumper($params[0]);
}

sub to_config_general {
    my ($self, @params) = @_;
    my $conf = Config::General->new();
    return $conf->save_string($params[0]);
}

sub get_ref {
    my ($self, @params) = @_;
    return ref $params[0];
}

sub get_private_key_pem {
    my ($self, @params) = @_;
    return unless $params[0];
    my $pk = Crypt::PK::RSA->new();
    $pk->import_key($params[0]);
    die('not a private key: ' . Dumper($params[0])) unless $encrytper->is_private();
    return $pk->export_key_pem('private');
}

sub get_public_key_pem {
    my ($self, @params) = @_;
    return unless $params[0];
    my $pk = Crypt::PK::RSA->new();
    $pk->import_key($params[0]);
    die('not a public key: ' . Dumper($params[0])) if $encrytper->is_private();
    return $pk->export_key_pem('public');
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

=item [% Utils.get_ref(object) %]

Get the variable type.

=item [% pem = Utils.get_private_key_pem(private key) %]

Converts the given RSA private key (JWK data structure) to .pem.

=item [% pem = Utils.get_public_key_pem(public key) %]

Converts the given RSA public key (JWK data structure) to .pem.

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
