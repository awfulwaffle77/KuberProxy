FROM python:3.9.7
RUN mkdir /app
WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "proxy.py" ]
