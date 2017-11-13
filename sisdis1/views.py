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

def list_cabang():
	npm = ["1406543574","1406579100","1406543725","1406527620","1406527513","1306398983","1406572025","1406543763"]
	resp_cabang = requests.get('http://152.118.31.2/list.php')
	body_cabang_unicode = resp_cabang.text
	body_cabang = json.loads(body_cabang_unicode)
	cabangs = []
	for cabang in body_cabang:
		if cabang['npm'] in npm:
			cabangs.append(cabang)
	return cabangs

def quorum_terpenuhi():
	# resp_cabang = requests.get('http://152.118.31.2/list.php')
	# body_cabang_unicode = resp_cabang.text
	# body_cabang = json.loads(body_cabang_unicode)
	quorum = list_cabang()
	print(quorum)
	# quorum = [{"ip": "172.17.0.57","npm": "1406543574"},
	# 	{"ip": "172.17.0.17","npm": "1406579100"},
	# 	{"ip": "172.17.0.49","npm": "1406543725"},
	# 	{"ip": "172.17.0.58","npm": "1406527620"},
	# 	{"ip": "172.17.0.60","npm": "1406527513"},
	# 	{"ip": "172.17.0.63","npm": "1306398983"},
	# 	{"ip": "172.17.0.26","npm": "1406572025"},
	# 	{"ip": "172.17.0.48","npm": "1406543763"}]
	count = 0
	for cabang in quorum:
		try:
			ip = cabang['ip']
			resp_ping = requests.post('http://'+ip+'/ewallet/ping', timeout=1)
			body_ping_unicode = resp_ping.text
			body_ping = json.loads(body_ping_unicode)
			if str(body_ping['pong']) == '1':
				count += 1
		except:
			count += 0
	print(count)
	return count >= 5

def quorum_terpenuhi_all():
	# resp_cabang = requests.get('http://152.118.31.2/list.php')
	# body_cabang_unicode = resp_cabang.text
	# body_cabang = json.loads(body_cabang_unicode)
	quorum = list_cabang()
	# [{"ip": "172.17.0.57","npm": "1406543574"},
	# 	{"ip": "172.17.0.17","npm": "1406579100"},
	# 	{"ip": "172.17.0.49","npm": "1406543725"},
	# 	{"ip": "172.17.0.58","npm": "1406527620"},
	# 	{"ip": "172.17.0.60","npm": "1406527513"},
	# 	{"ip": "172.17.0.63","npm": "1306398983"},
	# 	{"ip": "172.17.0.26","npm": "1406572025"},
	# 	{"ip": "172.17.0.48","npm": "1406543763"}]
	count = 0
	for cabang in quorum:
		try:
			ip = cabang['ip']
			resp_ping = requests.post('http://'+ip+'/ewallet/ping', timeout=1)
			print(ip,' ',resp_ping)
			body_ping_unicode = resp_ping.text
			body_ping = json.loads(body_ping_unicode)
			if str(body_ping['pong']) == '1':
				count += 1
		except:
			count += 0
	print(count)
	return count >= 8

def ping(req):
	if req.method == "POST":
		resp = {}
		resp['pong'] = 1
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
				resp['status_register'] = -4
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
		resp['nilai_saldo'] = -99
		return JsonResponse(resp)

def get_domisili(cabangs, user_id):
	for cabang in cabangs:
		if cabang['npm'] == user_id:
			return cabang['ip']
	return 0

def get_total_saldo(req):
	cabangs = list_cabang()
	# [{"ip": "172.17.0.57","npm": "1406543574"},
	# 	{"ip": "172.17.0.17","npm": "1406579100"},
	# 	{"ip": "172.17.0.49","npm": "1406543725"},
	# 	{"ip": "172.17.0.58","npm": "1406527620"},
	# 	{"ip": "172.17.0.60","npm": "1406527513"},
	# 	{"ip": "172.17.0.63","npm": "1306398983"},
	# 	{"ip": "172.17.0.26","npm": "1406572025"},
	# 	{"ip": "172.17.0.48","npm": "1406543763"}]
	print('masuk1')
	try:
		if quorum_terpenuhi_all():
			body_unicode = req.body.decode('utf-8')
			body = json.loads(body_unicode)
			user_id = body['user_id']
			nasabah = Nasabah.objects.filter(user_id = user_id)
			total_saldo = 0
			if user_id == '1406543725':
				if len(nasabah) < 1:
					resp = {}
					resp['nilai_saldo'] = -1
					return JsonResponse(resp)
			else:
				ip_domisili = get_domisili(cabangs, user_id)
				print(ip_domisili)
				if ip_domisili == 0:
					resp = {}
					resp['nilai_saldo'] = -99
					return JsonResponse(resp)
				else:
					body_post = {'user_id': user_id}
					resp_saldo   = requests.post('http://'+ip_domisili+'/ewallet/getTotalSaldo', json = body_post)
					body_saldo_unicode = resp_saldo.text
					body_saldo = json.loads(body_saldo_unicode)
					total_saldo = int(body_saldo['nilai_saldo'])
					resp = {}
					resp['nilai_saldo'] = total_saldo
					return JsonResponse(resp)
			print('quorum terpenuhi')
			kesalahan = False
			for cabang in cabangs:
				ip = cabang['ip']
				user_id = cabang['npm']
				# headers={'content-type':'application/json'},
				if True:
					body_get_saldo = {'user_id': '1406543725'}
					resp_saldo = requests.post('http://'+ip+'/ewallet/getSaldo', json = body_get_saldo)
					body_saldo_unicode = resp_saldo.text
					body_saldo = json.loads(body_saldo_unicode)
					saldo = int(body_saldo['nilai_saldo'])
					print(ip,' ',saldo)
					if saldo >= 0:
						total_saldo += saldo
					elif saldo < -1:
						kesalahan = True
					elif saldo == -1:
						body_post_register = {'user_id': '1406543725', 'nama': 'Tsesar Rizqi Pradana'}
						resp_register = requests.post('http://'+ip+'/ewallet/register', json = body_post_register)
						body_register_unicode = resp_register.text
						body_register = json.loads(body_register_unicode)
						if str(body_register['status_register']) != '1':
							print('masuk salah register')
							kesalahan = True
					if kesalahan:
						resp = {}
						resp['nilai_saldo'] = -3
						return JsonResponse(resp)
			resp = {}
			resp['nilai_saldo'] = total_saldo
			return JsonResponse(resp)
		else:
			resp = {}
			resp['nilai_saldo'] = -2
			return JsonResponse(resp)
	except:
		resp = {}
		resp['nilai_saldo'] = -99
		return JsonResponse(resp)

def transfer(req):
	try:
		body_unicode = req.body.decode('utf-8')
		body = json.loads(body_unicode)
		user_id = body['user_id']
		nilai = body['nilai']
		resp = {}
		if int(nilai) < 0 or int(nilai) > 1000000000:
			resp['status_transfer'] = -5
			return JsonResponse(resp)
		nasabah = Nasabah.objects.filter(user_id = user_id)
		if len(nasabah) == 1:
			if quorum_terpenuhi():
				try:
					nasabah[0].saldo += int(nilai)
					nasabah[0].save()
					resp['status_transfer'] = 1
					return JsonResponse(resp)
				except:
					resp['status_transfer'] = -4
					return JsonResponse(resp)
			else:
				resp['status_transfer'] = -2
		else:
			resp['status_transfer'] = -1
		return JsonResponse(resp)
	except:
		resp = {}
		resp['status_transfer'] = -99
		return JsonResponse(resp)


#############################################
#############################################
#############################################

def do_transfer(user_id, ip_tujuan, jumlah_transfer):
	# body_unicode = req.body.decode('utf-8')
	# body = json.loads(body_unicode)
	# user_id = body['user_id']
	# ip_tujuan = body['ip_tujuan']
	# jumlah_transfer = body['jumlah_transfer']

	nasabah = Nasabah.objects.filter(user_id = user_id)
	if len(nasabah) == 0:
		resp = {}
		resp['status_transfer'] = -1
		return JsonResponse(resp)
	if nasabah[0].saldo < int(jumlah_transfer):
		resp = {}
		resp['status_transfer'] = -5
		return JsonResponse(resp)
	body_post_saldo = {'user_id':user_id}
	resp_saldo = requests.post('http://'+ip_tujuan+'/ewallet/getSaldo', json = body_post_saldo)
	body_saldo_unicode = resp_saldo.text
	body_saldo = json.loads(body_saldo_unicode)
	if str(body_saldo['nilai_saldo']) == '-1':
		body_post_register = {'user_id':user_id, 'nama':nasabah[0].name}
		resp_register = requests.post('http://'+ip_tujuan+'/ewallet/register', json = body_post_register)
		body_register_unicode = resp_register.text
		body_register = json.loads(body_register_unicode)
		if str(body_register['status_register']) != '1':
			resp = {}
			resp['status_transfer'] = -99
			return JsonResponse(resp)
	try:
		body_post_transfer = {'user_id':user_id, 'nilai':int(jumlah_transfer)}
		resp_transfer = requests.post('http://'+ip_tujuan+'/ewallet/transfer', json = body_post_transfer)
		body_transfer_unicode = resp_transfer.text
		body_transfer = json.loads(body_transfer_unicode)
		resp = {}
		if str(body_transfer['status_transfer']) == '1':
			nasabah[0].saldo = nasabah[0].saldo - int(jumlah_transfer)
			nasabah[0].save()
		resp['status_transfer'] = body_transfer['status_transfer']
		return JsonResponse(resp)
	except:
		resp = {}
		resp['status_transfer'] = -99
		return JsonResponse(resp)

def do_register(user_id, nama, ip_tujuan):
	body_post_register = {'user_id':user_id, 'nama':nama}
	resp_register = requests.post('http://'+ip_tujuan+'/ewallet/register', json = body_post_register)
	body_register_unicode = resp_register.text
	body_register = json.loads(body_register_unicode)
	resp = {}
	resp['status_register'] = body_register['status_register']
	return JsonResponse(resp)

def do_get_saldo(user_id, ip_tujuan):
	body_post_saldo = {'user_id':user_id}
	resp_saldo = requests.post('http://'+ip_tujuan+'/ewallet/getSaldo', json = body_post_saldo)
	body_saldo_unicode = resp_saldo.text
	body_saldo = json.loads(body_saldo_unicode)
	resp = {}
	resp['nilai_saldo'] = body_saldo['nilai_saldo']
	return JsonResponse(resp)

def do_get_total_saldo(user_id, ip_tujuan):
	body_post_saldo = {'user_id':user_id}
	resp_saldo = requests.post('http://'+ip_tujuan+'/ewallet/getTotalSaldo', json = body_post_saldo)
	body_saldo_unicode = resp_saldo.text
	body_saldo = json.loads(body_saldo_unicode)
	resp = {}
	resp['nilai_saldo'] = body_saldo['nilai_saldo']
	return JsonResponse(resp)

def gui(req):
	if req.method == "POST":
		resp = {}
		command = req.POST.get('command', '')
		if command == 'register':
			user_id = req.POST.get('user_id', '')
			ip_tujuan = req.POST.get('cabang', '')
			nama = req.POST.get('nama', '')
			return do_register(user_id,nama,ip_tujuan)
		elif command == 'getsaldo':
			user_id = req.POST.get('user_id', '')
			ip_tujuan = req.POST.get('cabang', '')
			return do_get_saldo(user_id,ip_tujuan)
		elif command == 'gettotalsaldo':
			user_id = req.POST.get('user_id', '')
			ip_tujuan = req.POST.get('cabang', '')
			return do_get_total_saldo(user_id,ip_tujuan)
		elif command == 'transfer':
			user_id = req.POST.get('user_id', '')
			ip_tujuan = req.POST.get('cabang', '')
			jumlah_transfer = req.POST.get('jumlah_transfer', '')
			return do_transfer(user_id,ip_tujuan,jumlah_transfer)
		else:
			resp['response'] = 'Terdapat kesalahan.'
		return JsonResponse(resp)
	return render(req, 'gui.html',{})
