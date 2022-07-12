import reverse_proxy
from flask import Flask

app = Flask(__name__)

rp = reverse_proxy.ReverseProxy()


@app.route("/")
def sanity_check():
    """
        Acts as a sanity/health check for the server
    """
    return ""


@app.route("/basic")
def get():
    """
        Returns a basic response from the downstream
        servers.
    """
    try:
        return rp.get_request(algorithm=rp._round_robin).text
    except:
        return "Unable to establish connection."


if __name__ == "__main__":
    app.run(host=rp.socket_address.address, port = rp.socket_address.port, debug=True)
    