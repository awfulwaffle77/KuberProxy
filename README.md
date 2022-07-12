# KubeProxy

## How to run locally

1. Set the IP address as you need them in `config.yaml`.  All addresses
being set to `0.0.0.0` but with different ports work correctly.

2. Run `python proxy.py` in a terminal window and 
`python downstream_services/downstream_server.py -p <port>` in separate
terminal windows according to the `config.yaml` file.

3. `curl 127.0.0.1:8081` and requests should be working properly.

## Implementation

The implementation has been done in Python as it helped with the
speed of the implementation. All the implementaion has tried
to respect PEP8 as close as possible. I have also tried to
keep things as tidy as possible and have created `reverse_proxy`
as a python package.

The architecture was thought to be as basic as possible so that it
may be quickest to implement, while still showing the software
engineering skills needed.

![architecture](https://i.imgur.com/ZMvAd0P.jpg)

First of all, we needed to choose a web server to be used both on the 
proxy and the clients. I was pondering between a basic http 
server and Flask, but as the [Python docs about http.server](https://docs.python.org/3/library/http.server.html)
states that it is *not reccomended in production* I will go ahead and use
Flask (also, I have more experience with Flask and it should be quicker
to implement).

Even though ultimately I have realised that the proper way may be
to address services by domain, this implementation addresses services
directly by their hosts an thus uses their IPs an ports to communicate.

Having the server working, to be able to send requests to specific 
hosts, we need to create them. We will do this by "simulating" the
existence of such hosts. To do so, we are using 
`downstream_services/downstream_server.py`  which can be ran with
`python downstream_server.py -t <hostIP> -p <port>`.

Having tested with the host servers in separate terminal 
windows, it works correctly.

![all_working](https://i.imgur.com/4OmijLA.png)

We can also see that caching works correctly as the proxy gets requests and directly
addresses them and do not forward them to hosts.

## Automation

To be able to use the application(s) in a Kubernetes cluster, I
first had to create images of both `proxy.py` and `downstream_server.py`.

Built the reverse proxy image:

`docker build -t reverse_proxy:0.1.0 .`

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

`helm.exe install kuber-reverse-proxy helm_chart/reverse_proxy_helm`

Under `deployment.yaml: line 38` - had to change port to 8081 as this
is the port that the app listens on and without it liveness probes and
readiness probes cannot understand the state of our pods running the app.

I can see that the app runs using `kubectl logs <pod-name>`.

Using `minikube service kuber-reverse-proxy` I can open
the app in my browser. I can see that message 
`* service default/kuber-reverse-proxy has no node port` is
shown. Setting a node port should allow me to connect
to the app without using the minikube command, but this
may also be caveat of using Windows and minikube.

![minikube_service](https://i.imgur.com/HDzKyXs.png)

Checking the [documentation](https://minikube.sigs.k8s.io/docs/handbook/accessing/), 
I can see that it is stated that `The network is limited if using 
the Docker driver on Darwin, Windows, or WSL, and the Node IP is not reachable 
directly` so my assumption was true.

To be able to better (and quicker) reproduce the environment, 
I have created manually the downstream servers as deploymnet.

To be able to use the downstream severs' IPs in cofig.yaml
(in a quick & dirt manner), 
I have created 2 deployments (with `downstream_services/downstream[12].yaml`).
I am getting their IP addresses and I hardcode them in my config file
and then I run `helm upgrade` to rerun the reverse proxy.
Altough hacky, it is working and is proving that the reverse-proxy
application works properly. The hacky implementation is on the side
of the downstream services, which are not the point of this
assignment. The documentation that made it possible for me to
think about this approach is [here](https://dev.to/narasimha1997/communication-between-microservices-in-a-kubernetes-cluster-1n41).


The application work properly in this environment.

![kuber_working](https://i.imgur.com/fAkUHPP.png)

## Monitoring

As other people with more experience in this field are surely 
to know more about SLO/SLI than me, I did some reasearch and found 
[this article](https://www.squadcast.com/blog/using-observability-tools-to-set-slos-for-kubernetes-applications)
which proved to be very helpful. 

I have used helm to install Prometheus, by following the
[repo](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus)
and [Grafana](https://github.com/grafana/helm-charts).

Following [this](https://blog.marcnuri.com/prometheus-grafana-setup-minikube)
guide and trying to expose the prometheus server with command
`kubectl expose service prometheus-server --type=NodePort --target-port=9090 --name=prometheus-server-np`
did not work for me, but I have used 
`minikube service poremetheus-test-prometheus-server` and it properly worked.

Checked how to properly implement SLIs and SLOs 
[here](https://docs.bitnami.com/tutorials/implementing-slos-using-prometheus), but
due to lack of time I was not able to implement them.


