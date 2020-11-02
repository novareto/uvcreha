document manager
================

curl -X POST localhost:8080/user.add --data username=test --data password=test
curl localhost:8080/users/test
curl -X POST localhost:8080/users/test/folder.add --data az=myfolder
curl localhost:8080/users/test/details

curl localhost:8080/users/test/folders/myfolder
curl -X POST localhost:8080/users/test/folders/myfolder/doc.add --data name='Some Doc' --data state='Submitted' content_type='plain/text'


curl -X DELETE localhost:8080/users/test/folders/myfolder
