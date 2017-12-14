#!/usr/bin/env python
# consume_transfer
import pika, sys, json, os, django, datetime, time

credentials = pika.PlainCredentials('sisdis','sisdis')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
channel = connection.channel()

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='EX_TRANSFER', queue=queue_name, routing_key='REQ_1406543725')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sisdisweb.settings")
django.setup()
from sisdis1.models import Ping, Nasabah

def quorum_terpenuhi():
    old_treshold = datetime.datetime.now() - datetime.timedelta(seconds = 10)
    npms = Ping.objects.filter(date__gte = old_treshold).values('npm').distinct()
#    return len(npms) >= len(Ping.objects.all())/2
    return 1

def publish_resp(sender_id,status_transfer):
    credentials = pika.PlainCredentials('sisdis','sisdis')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
    channel = connection.channel()

    message = '{"action":"transfer","type":"response","status_transfer":'+str(status_transfer)+',"ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
    channel.basic_publish(exchange='EX_TRANSFER', routing_key='RESP_'+str(sender_id), body=message)
    
    connection.close()


def callback(ch, method, properties, body):
    print('masuk1')
    try:
        body_dict = json.loads(body.decode())
        action = body_dict['action']
        tipe = body_dict['type']
        if str(action) == 'transfer' and str(tipe) == 'request':
            user_id = str(body_dict['user_id'])
            sender_id = body_dict['sender_id']
            nilai = int(body_dict['nilai'])
            ts = body_dict['ts']
            try:
                status_transfer = -99
                if int(nilai) < 0 or int(nilai) > 1000000000:
                    status_transfer = -5
                    publish_resp(sender_id, status_transfer)
                    return
                nasabah = Nasabah.objects.filter(user_id = user_id)
                if len(nasabah) == 1:
                    if quorum_terpenuhi():
                        try:
                            print(nasabah[0].user_id,' ',user_id, ' ', nilai, ' ', nasabah[0].saldo)
                            nasabah[0].saldo = nasabah[0].saldo + int(nilai)
                            nasabah[0].save()
                            print(nasabah[0].saldo)
                            print('masuk2')
                            status_transfer = 1
                            publish_resp(sender_id, status_transfer)
                            return
                        except:
                            status_transfer = -4
                            publish_resp(sender_id, status_transfer)
                            return
                    else:
                        status_transfer = -2
                else:
                    status_transfer = -1
                publish_resp(sender_id, status_transfer)
                return
            except:
                resp = {}
                status_transfer = -99
                publish_resp(sender_id, status_transfer)
                return
    except:
        pass

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
