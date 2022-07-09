from flask import Flask
import argparse

from yaml import parse

"""
    The host server file. This will get the requests from the proxy
    and will send them back.
"""
app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--host", help="The host IP address")
parser.add_argument("-p", "--port", help="The host port")
args = parser.parse_args()

@app.route("/")
def func():
    return f'Hello from {args.port}'

if __name__ == "__main__":
        app.run(host=args.host, port=args.port, debug=True)