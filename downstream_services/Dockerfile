FROM python:3.9.7
RUN mkdir /downstream_services
WORKDIR /downstream_services
COPY . /downstream_services
RUN pip install -r requirements.txt
# ENTRYPOINT [ "python" ]
# CMD [ "downstream_server.py" ]
