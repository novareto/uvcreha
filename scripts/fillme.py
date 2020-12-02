import requests
import json


URL = "http://localhost:8080"
DATA_USER = {'username': 'cklinger', 'password':'password' }

#req = requests.put(URL+'/user.add', data=DATA_USER)
#print(req)

#req = requests.get(URL + '/users/cklinger')
#print(req.json())


#AZ_DATA = {'az': '4711'}

#req = requests.put(URL + '/users/cklinger/file.add', data=AZ_DATA)
#print(req.json())

DOC_DATA = {'content_type': 'account_info', 'state': 'init'}

req = requests.put(URL + '/api/users/cklinger/files/4711/doc.add', json=DOC_DATA)
import pdb; pdb.set_trace()
print(req.json())
