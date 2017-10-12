from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
import yaml, json, requests
from .models import CountReq, Nasabah

# Create your views here.
def hello(req):
	if req.method == "POST":
		resp = {}
		body_unicode = req.body.decode('utf-8')
		body = json.loads(body_unicode)
		if 'request' in body:
			request_string = body['request']
			count = CountReq.objects.filter(string=request_string)
			resp_time = requests.get('http://172.17.0.70:17088')
			body_time_unicode = resp_time.text
			body_time = json.loads(body_time_unicode)
			resp['response'] = "Good " + body_time['state'] + ", " + request_string
			resp['currentvisit'] = body_time['datetime']
			if len(count) > 0:
				tmp = count[0].count+1
				count[0].count = tmp
				count[0].save()
				resp['count'] = tmp
			else:
				new = CountReq(string=request_string,count=1)
				new.save()
				resp['count'] = 1
			resp['apiversion'] = 2.0
		else:
			resp['detail'] = "'request' is a required property"
			resp['status'] = 400
			resp['title'] = "Bad Request"
		return JsonResponse(resp)
	else:
		resp = {}
		resp['detail'] = "Method "+str(req.method)+" is not allowed"
		resp['status'] = 405
		resp['title'] = "Method Not Allowed"
		return JsonResponse(resp)

def plus_one(req, val):
	if req.method == "GET":
		resp = {}
		resp['apiversion'] = 2.0
		resp['plusoneret'] = int(val)+1
		return JsonResponse(resp)
	else:
		resp = {}
		resp['detail'] = "Method "+str(req.method)+" is not allowed"
		resp['status'] = 405
		resp['title'] = "Method Not Allowed"
		return JsonResponse(resp)

def page_not_found(req):
	resp = {}
	resp['detail'] = "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again."
	resp['status'] = 404
	resp['title'] = "Not Found"
	return JsonResponse(resp)

def spesifikasi(req):
	if req.method == "GET":
		file = open('spesifikasi.yaml')
		resp = HttpResponse(file.read())
		resp['Content-Type'] = 'text/x-yaml'
		return resp
	else:
		resp = {}
		resp['detail'] = "Method "+str(req.method)+" is not allowed"
		resp['status'] = 405
		resp['title'] = "Method Not Allowed"
		return JsonResponse(resp)

def quorum_terpenuhi():
	# resp_cabang = requests.get('http://152.118.31.2/list.php')
	# body_cabang_unicode = resp_cabang.text
	# body_cabang = json.loads(body_cabang_unicode)
	quorum = [{'ip':'172.17.0.49','npm':'1406543725'}]
	count = 0
	for cabang in quorum:
		ip = cabang['ip']
		resp_ping = requests.get('http://'+ip+'/ewallet/ping')
		body_ping_unicode = resp_ping.text
		body_ping = json.loads(body_ping_unicode)
		if str(body_ping['pong']) == '1':
			count += 1
	return count >= 1

def ping(req):
	if req.method == "POST":
		try:
			resp = {}
			resp['pong'] = 1
			return JsonResponse(resp)
		except:
			resp = {}
			resp['pong'] = -99
			return JsonResponse(resp)
	else:
		resp = {}
		resp['pong'] = -99
		return JsonResponse(resp)

def register(req):
	if req.method == "POST":
		try:
			body_unicode = req.body.decode('utf-8')
			body = json.loads(body_unicode)
			resp = {}
			user_id = body['user_id']
			name = body['nama']
			nasabah0 = Nasabah.objects.filter(user_id = user_id)
			if len(nasabah0) == 0:
				if quorum_terpenuhi():
					nasabah = Nasabah(user_id = user_id, name = name, saldo = 0)
					nasabah.save()
					resp['status_register'] = 1
				else:
					resp['status_register'] = -2
			else:
				resp['status_register'] = -99
			return JsonResponse(resp)
		except:
			resp = {}
			resp['status_register'] = -4
			return JsonResponse(resp)
	else:
		resp = {}
		resp['status_register'] = -99
		return JsonResponse(resp)

def get_saldo(req):
	if req.method == "POST":
		try:
			body_unicode = req.body.decode('utf-8')
			body = json.loads(body_unicode)
			resp = {}
			user_id = body['user_id']
			nasabah = Nasabah.objects.filter(user_id = user_id)
			if len(nasabah) == 1:
				if quorum_terpenuhi():
					resp['nilai_saldo'] = nasabah[0].saldo
				else:
					resp['nilai_saldo'] = -2
			else:
				resp['nilai_saldo'] = -1
			return JsonResponse(resp)
		except:
			resp = {}
			resp['nilai_saldo'] = -4
			return JsonResponse(resp)
	else:
		resp = {}
		resp['status_register'] = -99
		return JsonResponse(resp)

