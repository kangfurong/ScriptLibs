import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random

# 配置项
FILE_NAME = "valid_proxies.json"
MAX_PROXIES = 30  # 最大有效代理数量
CHECK_EXISTING_THRESHOLD = 3  # 检查本地代理后达到此数量则跳过爬取
MAX_TOTAL_CHECK_DURATION = 30 * 60  # 检测总耗时最大不超过 30 分钟
FETCH_DELAY_SECONDS = 0.1  # 爬取延迟

PROXY_TEST_URLS_HTTP = [
    "http://httpbin.org/ip",
    "http://api-ipv4.ip.sb/ip",
    "http://ip-api.com/json/"
]

PROXY_TEST_URLS_HTTPS = [
    "https://httpbin.org/ip",
    "https://api64.ipify.org?format=json",
    "https://ipapi.co/json/"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
]

VALID_PROXIES = []
START_CHECK_TIME = None

def _proxy_key(proxy):
    return f"{proxy['type'].upper()}://{proxy['ip']}:{proxy['port']}"

def _deduplicate_proxies(proxies):
    """去重代理列表"""
    seen = set()
    result = []
    for proxy in proxies:
        key = _proxy_key(proxy)
        if key not in seen:
            seen.add(key)
            result.append(proxy)
    return result

def _get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def _get_random_proxy():
    """随机返回一个可用代理用于爬取"""
    if VALID_PROXIES:
        p = random.choice(VALID_PROXIES)
        return {p['type'].lower(): f"{p['type'].lower()}://{p['ip']}:{p['port']}"}
    return None

def _get_location(ip):
    """获取 IP 地址对应地理位置"""
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = res.json()
        if data.get("status") == "success":
            return f"{data['country']} {data['regionName']} {data['city']}"
    except:
        pass
    return "未知"

def _check_proxy(proxy):
    """检测代理是否支持 HTTP 和 HTTPS（分别从多个测试网站中选择）"""
    if time.time() - START_CHECK_TIME > MAX_TOTAL_CHECK_DURATION:
        return False

    proxies = {
        proxy['type'].lower(): f"{proxy['type'].lower()}://{proxy['ip']}:{proxy['port']}"
    }

    def _test_url(url):
        try:
            res = requests.get(url, headers=_get_random_headers(), proxies=proxies, timeout=5)
            return res.status_code == 200
        except:
            return False

    http_url = random.choice(PROXY_TEST_URLS_HTTP)
    https_url = random.choice(PROXY_TEST_URLS_HTTPS)

    http_ok = _test_url(http_url)
    https_ok = _test_url(https_url)

    if http_ok and https_ok:
        delay = random.uniform(0.1, 0.5)  # 模拟响应延迟
        proxy['delay'] = delay
        proxy['location'] = _get_location(proxy['ip'])
        VALID_PROXIES.append(proxy)
        print(f"[✓] 有效: {_proxy_key(proxy)} 支持 HTTP+HTTPS")
        return True
    else:
        print(f"[x] 无效: {_proxy_key(proxy)} 不支持 HTTP[{http_ok}] 或 HTTPS{https_ok}]")
        return False

def _load_existing_proxies():
    """加载本地代理并检测其有效性"""
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            proxies = json.load(f)
        for p in proxies:
            if len(VALID_PROXIES) >= MAX_PROXIES:
                break
            _check_proxy(p)
    except Exception as e:
        print(f"加载本地代理失败: {e}")

def _fetch_from_bzpl():
    """从 getproxy.bzpl.tech 接口获取代理，支持 HTTP 和 HTTPS"""
    url = "https://getproxy.bzpl.tech/get/"
    count = 0
    while count < MAX_PROXIES * 2:
        try:
            res = requests.get(url, headers=_get_random_headers(), proxies=_get_random_proxy(), timeout=10)
            if res.status_code == 200:
                data = res.json()
                ip_port = data.get("proxy")
                if ip_port:
                    ip, port = ip_port.split(":")
                    proxy_type = "https" if data.get("https") else "http"
                    proxy = {
                        "ip": ip,
                        "port": port,
                        "type": proxy_type
                    }
                    if _check_proxy(proxy) and len(VALID_PROXIES) >= MAX_PROXIES:
                        return
                    count += 1
                    time.sleep(FETCH_DELAY_SECONDS)
        except Exception as e:
            print(f"BZPL 获取失败: {e}")
            break

def _fetch_from_kxdaili():
    """从 kxdaili 网站爬取代理"""
    for page in range(1, 8):
        url = f"https://www.kxdaili.com/dailiip/1/{page}.html"
        try:
            res = requests.get(url, headers=_get_random_headers(), proxies=_get_random_proxy(), timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            trs = soup.select("table tbody tr")
            for tr in trs:
                tds = tr.find_all("td")
                proxy = {
                    "ip": tds[0].text.strip(),
                    "port": tds[1].text.strip(),
                    "type": tds[3].text.strip().lower()
                }
                if _check_proxy(proxy) and len(VALID_PROXIES) >= MAX_PROXIES:
                    return
            time.sleep(FETCH_DELAY_SECONDS)
        except Exception as e:
            print(f"KXD 获取失败: {e}")
            continue

def _fetch_from_openproxylist():
    """从 openproxylist.xyz 获取 HTTP 代理列表"""
    url = "https://api.openproxylist.xyz/http.txt"
    try:
        res = requests.get(url, headers=_get_random_headers(), proxies=_get_random_proxy(), timeout=10)
        if res.status_code == 200:
            lines = res.text.strip().splitlines()
            for line in lines:
                if len(VALID_PROXIES) >= MAX_PROXIES:
                    return
                ip_port = line.strip().split(":")
                if len(ip_port) != 2:
                    continue
                proxy = {
                    "ip": ip_port[0],
                    "port": ip_port[1],
                    "type": "http"
                }
                _check_proxy(proxy)
                time.sleep(FETCH_DELAY_SECONDS)
    except Exception as e:
        print(f"OpenProxyList 获取失败: {e}")

def save_proxies():
    """保存有效代理到文件"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(VALID_PROXIES[:MAX_PROXIES], f, ensure_ascii=False, indent=2)

def get_valid_proxies():
    """对外接口，只从本地文件读取代理，不进行检测"""
    try:
        if not os.path.exists(FILE_NAME):
            return []
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def main():
    """主执行流程"""
    print(f"文件名:{FILE_NAME},最多获取代理个数={MAX_PROXIES},重启检测代理下限={CHECK_EXISTING_THRESHOLD},任务超时分钟数={MAX_TOTAL_CHECK_DURATION}\n")
    global START_CHECK_TIME
    START_CHECK_TIME = time.time()

    print("[+] 加载本地代理...")
    _load_existing_proxies()

    if len(VALID_PROXIES) >= CHECK_EXISTING_THRESHOLD:
        print("[✓] 已有足够可用代理，跳过爬取")
    else:
        print("[+] 爬取 BZPL 代理...")
        _fetch_from_bzpl()

        if len(VALID_PROXIES) < MAX_PROXIES:
            print("[+] 爬取 KXDaili 代理...")
            _fetch_from_kxdaili()

        if len(VALID_PROXIES) < MAX_PROXIES:
            print("[+] 爬取 OpenProxyList 代理...")
            _fetch_from_openproxylist()

    VALID_PROXIES[:] = _deduplicate_proxies(VALID_PROXIES)
    save_proxies()
    print(f"[✓] 共获取可用代理 {len(VALID_PROXIES)} 个")

if __name__ == "__main__":
    main()
