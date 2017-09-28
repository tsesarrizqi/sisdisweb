from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
import yaml, json
from .models import CountReq

# Create your views here.
def hello(req):
	if req.method == "POST":
		resp = {}
		body_unicode = req.body.decode('utf-8')
		body = json.loads(body_unicode)
		if 'request' in body:
			request_string = body['request']
			count = CountReq.objects.filter(string=request_string)
			resp2 = {"datetime": "2017-09-22T06:29:19.741889Z","state": "Morning"}
			resp['response'] = "Good " + resp2['state'] + ", " + request_string
			resp['currentvisit'] = resp2['datetime']
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
		resp['detail'] = "use POST instead of GET"
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
		resp['detail'] = "use GET instead of POST"
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
		resp['detail'] = "use GET instead of POST"
		resp['status'] = 405
		resp['title'] = "Method Not Allowed"
		return JsonResponse(resp)