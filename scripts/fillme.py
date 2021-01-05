import requests
import json


URL = "https://kraft.novareto.de"
DATA_USER = {'username': 'cklinger', 'password':'password' }

#req = requests.put(URL+'/api/user.add', json=DATA_USER)
#print(req)


AZ_DATA = {'az': '4712'}

#req = requests.put(URL + '/api/users/cklinger/file.add', json=AZ_DATA)
#print(req.text)
#print(req.json())

DOC_DATA = {'content_type': 'account_info'}

req = requests.put(URL + '/api/users/cklinger/files/4711/doc.add', json=DOC_DATA, verify=False)
print(req.json())
