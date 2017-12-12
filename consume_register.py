#!/usr/bin/env python
# consume_register
import pika, sys, json, os, django, datetime, time

credentials = pika.PlainCredentials('sisdis','sisdis')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
channel = connection.channel()

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='EX_REGISTER', queue=queue_name, routing_key='REQ_1406543725')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sisdisweb.settings")
django.setup()
from sisdis1.models import Ping, Nasabah

def quorum_terpenuhi():
    old_treshold = datetime.datetime.now() - datetime.timedelta(seconds = 10)
    npms = Ping.objects.filter(date__gte = old_treshold).values('npm').distinct()
    return len(npms) >= 5


def publish_resp(sender_id,status_register):
    credentials = pika.PlainCredentials('sisdis','sisdis')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
    channel = connection.channel()

    message = '{"action":"register","type":"response","status_register":'+str(status_register)+',"ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
    channel.basic_publish(exchange='EX_REGISTER', routing_key='RESP_'+str(sender_id), body=message)
    
    connection.close()


def callback(ch, method, properties, body):
    try:
        body_dict = json.loads(body.decode())
        action = body_dict['action']
        tipe = body_dict['type']
        if str(action) == 'register' and str(tipe) == 'request':
            try:
                user_id = str(body_dict['user_id'])
                name = str(body_dict['user_id'])
                sender_id = body_dict['sender_id']
                ts = body_dict['ts']
                nasabah0 = Nasabah.objects.filter(user_id = user_id)
                if len(nasabah0) == 0:
                    if quorum_terpenuhi():
                        nasabah = Nasabah(user_id = user_id, name = name, saldo = 0)
                        nasabah.save()
                        status_register = 1
                    else:
                        status_register = -2
                else:
                    status_register = -4
                publish_resp(sender_id, status_register)
                return
            except:
                resp = {}
                status_register = -4
                publish_resp(sender_id, status_register)
                return
        else:
            resp = {}
            status_register = -99
            publish_resp(sender_id, status_register)
            return
    except:
        pass

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()