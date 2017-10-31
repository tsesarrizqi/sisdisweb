import os, django, requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sisdisweb.settings")
django.setup()

from sisdis1.models import Nasabah

user_id = str(input('Masukkan user ID untuk ditransfer: '))
ip_tujuan = str(input('Masukkan IP cabang tujuan transfer: '))
jumlah_transfer = int(input('Masukkan jumlah transfer: '))

nasabah = Nasabah.objects.filter(user_id = user_id)
if len(nasabah) == 0:
	print('User ID belum terdaftar di sistem ini.')
	return

body_post_saldo = {'user_id':user_id}
resp_saldo = requests.post('http://'+ip_tujuan+'/ewallet/getSaldo', json = body_post)
body_saldo_unicode = resp_saldo.text
body_saldo = json.loads(body_saldo_unicode)
if str(body_saldo['nilai_saldo']) == '-1':
	body_post_register = {'user_id':user_id, 'nama':nasabah[0].nama}
	resp_register = requests.post('http://'+ip_tujuan+'/ewallet/resgiter', json = body_post_register)
	body_register_unicode = resp_register.text
	body_register = json.loads(body_register_unicode)
	if str(body_register['status_register']) != '1':
		print('Terjadi kesalahan. Transfer sejumlah ',jumlah_transfer,' ke cabang ',ip_tujuan,' gagal.')
		return
try:
	body_post_transfer = {'user_id':user_id, 'nilai':jumlah_transfer}
	resp_transfer = requests.post('http://'+ip_tujuan+'/ewallet/transfer', json = body_post_transfer)
	body_transfer_unicode = resp_transfer.text
	body_transfer = json.loads(body_transfer_unicode)
	if str(body_transfer['status_transfer']) == '1':
		nasabah.saldo = nasabah.saldo - jumlah_transfer
		nasabah.save()
		print('Transfer sejumlah ',jumlah_transfer,' ke cabang ',ip_tujuan,' berhasil.')
	else:
		print('Transfer sejumlah ',jumlah_transfer,' ke cabang ',ip_tujuan,' gagal.')
except:
	print('Terjadi kesalahan. Transfer sejumlah ',jumlah_transfer,' ke cabang ',ip_tujuan,' gagal.')