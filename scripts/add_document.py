import requests


URL = "http://localhost:8080"


DATA_USER = {'uid': '152020000860822', 'loginname': 'cklinger', 'password':'test' }
#req = requests.put(URL+'/api/user.add', json=DATA_USER)
#print(req)


AZ_DATA = {'az': '3', 'mnr':'000000930063497', 'vid':'152020000516523'}
req = requests.put(URL + '/api/users/152020000860822/file.add', json=AZ_DATA)
#print(req.json())

DOC_DATA = {'content_type': 'account_info'}

req = requests.put(URL + '/api/users/cklinger/files/4711/doc.add', json=DOC_DATA, verify=False)
print(req.json())

