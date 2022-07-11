# KubeProxy

*The Reverse Proxy implementation you never knew you needed.*

## Implementation

The implementation will be done in Python as it should help with the
speed of the implementation (also I am the most confident in Python
skills).

First of all, we need to choose a web server to be used both on the 
proxy and the clients. I was pondering between a basic http 
server and Flask, but as the [Python docs about http.server](https://docs.python.org/3/library/http.server.html)
states that it is *not reccomended in production* I will go ahead and use
Flask (also, I have more experience with Flask and it should be quicker
to implement).

Flask was not working properly inside my ReverseProxy class, so I
checked how to achieve this. I found [this Stackoverflow link](https://stackoverflow.com/questions/40460846/using-flask-inside-class)
that states that such approach would not be compliant with Flask's
style guide. If this is the case, I will change my approach.

Altough not exactly what I wanted, the current approach works.

Now that the server is working, to be able to send requests to specific 
hosts, we need to create them. We will do this by "simulating" the
existence of such hosts. From the main file, we will create Flask
applications with specifci arguments to make that possible. We
will create subprocesses to make this possible

I tried to respect PEP88.

Currently tested with the host servers in separate terminal windows
and it works correctly. Next, I will need to tweak the responses
and the algortihms.

I tried to kept thing tidy and I have put the reverse_proxy.py 
file and the util in a separate directory, making it act like
a package. I have followed the instructions at 
[this stackoverflow link](https://stackoverflow.com/questions/35727134/module-imports-and-init-py)
to achieve it.

`TODO: Add some screenshots`

`TODO: Add some proper exception mechanisms at flask get request`

As I have not played with Helm before, I will try and create a Kuberenetes deployment first. 

## Docker

Created the Dockerfile and then build it and ran it. (The kubernetes
folder should not be in this image)

Built the image:

`docker build -t reverse_proxy:0.1.0 .`

Created a new network:

`docker network create --subnet=172.18.0.0/16 proxy_network`

Ran a container:

`docker run -d -p 5000:8081 reverse_proxy:0.1.0`

Using `docker inspect <container_id>`, I can see
the following:
```
 "Ports": {
                "8081/tcp": [
                    {
                        "HostIp": "0.0.0.0",
                        "HostPort": "5000"
                    }
                ]
            },
```
This means that I should be able to access it through
`curl 127.0.0.1:5000`, which I am able to.

We also need to create an image of the application
that will run on the downstream servers.

`docker build -t downstream_server:0.1.0 .`

We then retag and push the images to docker hub:

`docker image tag reverse_proxy:0.1.0 morphinn/reverse_proxy:0.1.0`
`docker image tag downstream_server:0.1.0 morphinn/downstream_server:0.1.0`

`docker push morphinn/reverse_proxy:0.1.0`
`docker push morphinn/downstream_server:0.1.0`

We use helm to install our chart

`helm.exe install kuber-reverse-proxy ../helm_chart/reverse_proxy_helm`

`deployment.yaml: line 38` - had to change port to 5000

Tried to delete services using 
`kubectl delete services kuber-reverse-proxy -n default`, but helm
showed `Error: INSTALLATION FAILED: cannot re-use a name that is still in use`
when trying `helm install`; mitigated this with `helm upgrade`.

As the application is running on port 8081, I have to set the liveness
and readiness probes to check that port so that the pods can run correctly.

I can see that the app runs using `kubectl logs <pod-name>`.

Using `minikube service kuber-reverse-proxy` I can open
the app in my browser. I can see that message 
`* service default/kuber-reverse-proxy has no node port` is
shown. Setting a node port should allow me to connect
to the app without using the minikube command, but this
may also be caveat of using Windows and minikube.

Checking the [documentation](https://minikube.sigs.k8s.io/docs/handbook/accessing/), 
I can see that it is stated that `The network is limited if using 
the Docker driver on Darwin, Windows, or WSL, and the Node IP is not reachable directly.` so my assumption was true.

Using `helm template <path_to_chart>` we can see the templates 
with values changes as per the `values.yaml` file.

To be able to better (and quicker) reproduce the environment, 
I have created manually the downstream servers as deploymnet.

`kubectl create -f downstream-jobx.yaml` where x is the number of
the deployment.

To be able to use the downstream severs' IPs in cofig.yaml, 
I have created 2 deployments (with `downstream_services/downstream[12].yaml`).
I am getting their IP addresses and I hardcode them in my config file
and then I run `helm upgrade` to rerun the reverse proxy.
Altough hacky, it is working and is proving that the reverse-proxy
application works properly. The hacky implementation is on the side
of the downstream services, which are not the point of this
assignment. The documentation that made it possible for me to
think about this approach is [here](https://dev.to/narasimha1997/communication-between-microservices-in-a-kubernetes-cluster-1n41).

### Reminders

Reading the document I can see that it is stated that " downstream 
services are identified using the Host Http header". The responses contain
this header. 

-> JSON POST requests are not tested, but should also work properly

