package NGCP::Template::Plugin::Utils 1.000;

use strict;
use warnings;

use parent 'Template::Plugin';

use MIME::Base64 qw();

sub new {
    my ($class, $context, @params) = @_;

    bless {
        _CONTEXT => $context,
    }, $class;
}

sub encode_base64 {

    my ($self, @params) = @_;
    return MIME::Base64::encode($params[0],'');

}

1;
