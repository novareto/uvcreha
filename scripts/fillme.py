import requests
import json


URL = "http://localhost:8080"
DATA_USER = {'username': 'hans', 'password':'password' }

#req = requests.put(URL+'/api/user.add', json=DATA_USER)
#print(req)


#AZ_DATA = {'az': '4791'}

#req = requests.put(URL + '/api/users/hans/file.add', json=AZ_DATA)
#print(req.json())

DOC_DATA = {'content_type': 'account_info'}

req = requests.put(URL + '/api/users/hans/files/4791/doc.add', json=DOC_DATA)
print(req.json())
