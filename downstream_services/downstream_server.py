from flask import Flask, make_response
import argparse

from yaml import parse

"""
    The downstream server file, one of the hosts of a service. This will
    get the requests from the proxy and will send them back.
"""
app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--host", help="The host IP address")
parser.add_argument("-p", "--port", help="The host port")
args = parser.parse_args()

# if the host argument is not provided, then default with localhost
if args.host == None:  
    args.host = "127.0.0.1"

@app.route("/")
def response_example():
    # sample response
    response = make_response(f'Hello from {args.port}')
    response.headers['Host'] = str(args.host) + ":" + str(args.port)
    return response

if __name__ == "__main__":
        app.run(host=args.host, port=args.port, debug=True)