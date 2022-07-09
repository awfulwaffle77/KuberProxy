from transformers import RagModel
import yaml
import requests
import random
import subprocess
import utils

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

                self.run_server()

                print(" ")
            except:
                print("Error processing YAML.")
    
    
    def route(self, request, algorithm=None):
        """
            Specifies how to route and where to route (to which
            downstream host)
        """
        if algorithm == None:
           rand_service = random.choice(self.services)
           rand_host = random.choice(rand_service.hosts)
           url = "http://" + str(rand_host.address) + ":" + str(rand_host.port) + "/"
           r = requests.get(url)

           return r


    def run_backend_servers(self):
        """
        !!! THIS SHOULD NOT EXIST AT ALL !!!
            Runs the Flask application as subprocesses for the hosts under services.
        """
        for service in self.services:
            for host in service.host:
               subprocess.run(['python','host_server.py', '-t',host.address,'-p', host.port]) 

    def test(self):
        return "hello world"