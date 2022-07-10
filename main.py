import reverse_proxy
from flask import Flask

app = Flask(__name__)

rp = reverse_proxy.ReverseProxy()

@app.route("/")
def get():
    return rp.get_request(algorithm=rp._round_robin).text

if __name__ == "__main__":
    app.run(host=rp.socket_address.address, port = rp.socket_address.port, debug=True)
    