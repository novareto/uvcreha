import requests


URL = "http://localhost:8080"
DATA_USER = {'uid': '152020000860822', 'loginname': 'cklinger', 'password':'test' }

req = requests.put(URL+'/api/user.add', json=DATA_USER)
print(req)


#AZ_DATA = {'az': '4712'}

#req = requests.put(URL + '/api/users/cklinger/file.add', json=AZ_DATA)
#print(req.text)
#print(req.json())

#DOC_DATA = {'content_type': 'account_info'}

#req = requests.put(URL + '/api/users/cklinger/files/4711/doc.add', json=DOC#_DATA, verify=False)
#print(req.json())

