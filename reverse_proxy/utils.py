"""
    Structures that make our work easier.
"""


class SocketAddress:
    """
        Used to store IP and port
        Name chosen as per https://en.m.wikipedia.org/wiki/Network_socket#Socket_addresses
    """
    def __init__(self, yaml_struct) -> None:
        self.address = yaml_struct['address']
        self.port = yaml_struct['port']
    

    def __str__(self):
        """
            This function overrides the str function over this class
            so that we may easily use it when needed to transform the 
            class into a dict key.
        """
        return (str(self.address) + str(self.port))


class Service:
    def __init__(self, yaml_struct) -> None:
        """
            Creates a structure from yaml_struct['proxy']['service'],
            containing a name, a domain and a list of hosts as SocketAddress
        """
        self.name = yaml_struct['name']
        self.domain = yaml_struct['domain']
        
        self.hosts = []
        for host in yaml_struct['hosts']:
            self.hosts.append(SocketAddress(host))
    

    def __str__(self):
        """
            This function overrides the str function over this class
            so that we may easily use it when needed to transform the 
            class into a dict key.
        """
        return (str(self.name) + str(self.domain))