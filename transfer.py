import os, django, requests

django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sisdisweb.settings")

from sisdis1.models import Nasabah

user_id = str(input('Masukkan user ID untuk ditransfer transfer: '))
ip_tujuan = str(input('Masukkan IP cabang tujuan transfer: '))
jumlah_transfer = int(input('Masukkan jumlah transfer: '))

try:
	nasabah = Nasabah.objects.get(user_id = user_id)
	body_post = {'user_id':user_id, 'nilai':jumlah_transfer}
	resp_transfer = requests.post('http://'+ip_tujuan+'/ewallet/transfer', json = body_post)
	body_transfer_unicode = resp_transfer.text
	body_transfer = json.loads(body_transfer_unicode)
	if str(body_transfer['status_transfer']) == '1':
		nasabah.saldo = nasabah.saldo - jumlah_transfer
		nasabah.save()
	print('Transfer sejumlah ',jumlah_transfer,' ke cabang ',ip_tujuan,' berhasil.')
except:
	print('Terjadi kesalahan. Transfer sejumlah ',jumlah_transfer,' ke cabang ',ip_tujuan,' gagal.')
	print('Kemungkinan user ID yang diberikan belum terdaftar di cabang ini.')