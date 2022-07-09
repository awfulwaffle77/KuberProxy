import yaml
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
    
    def test(self):
        return "hello world"