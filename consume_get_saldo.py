#!/usr/bin/env python
# consume_get_saldo
import pika, sys, json, os, django, datetime, time

credentials = pika.PlainCredentials('sisdis','sisdis')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
channel = connection.channel()

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='EX_GET_SALDO', queue=queue_name, routing_key='REQ_1406543725')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sisdisweb.settings")
django.setup()
from sisdis1.models import Ping, Nasabah

def quorum_terpenuhi():
    old_treshold = datetime.datetime.now() - datetime.timedelta(seconds = 10)
    npms = Ping.objects.filter(date__gte = old_treshold).values('npm').distinct()
    return len(npms) >= 0


def publish_resp(sender_id,nilai_saldo):
    credentials = pika.PlainCredentials('sisdis','sisdis')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
    channel = connection.channel()

    message = '{"action":"get_saldo","type":"response","nilai_saldo":'+str(nilai_saldo)+',"ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
    channel.basic_publish(exchange='EX_GET_SALDO', routing_key='RESP_'+str(sender_id), body=message)
    
    connection.close()


def callback(ch, method, properties, body):
    try:
        body_dict = json.loads(body.decode())
        action = body_dict['action']
        tipe = body_dict['type']
        if str(action) == 'get_saldo' and str(tipe) == 'request':
            user_id = str(body_dict['user_id'])
            sender_id = body_dict['sender_id']
            ts = body_dict['ts']
            try:
                resp = {}
                nasabah = Nasabah.objects.filter(user_id = user_id)
                if len(nasabah) == 1:
                    if quorum_terpenuhi():
                        nilai_saldo = nasabah[0].saldo
                    else:
                        nilai_saldo = -2
                else:
                    nilai_saldo = -1
                publish_resp(sender_id,nilai_saldo)
                return
            except:
                resp = {}
                nilai_saldo = -4
                publish_resp(sender_id,nilai_saldo)
                return
        else:
            resp = {}
            nilai_saldo = -99
            publish_resp(sender_id,nilai_saldo)
            return
    except:
        pass

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
