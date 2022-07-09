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

### Reminders

Reading the document I can see that it is stated that " downstream 
services are identified using the Host Http header". I am not sure 
why this would be needed but I will make the responses contain
this header.