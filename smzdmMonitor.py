import requests
from bs4 import BeautifulSoup
import random
import json
import time
import os
from libs.kToolLibs import kMD5FileManager
import kCustomNotify

# =============================
# 白名单配置说明：
# whitekeylist 为一个列表，每个元素是一个配置项，包含：
# - keywords：关键词列表，表示必须命中这些关键词组（每组是“或”关系，组与组之间是“与”关系）
# - "keywords": [["苹果", "iPhone"], ["16"]],表示 苹果 16，iphone 16都是关键字
# - exclude_keywords：排除关键词组，每组是“与”关系，组之间是“或”关系
# - "exclude_keywords": [["16e"], ["二手", "手机"]],表示排除包含16e 和 包含 二手且手机
# - price_range：一个二元组 (min_price, max_price)，表示价格范围（元）
# =============================

whitekeylist = [
    {
        "keywords": [["苹果", "iPhone"], ["16"],["256","512","1T"]],
        "exclude_keywords": [["16e"],["MAC"], ["二手"],],
        "price_range": (1000, 4000)
    },
    {
        "keywords": [["华为", "huawei"], ["p70","pura 70","mate 70","mate 60"],["256","512","1T"]],
        "exclude_keywords": [["16e"], ["二手"],],
        "price_range": (1000, 4000)
    },
    {
        "keywords": [["菜籽油","食用油","玉米油",],["5L"],],
        "exclude_keywords": [],
        "price_range": (0, 35)
    },
    {
        "keywords": [["大米","金龙鱼","福临门","五常","柴火大院" ],["5kg"],],
        "exclude_keywords": [],
        "price_range": (0, 15)
    },
    {
        "keywords": [["沐浴露", ],["舒肤佳"],],
        "exclude_keywords": [],
        "price_range": (0, 10)
    }
]

# 随机 UA
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (Linux; Android 10; SM-G970F)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; M2007J17C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36 Xiaomi",
    "Mozilla/5.0 (Linux; Android 10; ELS-AN00 Build/HUAWEIELS-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36 Huawei",
    "Mozilla/5.0 (Linux; Android 10; V1981A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36 Vivo",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SAMSUNG SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/17.0 Chrome/96.0.4664.45 Mobile Safari/537.36"
]

# 📦 从文件读取代理
def load_proxies(filename='valid_proxies.json'):
    proxies = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    proxy = f"{item['type']}://{item['ip']}:{item['port']}"
                    proxies.append(proxy)
        except Exception as e:
            print("读取代理文件失败：", e)
    return proxies

# 🔍 匹配包含关键词
def match_keywords(title, keywords):
    title_cleaned = title.replace(" ", "").lower()
    return all(
        any(k.replace(" ", "").lower() in title_cleaned for k in group)
        for group in keywords
    )

# ❌ 匹配排除关键词
def match_excludes(title, exclude_keywords):
    title_cleaned = title.replace(" ", "").lower()
    return any(
        all(k.replace(" ", "").lower() in title_cleaned for k in group)
        for group in exclude_keywords
    )

# 🌐 请求网页
def get_html(url, proxy_list, max_retries=3):
    for attempt in range(max_retries):
        use_proxy = random.random() < 0.7 and proxy_list
        proxy = random.choice(proxy_list) if use_proxy else None
        proxies = {"http": proxy, "https": proxy} if proxy else None
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            print(f"[请求尝试 {attempt + 1}] 使用代理：{bool(proxy)} - {proxy or '直连'}")
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[状态码异常] {response.status_code}")
        except Exception as e:
            print(f"[请求异常] {e}")
        time.sleep(1)
    print("[请求失败] 多次重试后放弃。")
    return None

# 🕸 主爬虫逻辑
def crawl_smzdm():
    #https://www.smzdm.com/jingxuan/p2/  表示第二页
    url = "https://www.smzdm.com/jingxuan/"
    proxy_list = None
    #proxy_list = load_proxies()
    html = get_html(url, proxy_list)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    li_tags = soup.find_all("li", class_="J_feed_za feed-row-wide")
    if not li_tags:
        print("未找到 li 标签 (class=J_feed_za feed-row-wide)")
        return []

    results = []
    for li in li_tags:
        content_div = li.find("div", class_="z-feed-content")
        if not content_div:
            print("未找到 div 标签 (class=z-feed-content)")
            continue

        # 获取标题 + 链接
        h5 = content_div.find("h5", class_="feed-block-title")
        if not h5:
            print("未找到 h5 标签 (class=feed-block-title)")
            continue
        title_a = h5.find("a")
        if not title_a:
            print("未找到标题 a 标签 (class=feed-block-title 下)")
            continue
        title = title_a.get_text(strip=True)
        href = title_a.get("href", "")

        # 获取价格
        price_a = content_div.find("a", class_="z-highlight")
        if not price_a:
            print("未找到价格 a 标签 (class=z-highlight)")
            continue
        price_str = price_a.get_text(strip=True).replace("￥", "").replace(",", "")
        try:
            price = float(''.join(c for c in price_str if c.isdigit() or c == '.'))
        except Exception as e:
            print(f"价格转换失败：{price_str} - 错误：{e}")
            continue

        # 获取“值”
        zhi_a = content_div.find("a", class_="J_zhi_like_fav price-btn-up")
        zhiV = None
        if zhi_a:
            zhi_span = zhi_a.find("span", class_="unvoted-wrap")
            if zhi_span and zhi_span.span:
                zhiV = zhi_span.span.get_text(strip=True)
            else:
                print("未找到 span 值标签 (class=unvoted-wrap)")
        else:
            print("未找到 a 标签 (class=J_zhi_like_fav price-btn-up)")

        # 获取“不值”
        buzhi_a = content_div.find("a", class_="J_zhi_like_fav price-btn-down")
        buzhiV = None
        if buzhi_a:
            buzhi_span = buzhi_a.find("span", class_="unvoted-wrap")
            if buzhi_span and buzhi_span.span:
                buzhiV = buzhi_span.span.get_text(strip=True)
            else:
                print("未找到 span 不值标签 (class=unvoted-wrap)")
        else:
            print("未找到 a 标签 (class=J_zhi_like_fav price-btn-down)")

        # 关键词匹配
        matched = False
        for rule in whitekeylist:
            if match_keywords(title, rule["keywords"]) and not match_excludes(title, rule.get("exclude_keywords", [])):
                min_p, max_p = rule.get("price_range", (0, float('inf')))
                if min_p <= price <= max_p:
                    matched = True
                    break
        if not matched:
            continue

        item = {
            "title": title,
            "href": href,
            "price": str(price),
            "zhi": zhiV,
            "buzhi": buzhiV
        }
        results.append(item)

    return results

# ✅ 启动入口
if __name__ == '__main__':
    product_data = crawl_smzdm()
    file_manager = kMD5FileManager('smzdmMonitorMD5.txt')
    # 打印所有商品的字典数据
    if product_data:
        print(f"[爬取完成] 获取到 {len(product_data)} 条商品数据:")
        for product in product_data:
            if file_manager.write_md5_with_date(product.get('title', '') + product.get('price', '')):
                notifytxt = f"标题:{product.get('title', '')}\n单价:{product.get('price', '')}\n 链接:{product.get('href', '')}" 
                print(notifytxt)
                kCustomNotify.send_wecom_notification("SMZDM提醒",notifytxt,"WECOM_BOT_GENERALNOTIFY_KEY")
            else:
                pass
                #print("md5 write failed")
    else:
        pass
