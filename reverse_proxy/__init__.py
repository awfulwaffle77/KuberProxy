import yaml
import requests
import random
from reverse_proxy import utils


class ReverseProxy:
    def __init__(self, _config_filename = "config.yaml") -> None:
        """ 
            Initializes the members with the configurations from
            the config file.
        """
        with open(_config_filename) as config_filename:
            try:
                yaml_struct = yaml.safe_load(config_filename)

                self.services = []
                for service in yaml_struct['proxy']['services']:
                    self.services.append(utils.Service(service))

                self.socket_address = utils.SocketAddress(yaml_struct['proxy']['listen'])

                # empty dictionary that will act as a cache 
                self.__cache_dict = {}

                # these variables are used for round robin and must be kept in 
                # memory while the program is running so that we may know 
                # which other service/host to choose further
                self.service_idx = 0
                self.host_idx = 0

            except:
                print("Error processing YAML.")
    

    def __cache(self, service, host):
        """
            A function that acts accordingly before making a request,
            retrieving it from cache memory or making the request
            and adding it to cache memory if it doesn't exist there.
        """
        s = str(service) + str(host)  # the key in the dict
        if s in self.__cache_dict:
            return self.__cache_dict[s]
        else:
           url = "http://" + str(host.address) + ":" + str(host.port) + "/"
           r = requests.get(url)

           print("Caching..")
           self.__cache_dict[s] = r  # add to cache

           return r
        

    
    def get_request(self, algorithm=None):
        """
            Specifies how to route and where to route (to which
            downstream host)
        """
        if algorithm == None:
           rand_service = random.choice(self.services)
           rand_host = random.choice(rand_service.hosts)

           return self.__cache(rand_service, rand_host) 
        else:
            return algorithm()


    def _round_robin(self):
        """
            Round robin algorithm declared protected to be used with get_request() 
            function.
        """
        service = self.services[self.service_idx]   
        host = service.hosts[self.host_idx]
        
        r = self.__cache(service, host)

        self.host_idx = (self.host_idx + 1) % len(service.hosts)
        # if host_idx is at the last element
        if self.host_idx == 0:
            # increment service_idx
            self.service_idx = (self.service_idx + 1) % len(self.services)

        return r