"""
    Structures that make our work easier.
"""

import yaml


class SocketAddress:
    """
        As per the link at https://en.m.wikipedia.org/wiki/Network_socket#Socket_addresses
        I have decided to name the combination of IP Address + Port Socket Address
    """
    def __init__(self, yaml_struct) -> None:
        self.address = yaml_struct['address']
        self.port = yaml_struct['port']

class Service:
    def __init__(self, yaml_struct) -> None:
        """
            The cleanest implementation would be if the Service class
            takes care of creating its members based on a
            yaml_struct['proxy']['service']
        """
        self.name = yaml_struct['name']
        self.domain = yaml_struct['domain']
        
        self.hosts = []
        for host in yaml_struct['hosts']:
            self.hosts.append(SocketAddress(host))
        print(" ")