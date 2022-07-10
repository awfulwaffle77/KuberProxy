FROM python:3.9.7
RUN mkdir /app
WORKDIR /app

COPY . /app/
# Currently not working as it throws error
# "No module named reverse_proxy"

#COPY requirements.txt /app
#COPY proxy.py /app
#COPY config.yaml /app
#ADD reverse_proxy /app/

RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "proxy.py" ]
