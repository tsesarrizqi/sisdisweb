#!/usr/bin/env python
import pika, sys, json, os, django, datetime

credentials = pika.PlainCredentials('sisdis','sisdis')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
channel = connection.channel()

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='EX_PING', queue=queue_name)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sisdisweb.settings")
django.setup()
from sisdis1.models import Ping

def callback(ch, method, properties, body):
    try:
        body_dict = json.loads(body.decode())
        action = body_dict['action']
        if str(action) == 'ping':
            npm = body_dict['npm']
            ts = body_dict['ts']
            ping1 = Ping(npm = npm, date = ts)
            ping1.save()
            old_treshold = datetime.datetime.now() - datetime.timedelta(seconds = 15)
            old_msg = Ping.objects.filter(date__lte = old_treshold)
            old_msg.delete()
    except:
        pass

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
