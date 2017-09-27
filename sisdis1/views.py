from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
import yaml, json

# Create your views here.
def hello(req):
	if req.method == "POST":
		resp = {}
		body_unicode = req.body.decode('utf-8')
		body = json.loads(body_unicode)
		request_string = body['request']
		# stream = open("/home/tsesar/sisdisweb/spesifikasi.yaml", 'r')
		# tmp = yaml.load(stream)
		resp['response'] = request_string
		resp['apiversion'] = "2.0"
		# resp['body'] = body_data
		resp['currentvisit'] = str(datetime.now())		
		# resp = json.dumps(data)
		return JsonResponse(resp)


def plus_one(req, val):
	
	return HttpResponse("suskses_plus_one")