import requests
import json


URL = "https://kraft.novareto.de"
URL = "http://localhost:8080"
DATA_USER = {'username': 'toto', 'password':'test' }

req = requests.put(URL+'/api/user.add', json=DATA_USER)
print(req)


#AZ_DATA = {'az': '4712'}

#req = requests.put(URL + '/api/users/cklinger/file.add', json=AZ_DATA)
#print(req.text)
#print(req.json())

#DOC_DATA = {'content_type': 'account_info'}

#req = requests.put(URL + '/api/users/cklinger/files/4711/doc.add', json=DOC#_DATA, verify=False)
#print(req.json())
