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
			resp['response'] = request_string
			resp['currentvisit'] = str(datetime.now())
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

def plus_one(req, val):
	resp = {}
	resp['apiversion'] = 2.0
	resp['plusoneret'] = int(val)+1
	return JsonResponse(resp)

def page_not_found(req):
	resp = {}
	resp['detail'] = "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again."
	resp['status'] = 404
	resp['title'] = "Not Found"
	return JsonResponse(resp)

def spesifikasi(req):
	file = open('spesifikasi.yaml', 'rb')
	resp = HttpResponse(content=file)
	resp['Content-Type'] = 'application/yaml'
	return resp
	# stream = open("spesifikasi.yaml", 'r')
	# return HttpResponse(str(yaml.load(stream)))