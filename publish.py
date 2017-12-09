#!/usr/bin/env python
import pika, sys, datetime, time

credentials = pika.PlainCredentials('sisdis','sisdis')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
channel = connection.channel()

message = '{"action":"ping","npm":"1406543725","ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
while 1:
    channel.basic_publish(exchange='EX_PING', routing_key='', body=message)
    time.sleep(5)

connection.close()
