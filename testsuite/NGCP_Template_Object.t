#!/usr/bin/perl

use strict;
use warnings;

use Cwd;
use Test::More;

plan tests => 48;

use_ok('NGCP::Template::Object');

my $cfg_ce = {
    general => {
        ngcp_type => 'spce',
    },
    intercept => {
        enable => 'no',
    },
    hosts => {
        self => {
            role => [ qw(db lb proxy rtp) ],
        },
    },
};

my $cfg_pro = {
    general => {
        ngcp_type => 'sppro',
    },
    intercept => {
        enable => 'no',
    },
    hosts => {
        sp1 => {
            role => [ qw(mgmt db lb proxy rtp storage) ],
            peer => 'sp2',
        },
        sp2 => {
            peer => 'sp3',
        },
        sp3 => {
            peer => 'sp1',
        },
    },
};

my $cfg_carrier = {
    general => {
        ngcp_type => 'carrier',
    },
    intercept => {
        enable => 'no',
    },
    cluster_sets => {
        type => 'central',
    },
    hosts => {
        prx01a => {
            role => [ qw(li proxy) ],
            peer => 'prx01b',
            dbnode => 'db01',
        },
        web01a => {
            role => [ qw(mgmt) ],
        },
        web01b => {
            role => [ qw(mgmt) ],
        },
        web01c => {
            role => [ qw(mgmt) ],
        },

    },
};


my $obj_ce = NGCP::Template::Object->new($cfg_ce);
my $obj_pro = NGCP::Template::Object->new($cfg_pro);
my $obj_carrier = NGCP::Template::Object->new($cfg_carrier);

# Check get_online_cpus().
{
    my $cwd = getcwd();
    local $ENV{PATH} = "$cwd/mock-bin:$ENV{PATH}";

    is($obj_ce->get_online_cpus(), 8, 'number of online processors');
}

# Check has_role().
ok(!$obj_ce->has_role('non-existent', 'storage'),
    'host unknown has storage role');
ok($obj_ce->has_role('self', '.*'), 'host self has wildcard role');
ok($obj_ce->has_role('self', 'db'), 'host self has db role');
ok($obj_ce->has_role('self', 'lb'), 'host self has lb role');
ok($obj_ce->has_role('self', 'proxy'), 'host self has proxy role');
ok($obj_ce->has_role('self', 'rtp'), 'host self has rtp role');
ok(!$obj_ce->has_role('self', 'storage'), 'has self does not have storage role');

ok($obj_pro->has_role('sp1', 'storage'), 'host sp1 has storage role');

ok(!$obj_carrier->has_role('prx01a', 'li'), 'host prx01a does not have li role');
ok(!$obj_carrier->has_role('prx01a', 'li_dist'),
    'host prx01a does not have li_dist virtual role');
{
    local $obj_carrier->{config}{intercept}{enable} = 'yes';
    ok($obj_carrier->has_role('prx01a', 'li'),
        'host prx01a has li role (with intercept enabled)');
    ok(!$obj_carrier->has_role('prx01a', 'li_dist'),
        'host prx01a does not have li_dist virtual roles (with intercept enabled)');

    local $obj_carrier->{config}{cluster_sets}{type} = 'distributed';
    ok($obj_carrier->has_role('prx01a', 'li'),
        'host prx01a has li role (with cluster_sets as distributed)');
    ok($obj_carrier->has_role('prx01a', 'li_dist'),
        'host prx01a has li_dist virtual role (with cluster_sets as distributed)');
}

# Check get_peername().
is($obj_ce->get_peername('self'), undef, 'host self has no peer');
is($obj_pro->get_peername('sp1'), 'sp2', 'host sp1 has sp2 as peer');
is($obj_carrier->get_peername('prx01a'), 'prx01b', 'host prx01a has prx01b as peer');

# Check get_sibnames().
is_deeply([ $obj_ce->get_sibnames('self') ], [ ], 'no siblings for self');

is_deeply([ $obj_pro->get_sibnames('sp1')] , [ qw(sp2 sp3) ], 'siblings for sp1');
is_deeply([ $obj_pro->get_sibnames('sp2') ], [ qw(sp1 sp3) ], 'siblings for sp2');
is_deeply([ $obj_pro->get_sibnames('sp3') ], [ qw(sp1 sp2) ], 'siblings for sp3');

is_deeply([ $obj_carrier->get_sibnames('web01a') ], [ qw(web01b web01c) ], 'siblings for web01a');
is_deeply([ $obj_carrier->get_sibnames('web01b') ], [ qw(web01a web01c) ], 'siblings for web01b');
is_deeply([ $obj_carrier->get_sibnames('web01c') ], [ qw(web01a web01b) ], 'siblings for web01c');

# Check get_firstname().
is($obj_ce->get_firstname('non-existent'), 'self',
    'host unknown has self as first name');
is($obj_ce->get_firstname('self'), 'self', 'host self has self as first name');
is($obj_pro->get_firstname('sp1'), 'sp1', 'host sp1 has sp1 as first name');
is($obj_pro->get_firstname('sp2'), 'sp1', 'host sp2 has sp1 as first name');
is($obj_pro->get_firstname('sp3'), 'sp1', 'host sp3 has sp1 as first name');

# Check get_pairname().
is($obj_ce->get_pairname('self'), 'spce', 'host self has sp as pairname');
is($obj_pro->get_pairname('sp1'), 'sp', 'host sp1 has sp as pairname');
is($obj_pro->get_pairname('sp2'), 'sp', 'host sp2 has sp as pairname');
is($obj_pro->get_pairname('sp9'), 'sp', 'host sp9 has sp as pairname');
is($obj_carrier->get_pairname('web01a'), 'web01',
    'host web01a has web01 as pairname');
is($obj_carrier->get_pairname('web01b'), 'web01',
    'host web01b has web01 as pairname');
is($obj_carrier->get_pairname('web01i'), 'web01',
    'host web01i has web01 as pairname');

# Check get_mgmt_pairname().
is($obj_ce->get_mgmt_pairname(), 'sp', 'spce has sp as mgmt pairname');
is($obj_pro->get_mgmt_pairname(), 'sp', 'sppro has sp as mgmt pairname');
is($obj_carrier->get_mgmt_pairname(), 'web01', 'carrier has web01 as mgmt pairname');

# Check get_dbnode().
is($obj_ce->get_dbnode('non-existent'), 'self', 'host unknown has self as dbnode');
is($obj_carrier->get_dbnode('prx01a'), 'db01', 'host prx01a has db01 as dbnode');

# Check net_ip_expand().
is($obj_ce->net_ip_expand('1:2::5:20'),
    '1:2:0:0:0:0:5:20',
    'normalize IPv6 1:2::5:20');
is($obj_ce->net_ip_expand('001:2::0005:020'),
    '001:2:0:0:0:0:0005:020',
    'normalize IPv6 001::0005:020');
is($obj_ce->net_ip_expand('1::0'),
    '1:0:0:0:0:0:0:0',
    'normalize IPv6 1::0');

## instances
delete $cfg_pro->{hosts}{sp3};
$cfg_pro->{hosts}{sp2}{peer} = 'sp1';
$cfg_pro->{hosts}{sp1}{interfaces} = [ qw(eth0 eth1) ];
$cfg_pro->{hosts}{sp1}{eth0} = {
    ip => '172.16.7.1',
    netmask => '255.255.255.0',
    type => [ qw(ha_int sip_int) ],
};
$cfg_pro->{hosts}{sp1}{eth1} = {
    cluster_set => [ 'default' ],
    ip => '172.16.8.1',
    netmask => '255.255.255.224',
    type => [ 'sip_ext' ],
};
$cfg_pro->{hosts}{sp2}{interfaces} = [ qw(eth0 eth1) ];
$cfg_pro->{hosts}{sp2}{eth0} = {
    ip => '172.16.7.2',
    netmask => '255.255.255.0',
    type => [ qw(ha_int sip_int) ],
};
$cfg_pro->{hosts}{sp2}{eth1} = {
    cluster_set => [ 'default' ],
    ip => '172.16.8.2',
    netmask => '255.255.255.224',
    type => [ 'sip_ext' ],
};

my $iface_A = [
    {name => 'eth0', ip => '172.16.7.4', type => 'sip_int'},
    {name => 'eth1', ip => '172.16.8.4', type => 'sip_ext'},
];
my $iface_B = [
    {name => 'eth0', ip => '172.16.7.6', type => 'sip_int'},
    {name => 'eth1', ip => '172.16.8.6', type => 'sip_ext'},
];
$cfg_pro->{instances} = [
    {name => 'A', host => 'sp2', interfaces => $iface_A},
    {name => 'B', host => 'sp3', interfaces => $iface_B},
];
$obj_pro = NGCP::Template::Object->new($cfg_pro);

# Check get_instances(hostname).
my $instances = [
    {
        name      => 'A',
        host      => 'sp2',
        interfaces => [
            {
                name    => 'eth0',
                ip      => '172.16.7.4',
                type    => 'sip_int',
                netmask => '255.255.255.0'
            },
            {
                name        => 'eth1',
                ip          => '172.16.8.4',
                type        => 'sip_ext',
                netmask     => '255.255.255.224',
                cluster_set => ['default']
            },
        ]
    },
];
is_deeply($obj_pro->get_instances('sp1'), $instances,
    'host sp1 has one instances defined');
is_deeply($obj_pro->get_instances('sp2'), $instances,
    'host sp2 has one instances defined');
