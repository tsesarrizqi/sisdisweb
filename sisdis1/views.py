from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def hello(req):
	return HttpResponse("sukses_hello")

def plus_one(req, val):
	return HttpResponse("suskses_plus_one")