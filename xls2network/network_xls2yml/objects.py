#!/usr/bin/env python3

import re
import itertools


def unique_ids_generator():
    """A generator for unique IDs.
    A unique ID is an integer returned as string data type.
    This is used for dbnode, for example.
    """
    for i in itertools.count(1):
        yield str(i)


GLOBAL_UID_GEN = unique_ids_generator()


class VirtualLAN:
    """
    Mutable abstraction of a virtual LAN network.
    It stores data about the network such as an ID and
    a reference to the gateway.
    """

    def __init__(self, name, _id):
        self.name = name
        self.id = _id
        self.gateway = None

    def __repr__(self):
        msg = 'VirtualLAN(name={} id={} gateway={})'
        return msg.format(self.name, self.id, self.gateway)

    def __str__(self):
        return 'vlan{}'.format(self.id)


class NetworkConnection:
    """
    Mutable abstraction of a network connection.
    It stores data about the connection such as the IP address in use.
    It potentially normalizes and validates settings when they are set.
    """

    def __init__(self, ip_addr, subnetmask, vlan, phy):
        self.ip_addr = ip_addr
        self.subnetmask = subnetmask
        self.vlan = vlan
        self.phy = phy

    def __str__(self):
        msg = 'Connection({} ⇔ {})'
        return msg.format(self.phy or self.ip_addr, str(self.vlan))

    def __repr__(self):
        msg = 'NetworkConnection(ip_addr={} subnetmask={} vlan={} phy={})'
        return msg.format(self.ip_addr, self.subnetmask, self.vlan, self.phy)

    @property
    def subnetmask(self):
        return self._subnetmask

    @subnetmask.setter
    def subnetmask(self, snm):
        snms = str(snm)
        # regular expression to match subnet masks such as '255.255.255.240'
        m = re.match(r'(\d{1,3})\.' * 3 + '(\d{1,3})$', snms)
        if m:
            self._subnetmask = snms
        else:
            errmsg = "Subnet mask '{}' has invalid format"
            parts = []
            while snms:
                e = min(len(snms), 3)
                try:
                    int(snms[0:e])
                except ValueError:
                    raise ValueError(errmsg.format(snm))
                parts.append(snms[0:e])
                snms = snms[e:]
            if len(parts) != 4:
                raise ValueError(errmsg.format(snm))
            self._subnetmask = '.'.join(parts)

    @property
    def network_type(self):
        # TODO: verify whether phy signifies 'lo'
        if self.phy == 'lo':
            return ['ssh_ext', 'api_int']
        return []


class Host:
    """
    Mutable abstraction of a host in a network.
    It stores the hostname and networks, the host is attached to.
    """

    def __init__(self, hostname):
        self.hostname = hostname
        self.nets = []
        self._dbnode = None

        assert bool(self.hostname), 'Hostname must not be empty'

    def __repr__(self):
        nets = [str(net) for net in self.nets]
        return 'Host(hostname={}, nets={})'.format(self.hostname, nets)

    def add_net(self, net):
        """Attach a network connection to this host

        :param net:    the network to attach
        :type net:     NetworkConnection
        """
        self.nets.append(net)

    @property
    def peer(self):
        m = re.match(r'(\w{1,5}\d{1,2})([ab])$', self.hostname)
        if m:
            return m.group(1) + (m.group(2) == 'a' and 'b' or 'a')
        return ''

    @property
    def roles(self):
        rs = []
        if self.hostname.startswith('db'):
            rs.append('db')
        return rs

    @property
    def dbnode(self):
        if not self._dbnode:
            self._dbnode = next(GLOBAL_UID_GEN)
        return self._dbnode

    def __str__(self):
        return self.hostname

    def yaml(self):
        """Returns the python data structure representing this host.
        The python data structure can be easily passed to the `PyYAML`
        module to represent this host in YAML.
        """
        struct = {
            'lo': {
              'advertised_ip': [],
              'hwaddr': '00:00:00:00:00:00',
              'ip': '127.0.0.1',
              'netmask': '255.0.0.0',
              'shared_ip': [],
              'shared_v6ip': [],
              'type': ['ssh_ext', 'api_int'],
              'v6ip': '::1'
            },
            'interfaces': ['lo'] + [str(net.vlan) for net in self.nets],
        }

        if self.peer:
            struct['peer'] = self.peer

        struct['dbnode'] = self.dbnode

        bonds = [net.phy for net in self.nets
                 if net.phy and re.match(r'bond\d+$', net.phy)]
        for bond in bonds:
            struct[bond] = {
              'bond_miimon': '100',
              'bond_mode': 'active-backup',
              'bond_slaves': 'eth0 eth1',
            }

        roles = self.roles
        if len(roles) > 0:
            struct['role'] = self.roles

        for net in self.nets:
            struct[str(net.vlan)] = {
                'ip': net.ip_addr,
                'netmask': net.subnetmask,
                'type': [net.vlan.name],
                'vlan_raw_device': net.phy
            }
            if net.vlan.gateway:
                assert len(net.vlan.gateway.nets) == 1
                ip_addr = net.vlan.gateway.nets[0].ip_addr
                struct[str(net.vlan)]['gateway'] = ip_addr

        return struct
