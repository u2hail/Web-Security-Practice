1、打开阿里云官网www.aliyun.com

![image-20260610094352618](images/image-20260610094352618.png)

2、在产品里搜索容器镜像服务

![image-20260610094453822](images/image-20260610094453822.png)

3、找到相关资源，打开控制台

![image-20260610094535281](images/image-20260610094535281.png)

4、找到加速器地址，复制到daemon.json

![image-20260610094624650](images/image-20260610094624650.png)

![image-20260610095211243](images/image-20260610095211243.png)

5、sudo docker pull betsy0/pwdflielogic:latest

​	  sudo docker run -d -p 10001:81 --restart=always betsy0/pwdflielogic:latest

192.168.171.133：10001

![image-20260610095738274](images/image-20260610095738274.png)

完成