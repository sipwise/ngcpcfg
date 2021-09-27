#!/usr/bin/perl

use strict;
use warnings;

use Test::More;

plan tests => 32;

use_ok('NGCP::Template::Object');

my $config = {
    general => {
        ngcp_type => 'spce',
    },
    intercept => {
        enable => 'no',
    },
    cluster_sets => {
        type => 'central',
    },
    hosts => {
        self => {
            role => [ qw(db lb proxy rtp) ],
        },
        sp1 => {
            role => [ qw(mgmt db lb proxy rtp storage) ],
            peer => 'sp2',
        },
        sp2 => {
            peer => 'sp1',
        },
        prx01a => {
            role => [ qw(li proxy) ],
            peer => 'prx01b',
            dbnode => 'db01',
        },
        web01a => {
            role => [ qw(mgmt) ],
        },
    },
};

my $obj = NGCP::Template::Object->new($config);

# Check has_role().
ok(!$obj->has_role('non-existent', 'storage'),
    'host unknown has storage role');
ok($obj->has_role('self', '.*'), 'host self has wildcard role');
ok($obj->has_role('self', 'db'), 'host self has db role');
ok($obj->has_role('self', 'lb'), 'host self has lb role');
ok($obj->has_role('self', 'proxy'), 'host self has proxy role');
ok($obj->has_role('self', 'rtp'), 'host self has rtp role');
ok(!$obj->has_role('self', 'storage'), 'has self does not have storage role');

ok($obj->has_role('sp1', 'storage'), 'host sp1 has storage role');

ok(!$obj->has_role('prx01a', 'li'), 'host prx01a does not have li role');
ok(!$obj->has_role('prx01a', 'li_dist'),
    'host prx01a does not have li_dist virtual role');
{
    local $obj->{config}->{intercept}{enable} = 'yes';
    ok($obj->has_role('prx01a', 'li'),
        'host prx01a has li role (with intercept enabled)');
    ok(!$obj->has_role('prx01a', 'li_dist'),
        'host prx01a does not have li_dist virtual roles (with intercept enabled)');

    local $obj->{config}->{cluster_sets}{type} = 'distributed';
    ok($obj->has_role('prx01a', 'li'),
        'host prx01a has li role (with cluster_sets as distributed)');
    ok($obj->has_role('prx01a', 'li_dist'),
        'host prx01a has li_dist virtual role (with cluster_sets as distributed)');
}

# Check get_peername().
is($obj->get_peername('self'), undef, 'host self has no peer');
is($obj->get_peername('sp1'), 'sp2', 'host sp1 has sp2 as peer');
is($obj->get_peername('prx01a'), 'prx01b', 'host prx01a has prx01b as peer');

# Check get_firstname().
is($obj->get_firstname('non-existent'), 'self',
    'host unknown has self as first name');
is($obj->get_firstname('self'), 'self', 'host self has self as first name');
is($obj->get_firstname('sp1'), 'sp1', 'host sp1 has sp1 as first name');
is($obj->get_firstname('sp2'), 'sp1', 'host sp2 has sp1 as first name');

# Check get_mgmt_pairname().
is($obj->get_mgmt_pairname(), 'sp', 'spce has sp as mgmt pairname');
{
    delete local $obj->{config}{hosts}{self};
    local $obj->{config}{general}{ngcp_type} = 'sppro';
    is($obj->get_mgmt_pairname(), 'sp', 'sppro has sp as mgmt pairname');

    delete local $obj->{config}{hosts}{sp1};
    delete local $obj->{config}{hosts}{sp2};
    local $obj->{config}{general}{ngcp_type} = 'carrier';
    is($obj->get_mgmt_pairname(), 'web01', 'carrier has web01 as mgmt pairname');
}

# Check get_dbnode().
is($obj->get_dbnode('non-existent'), 'self', 'host unknown has self as dbnode');
is($obj->get_dbnode('prx01a'), 'db01', 'host prx01a has db01 as dbnode');

# Check net_ip_expand().
is($obj->net_ip_expand('1:2::5:20'),
    '1:2:0:0:0:0:5:20',
    'normalize IPv6 1:2::5:20');
is($obj->net_ip_expand('001:2::0005:020'),
    '001:2:0:0:0:0:0005:020',
    'normalize IPv6 001::0005:020');
is($obj->net_ip_expand('1::0'),
    '1:0:0:0:0:0:0:0',
    'normalize IPv6 1::0');

## instances
$config->{instances} = [
    {name => 'A', host => 'sp2'},
    {name => 'B', host => 'sp3'},
];
my $obj = NGCP::Template::Object->new($config);

# Check get_instances(hostname).
my $instances = [{name=>'A',host=>'sp2'}];
is_deeply($obj->get_instances('sp1'), $instances,
    'host sp1 has one instances defined');
is_deeply($obj->get_instances('sp2'), $instances,
    'host sp2 has one instances defined');
