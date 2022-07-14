# KubeProxy

## How to run locally

1. Set the IP address as you need them in `config.yaml`.  All addresses
being set to `0.0.0.0` but with different ports are working correctly.

2. Run `python proxy.py` in a terminal window and 
`python downstream_services/downstream_server.py -p <port>` in separate
terminal windows according to the `config.yaml` file.

3. `curl 127.0.0.1:8081/basic`

## Implementation

The implementation has been done in Python as it helped with the
speed of the implementation. All the implementation has tried
to respect PEP8 as closely as possible. I have also tried to
keep things as tidy as possible and have created `reverse_proxy`
as a python package.

The architecture was thought to be as basic as possible so that it
may be quickest to implement, while still showing the software
engineering skills needed.

![architecture](https://i.imgur.com/ZMvAd0P.jpg)

First of all, we needed to choose a web server to be used both on the 
proxy and the clients. I was pondering between a basic http 
server and Flask, but as the [Python docs about http.server](https://docs.python.org/3/library/http.server.html)
states that it is *not recommended in production* I will go ahead and use
Flask (also, I have more experience with Flask and it should be quicker
to implement).

Even though ultimately I have realised that the proper way may be
to address services by domain, this implementation addresses services
directly by their hosts and thus uses their IPs and ports to communicate.

Having the server working, to be able to send requests to specific 
hosts, we need to create them. We will do this by "simulating" the
existence of such hosts. To do so, we are using 
`downstream_services/downstream_server.py`  which can be ran with
`python downstream_server.py -t <hostIP> -p <port>`.

Having tested with the host servers in separate terminal 
windows, it works correctly.

![all_working](https://i.imgur.com/4OmijLA.png)

We can also see that caching works correctly as the proxy gets requests and directly
addresses them and does not forward them to hosts.

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

```
docker image tag reverse_proxy:0.1.0 morphinn/reverse_proxy:0.1.0
docker image tag downstream_server:0.1.0 morphinn/downstream_server:0.1.0
```

```
docker push morphinn/reverse_proxy:0.1.0
docker push morphinn/downstream_server:0.1.0
```

We use helm to install our chart:

`helm.exe install kuber-reverse-proxy helm_chart/reverse_proxy_helm`

Under `deployment.yaml: line 38`, I had to change port to 8081 as this
is the port that the app listens on and without it liveness probes and
readiness probes cannot understand the state of our pod(s) running the app.

I can see that the app is running using `kubectl logs <pod-name>`.

Using `minikube service kuber-reverse-proxy` I can open
the app in my browser. I can see that message 
`* service default/kuber-reverse-proxy has no node port` is
shown. Setting a node port should allow me to connect
to the app without using the minikube command, but this
may also be a caveat of using Windows and minikube.

![minikube_service](https://i.imgur.com/HDzKyXs.png)

Checking the [documentation](https://minikube.sigs.k8s.io/docs/handbook/accessing/), 
I can see that it is stated that `The network is limited if using 
the Docker driver on Darwin, Windows, or WSL, and the Node IP is not reachable 
directly` so my assumption seems to be true.

To be able to better (and quicker) reproduce the environment, 
I have manually created the downstream servers as deployment.

To be able to use the downstream servers' IPs in cofig.yaml
(in a quick & dirt manner), 
I have created 2 deployments (with `downstream_services/downstream[12].yaml`).
I am getting their IP addresses and I hardcode them in my config file
and then I run `helm upgrade` to rerun the reverse proxy.
Although hacky, it is working and is proving that the reverse-proxy
application works properly. The hacky implementation is on the side
of the downstream services, which are not the point of this
assignment. The documentation that made it possible for me to
think about this approach is [here](https://dev.to/narasimha1997/communication-between-microservices-in-a-kubernetes-cluster-1n41).


The application works properly in this environment.

![kuber_working](https://i.imgur.com/fAkUHPP.png)

## Monitoring

As other people with more experience in this field are surely 
to know more about SLO/SLI than me, I did some research and found 
out that one of the best approach would be using 
[The Four Golden Signlas](https://sre.google/sre-book/monitoring-distributed-systems/#xref_monitoring_golden-signals)
as they focus on key aspects related to our service.

- Latency: because we need to know how quick (or slow) requests are resolved 
- Traffic: measured probably in HTTP requests/sec in our case; useful
because this may show a reason of why latency increases in a specific
time windows for example
- Errors: always a good metric to see if something is going wrong, but may
be tricky to catch in specific cases (e.g. when the application responds with a code 200,
but with wrong content)
- Saturation: the overall capacity of the service, because most systems begin to degrade before utilization hits 100%

Also checked how to properly implement SLIs and SLOs 
[here](https://docs.bitnami.com/tutorials/implementing-slos-using-prometheus), but
due to lack of time I was not able to implement them.

I have used helm to install Prometheus, by following the
[Prometheus repo](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus)
and [Grafana repo](https://github.com/grafana/helm-charts).

Checking with `minikube service poremetheus-test-prometheus-server`, 
I could observe that Prometheus works and Grafana too.

## Feedback

### Implementation 

- The reverse proxy does not take into account the Host header to redirect the queries - "The reverse proxy should support multiple downstream services with multiple instances, downstream services are identified using the Host Http header."
- It only supports GET requests, forwarded to hardcoded service paths - this should either be configurable or pass all client requests
- Both random (default behavior) and round-robin take all services into account without any regards for the target service, which means that even if target A is requested it could be that a response is forwarded from service B (this is again caused by not using the Host header)
- If one service instance is down and if the request hasn’t already been cached, the whole reverse proxy is stuck serving the failing request for all clients. Correct error handling would have prevented such an issue, had the proxy analysed the origin responses before caching & forwarding them
- The in-memory cache extension is poorly implemented - the caching key would clash in reality, since the URLs are not parsed correctly. Moreover, the caching doesn’t obey any of the HTTP 1.1. protocol’s caching rules, described in https://datatracker.ietf.org/doc/html/rfc7234
- The proxy’s configuration is properly loaded, but not validated.
- No unit tests.
  
### Automation

- Helm chart OK.
- Liveness and Readiness probes should have been configured on a dedicated path.

### Monitoring

- Did not have much experience on the topic but tried to search for information and came up with basic definitions of what could be relevant SLIs
- Did not implement any SLIs but did come up with Prometheus/Grafana deployed using Helm charts. He also delivered an HPA configuration but did not mention it in the docs