#!/usr/bin/env python
# consume_get_total_saldo
import pika, sys, json, os, django, datetime, time

credentials = pika.PlainCredentials('sisdis','sisdis')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
channel = connection.channel()

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='EX_GET_TOTAL_SALDO', queue=queue_name, routing_key='REQ_1406543725')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sisdisweb.settings")
django.setup()
from sisdis1.models import Ping, Nasabah

def list_cabang():
    npm = ["1406543725"]
    resp_cabang = requests.get('http://152.118.31.2/list.php')
    body_cabang_unicode = resp_cabang.text
    body_cabang = json.loads(body_cabang_unicode)
    cabangs = []
    for cabang in body_cabang:
        if cabang['npm'] in npm:
            cabangs.append(cabang)
    return cabangs

def quorum_terpenuhi():
    old_treshold = datetime.datetime.now() - datetime.timedelta(seconds = 10)
    npms = Ping.objects.filter(date__gte = old_treshold).values('npm').distinct()
    return len(npms) >= 0


def publish_resp(sender_id,nilai_saldo):
    credentials = pika.PlainCredentials('sisdis','sisdis')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
    channel = connection.channel()

    message = '{"action":"get_total_saldo","type":"response","nilai_saldo":'+str(nilai_saldo)+',"ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
    channel.basic_publish(exchange='EX_GET_TOTAL_SALDO', routing_key='RESP_'+str(sender_id), body=message)
    
    connection.close()


def get_domisili(cabangs, user_id):
    for cabang in cabangs:
        if cabang['npm'] == user_id:
            return cabang['ip']
    return 0


def do_get_saldo(recv_id,user_id):
    credentials = pika.PlainCredentials('sisdis','sisdis')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
    channel1 = connection.channel()
    channel2 = connection.channel()
    
    result = channel2.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel2.queue_bind(exchange='EX_GET_SALDO', queue=queue_name, routing_key='RESP_1406543725')

    message = '{"action":"get_saldo","user_id":"'+str(user_id)+'","sender_id":"1406543725","type":"request","ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
    channel1.basic_publish(exchange='EX_GET_SALDO', routing_key='REQ_'+str(recv_id), body=message)
    
    while True:
        method_frame, header_frame, body = channel2.basic_get(queue=queue_name, no_ack=True)

        if not (method_frame == None):
            try:
                connection.close()
                body_dict = json.loads(body.decode())
                action = body_dict['action']
                tipe = body_dict['type']
                if str(action) == 'get_saldo' and str(tipe) == 'response':
                    nilai = int(body_dict['nilai_saldo'])
                    resp = {}
                    resp['nilai_saldo'] = nilai
                    return JsonResponse(resp)
                resp = {}
                resp['nilai_saldo'] = -99
                return JsonResponse(resp)
            except:
                resp = {}
                resp['nilai_saldo'] = -99
                return JsonResponse(resp)


def do_register(recv_id,user_id,nama):
    credentials = pika.PlainCredentials('sisdis','sisdis')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
    channel1 = connection.channel()
    channel2 = connection.channel()
    
    result = channel2.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel2.queue_bind(exchange='EX_REGISTER', queue=queue_name, routing_key='RESP_1406543725')

    message = '{"action":"register","user_id":"'+str(user_id)+'","nama":"'+str(nama)+'","sender_id":"1406543725","type":"request","ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
    channel1.basic_publish(exchange='EX_REGISTER', routing_key='REQ_'+str(recv_id), body=message)
    
    while True:
        method_frame, header_frame, body = channel2.basic_get(queue=queue_name, no_ack=True)

        if not (method_frame == None):
            try:
                connection.close()
                body_dict = json.loads(body.decode())
                action = body_dict['action']    # body_unicode = req.body.decode('utf-8')
    # body = json.loads(body_unicode)
    # user_id = body['user_id']
    # ip_tujuan = body['ip_tujuan']
    # jumlah_transfer = body['jumlah_transfer']
                tipe = body_dict['type']
                if str(action) == 'register' and str(tipe) == 'response':
                    status = int(body_dict['status_register'])
                    resp = {}
                    resp['status_register'] = status
                    return JsonResponse(resp)
                resp = {}
                resp['status_register'] = -99
                return JsonResponse(resp)
            except:
                resp = {}
                resp['status_register'] = -99
                return JsonResponse(resp)


def do_get_total_saldo(recv_id,user_id):
    credentials = pika.PlainCredentials('sisdis','sisdis')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.3',credentials=credentials))
    channel1 = connection.channel()
    channel2 = connection.channel()
    
    result = channel2.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel2.queue_bind(exchange='EX_GET_TOTAL_SALDO', queue=queue_name, routing_key='RESP_1406543725')

    message = '{"action":"get_total_saldo","user_id":"'+str(user_id)+'","sender_id":"1406543725","type":"request","ts":'+'"{:%Y-%m-%d %H:%M:%S}"'.format(datetime.datetime.now())+'}'
    channel1.basic_publish(exchange='EX_GET_TOTAL_SALDO', routing_key='REQ_'+str(recv_id), body=message)
    
    while True:
        method_frame, header_frame, body = channel2.basic_get(queue=queue_name, no_ack=True)

        if not (method_frame == None):
            try:
                connection.close()
                body_dict = json.loads(body.decode())
                action = body_dict['action']
                tipe = body_dict['type']
                if str(action) == 'get_total_saldo' and str(tipe) == 'response':
                    nilai = int(body_dict['nilai_saldo'])
                    resp = {}
                    resp['nilai_saldo'] = nilai
                    return JsonResponse(resp)
                resp = {}
                resp['nilai_saldo'] = -99
                return JsonResponse(resp)
            except:
                resp = {}
                resp['nilai_saldo'] = -99
                return JsonResponse(resp)


def callback(ch, method, properties, body):
    cabangs = list_cabang()
    try:
        body_dict = json.loads(body.decode())
        action = body_dict['action']
        tipe = body_dict['type']
        if str(action) == 'get_saldo' and str(tipe) == 'request':
            user_id = str(body_dict['user_id'])
            sender_id = body_dict['sender_id']
            ts = body_dict['ts']
            try:
                if quorum_terpenuhi():
                    nasabah = Nasabah.objects.filter(user_id = user_id)
                    total_saldo = 0
                    if user_id == '1406543725':
                        if len(nasabah) < 1:
                            nilai_saldo = -1
                            publish_resp(sender_id, nilai_saldo)
                            return
                    else:
                        # ip_domisili = get_domisili(cabangs, user_id)
                        # print(ip_domisili)
                        # if ip_domisili == 0:
                        #     nilai_saldo = -99
                        #     publish_resp(sender_id, nilai_saldo)
                        #     return
                        # else:
                        resp_saldo = do_get_total_saldo(user_id,user_id)
                        body_saldo_unicode = resp_saldo.text
                        body_saldo = json.loads(body_saldo_unicode)
                        total_saldo = int(body_saldo['nilai_saldo'])
                        nilai_saldo = total_saldo
                        publish_resp(sender_id, nilai_saldo)
                        return
                    kesalahan = False
                    for cabang in cabangs:
                        ip = cabang['ip']
                        user_id = cabang['npm']
                        if True:
                            resp_saldo = do_get_saldo(user_id,'1406543725')
                            body_saldo_unicode = resp_saldo.text
                            body_saldo = json.loads(body_saldo_unicode)
                            saldo = int(body_saldo['nilai_saldo'])
                            # print(ip,' ',saldo)
                            if saldo >= 0:
                                total_saldo += saldo
                            elif saldo < -1:
                                kesalahan = True
                            elif saldo == -1:
                                resp_register = do_register(user_id,'1406543725','Tsesar Rizqi Pradana')
                                body_register_unicode = resp_register.text
                                body_register = json.loads(body_register_unicode)
                                if str(body_register['status_register']) != '1':
                                    kesalahan = True
                            if kesalahan:
                                nilai_saldo = -3
                                publish_resp(sender_id, nilai_saldo)
                                return
                    nilai_saldo = total_saldo
                    publish_resp(sender_id, nilai_saldo)
                    return
                else:
                    nilai_saldo = -2
                    publish_resp(sender_id, nilai_saldo)
                    return
            except:
                nilai_saldo = -99
                publish_resp(sender_id, nilai_saldo)
                return
        else:
            nilai_saldo = -99
            publish_resp(sender_id,nilai_saldo)
            return
    except:
        pass

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
