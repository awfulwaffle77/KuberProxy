from flask import Flask, make_response
import argparse

"""
    The downstream server file, one of the hosts of a service. This will
    get the requests from the proxy and will send them back.
"""
app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--host", help="The host IP address")
parser.add_argument("-p", "--port", help="The host port")
args = parser.parse_args()

# if the host argument is not provided, then default with 0.0.0.0
if args.host == None:  
    args.host = "0.0.0.0"


@app.route("/")
def response_example():
    # sample response
    response = make_response(f'Hello from {args.port}')
    # Host header set for the response https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/host
    response.headers['Host'] = str(args.host) + ":" + str(args.port)
    return response


if __name__ == "__main__":
    app.run(host=args.host, port=args.port, debug=True)