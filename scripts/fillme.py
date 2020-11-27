import requests


URL = "http://localhost:8080"
DATA_USER = {'username': 'cklinger', 'password':'password' }

req = requests.put(URL+'/user.add', data=DATA_USER)
print(req)

req = requests.get(URL + '/users/cklinger')
print(req.json())


AZ_DATA = {'az': '4711'}

req = requests.put(URL + '/users/cklinger/file.add', data=AZ_DATA)
print(req.json())

DOC_DATA = {'body': 'HANS PETER'}

req = requests.put(URL + '/users/cklinger/4711/document.add', data=DOC_DATA)
print(req.json())
