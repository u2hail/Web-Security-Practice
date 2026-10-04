XSS报告

## 漏洞概要

XSS（跨站脚本）是一类高危漏洞，存在于浏览器渲染页面的环境中，本质上是在数据与代码没有严格分离的环境下，将用户输入的内容作为HTML标签或JavaScript代码被浏览器解析执行。XSS漏洞常见于将用户输入直接输出到页面、未做上下文编码的场景。攻击者可通过XSS窃取用户Cookie实现会话劫持、以受害者身份执行操作、挂马钓鱼，存储型XSS更可用来攻击后台管理员。

XSS与SQL注入同源，都是"代码与数据没有分离"：SQL注入是数据库分不清SQL语句和数据，XSS是浏览器分不清页面标记和用户数据。区别只在于失守的层次——一个在数据库解析器，一个在浏览器解析器。

XSS按数据经过哪里分为三种：**反射型**的特点是数据经服务端响应立即回显，不落库，需要诱导受害者点击特制链接；**存储型**的特点是数据先落库，之后每次被访问都会触发，不需要诱导点击，危害最大，可用来打后台管理员；**DOM型**的特点是全程在前端完成，服务端不参与，数据被JavaScript从URL取出后写进危险函数（sink），如innerHTML、document.write、eval。

## 漏洞检测

0、寻找输入点

1、判断输出点（数据回到了哪里）

2、检测闭合方式

3、检测能否执行

4、检测过滤方式

5、检测XSS类型

## 打靶练习

### 【DOM高等难度】

![image-20261001225720357](images/image-20261001225720357.png)

从URL结构可以看出default是参数，将参数改为输入<script>alert(1)</script>测试xss漏洞

![image-20261001230237095](images/image-20261001230237095.png)

提交表单后页面自动回到了参数修改前的URL

![image-20261002114631816](images/image-20261002114631816.png)

查看devtools的network可以看到，刚刚的URL返回页面状态为302重定向，所以没有生效<script>alert(1)</script>

![image-20261002123938040](images/image-20261002123938040.png)

查看devtools的network，响应内容是

HTTP/1.1 302 Found Date: Thu, 01 Oct 2026 17:48:44 GMT Server: Apache/2.4.23 (Win32) OpenSSL/1.0.2j PHP/5.4.45 X-Powered-By: PHP/5.4.45 Expires: Thu, 19 Nov 1981 08:52:00 GMT Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0 Pragma: no-cache **location: ?default=English** Content-Length: 146 Keep-Alive: timeout=5, max=100 Connection: Keep-Alive Content-Type: text/html

可以看到被重定向的参数为?default=English

写成URL的形式[Vulnerability: DOM Based Cross Site Scripting (XSS) :: Damn Vulnerable Web Application (DVWA) v1.10 *Development*](http://127.0.0.1/DVWA-master/vulnerabilities/xss_d/?default=English)

这就是刚刚看到的页面

![image-20261002155309066](images/image-20261002155309066.png)

<SCRIPT>alert(1)</SCRIPT>尝试大写script，返回页面重定向

![image-20261002155706676](images/image-20261002155706676.png)

<sCript>alert(1)</sCript>尝试其他大小写组合，返回页面重定向

![image-20261002155758570](images/image-20261002155758570.png)

<script >alert(1)</script >尝试加入空格绕过，返回页面重定向

![image-20261002160108955](images/image-20261002160108955.png)

考虑到可能是通过匹配删除的方式过滤，尝试

`<scr<script>ipt>alert(1)</script>`

`<scri<script>pt>alert(1)</script>`

`<script<script>>alert(1)</script>`

全部返回页面重定向

![image-20261002160446214](images/image-20261002160446214.png)

初步判断script被多种条件过滤，换用<img src=x onerror=alert(1)>写入default

![image-20261004010946229](images/image-20261004010946229.png)

返回页面重定向，尝试从解析规则入手

![image-20261004011203668](images/image-20261004011203668.png)

URL：http://127.0.0.1/DVWA-master/vulnerabilities/xss_d/#?default=%3Cimg%20src=x%20onerror=alert(1)%3E

![image-20261004011228727](images/image-20261004011228727.png)

返回弹窗，验证漏洞存在。

### 【反射型高等难度】

![image-20261001230101602](images/image-20261001230101602.png)

页面上存在文本框，输入<script>alert(1)</script>测试漏洞

![image-20261004011609065](images/image-20261004011609065.png)

返回Hello >

![image-20261004011840686](images/image-20261004011840686.png)

测试<script>alert(1)，返回Hello (1)

![image-20261004012007177](images/image-20261004012007177.png)

测试<script>alert，返回Hello

![image-20261004012035906](images/image-20261004012035906.png)测试<script>，返回Hello >

可以得到几点信息：

1、防护方式为黑名单过滤

2、过滤方式为匹配删除

![image-20261004015742983](images/image-20261004015742983.png)

输入<img src=x onerror=alert(1)>

![image-20261004015808933](images/image-20261004015808933.png)

返回弹窗，验证漏洞存在

【存储型高等难度】

![image-20261004020112923](images/image-20261004020112923.png)

同时测试两个字段<script>alert(1)</script>

![image-20261004020142637](images/image-20261004020142637.png)

返回

Name: >
Message: alert(1)

![image-20261004020236817](images/image-20261004020236817.png)

测试大小写组合<scRipt>alert(1)</script>

![image-20261004020308313](images/image-20261004020308313.png)

返回

Name: >
Message: alert(1)

![image-20261004020401758](images/image-20261004020401758.png)

测试<img src=x onerror=alert(1)>

![image-20261004020421728](images/image-20261004020421728.png)

页面返回弹窗，验证漏洞存在。

## 总结

### 一、影响与危害

【先说技术上能做什么、需不需要凭据；再说本次已实际验证了什么（具体到哪个功能、哪类XSS、实际拿到了什么）；最后说对业务意味着什么】

**利用门槛**：【反射型/存储型/DOM型 的门槛不一样，分别写】

### 二、修复建议

1、根本修复：
   按输出上下文编码，而不是"统一转义一遍"。原理是让用户数据以**文本**身份
   进入解析器，而不是以**标记**身份。不同位置的编码方式不同：

   - HTML正文  → HTML实体编码（`<` → `&lt;`）
   - HTML属性  → 属性值加引号 + HTML实体编码（含 `"` 和 `'`）
   - JS字符串  → JS转义（不能只做HTML实体编码）
   - URL参数   → URL编码

   PHP里对应 `htmlspecialchars($x, ENT_QUOTES, 'UTF-8')`，
   注意必须带 `ENT_QUOTES`——只转义双引号不转义单引号，
   属性用单引号包裹时仍可越出。

2、为什么不能用转义/过滤替代：
   禁了 `<script>` 还有 `<img onerror>`、`<svg onload>`、`<details open ontoggle>`，
   黑名单永远列不全。与SQL注入的结论完全一致：这是"堵"而不是"隔离"。

3、临时缓解（代码改不动时）：
   - Cookie加 `HttpOnly`，让JS读不到Cookie，即便XSS成立也偷不走会话
   - 配CSP限制脚本来源、禁止内联脚本
   - 敏感操作加二次验证
   - 限制输入长度（只能挡住长payload，挡不住 `<svg onload=alert(1)>`，只能算辅助）

4、同类问题排查：
   按"用户输入在哪里被输出"对全部页面做一次检索，重点检查：
   - 所有搜索/留言/资料类的回显点
   - 后台管理页面（存储型XSS最常打的地方）
   - 请求头被记录并回显的位置（User-Agent、Referer 记进库后在后台展示）
   - 前端JS里的DOM sink

5、修复验证方法：
   用原 payload 复测：【本关的复测 payload】
   预期：源码里 `<` 变成 `&lt;`，页面显示为文本，不执行。

   并需更换上下文复测（只改一处编码不算修好）：
   - 属性上下文：`" onmouseover=alert(1) x="`，预期引号被编码成 `&quot;`
   - 单引号属性：`' onmouseover=alert(1) x='`，预期 `'` 被编码成 `&#39;`
     （这一条专门验证 `ENT_QUOTES` 是否生效）
   - JS字符串内：`';alert(1);//`，预期引号被转义

   并需更换标签复测，确认黑名单不是唯一防线：
   `<img src=1 onerror=alert(1)>`、`<svg onload=alert(1)>`
   预期：全部被编码输出，无一执行。

### 三、延伸思考

**卡在哪**：

1、【本关实际卡住的地方。写"我一开始以为…后来发现…"这种过程，不要只写结论】
2、【】

**学到什么**：

1、【能带到下一关的结论】
2、【】
