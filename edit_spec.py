import socket, yaml

hostname = socket.gethostbyname(socket.gethostname())
stream_r = open('spesifikasi.yaml')
spec = yaml.load(stream_r)
spec['host'] = str(hostname)+':80'
stream_w = open('spesifikasi.yaml', 'w')
yaml.dump(spec, stream_w)
