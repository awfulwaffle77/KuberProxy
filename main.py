import reverse_proxy
from flask import Flask

app = Flask(__name__)

rp = reverse_proxy.ReverseProxy()

@app.route("/")
def route():
    return rp.route("test_request")

if __name__ == "__main__":
    app.run(host=rp.socket_address.address, port = rp.socket_address.port, debug=True)
    