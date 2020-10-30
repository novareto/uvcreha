document manager
================

curl -X POST localhost:8080/user.add --data username=test --data password=test
curl -X POST localhost:8080/users/test/folder.add --data az=myfolder
curl localhost:8080/users/test/folders
curl localhost:8080/users/test/details
