import requests
from bs4 import BeautifulSoup
import datetime
import re
import time
import random
from libs.kToolLibs import kMD5FileManager
import kCustomNotify

# 请求头设置
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}

# 代理设置：可以根据实际情况更换或添加更多代理
#proxy_list = [
 #   {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"},
#    {"http": "http://192.168.0.1:1080", "https": "http://192.168.0.1:1080"}
#]
proxy_list = [
]

# 白名单定义
whitekeylist = [
    {
        "keywords": [["苹果","apple","Apple","iPhone"],["16"]],
        "price_range": (3500, 4500)
    },
    {
        "keywords": [["沐浴露"], ["舒肤佳"]],
        "price_range": (0, 10)
    },
    {
        "keywords": [["大米"], ["5kg","10kg"]],
        "price_range": (5, 15)
    },
    
]

# 判断是否匹配白名单和价格范围
def match_white_key_and_price_range(title: str, price_text: str) -> bool:
    """匹配多个关键词组，每组为“或”，组之间为“与”，并且价格在范围内"""
    price_match = re.search(r'(\d+(?:\.\d+)?)', price_text.replace(',', ''))
    if not price_match:
        print(f"[价格提取失败] price_text: {price_text}")
        return False
    price_val = float(price_match.group(1))

    for item in whitekeylist:
        keyword_groups = item.get("keywords", [])
        min_price, max_price = item.get("price_range", (0, float('inf')))

        if min_price <= price_val <= max_price:
            # 所有关键词组都需要满足“至少一个命中”
            if all(any(kw in title for kw in group) for group in keyword_groups):
                return True
    return False

# 获取随机代理或直连
def get_random_proxy():
    # 70%概率使用代理，30%使用直连
    return random.choice(proxy_list) if proxy_list and random.random() < 0.7 else {}

# 爬取页面内容
def crawl_smzdm():
    url = "https://www.smzdm.com/jingxuan/"
    products = []

    max_retries = 5  # 最大重试次数

    for attempt in range(max_retries):
        try:
            # 模拟请求间隔，防止反爬
            time.sleep(random.uniform(1, 3))

            # 随机选择代理或直连
            proxy = get_random_proxy()

            # 发送请求，设置请求头和随机代理
            response = requests.get(url, headers=headers, proxies=proxy, timeout=10)

            if response.status_code != 200:
                print(f"[请求失败] 状态码: {response.status_code}, 尝试次数 {attempt + 1}")
                if attempt < max_retries - 1:
                    print("[重试...]")
                    time.sleep(2)  # 重试前暂停2秒
                    continue
                else:
                    print("[最大重试次数已达]")
                    return products

            print(f"[请求成功] 获取页面内容")
            soup = BeautifulSoup(response.text, "html.parser")
            li_list = soup.find_all("li", class_="J_feed_za feed-row-wide")

            if not li_list:
                print("[未找到符合的li标签] class: J_feed_za feed-row-wide")
                return products


            # 遍历每个li标签
            for li in li_list:
                try:
                    # 获取标题和价格的相关信息
                    feed_content = li.find("div", class_="z-feed-content")
                    if feed_content:
                        title_tag = feed_content.find("h5", class_="feed-block-title").find("a")
                        title = title_tag.get_text(strip=True) if title_tag else None
                        href = title_tag.get("href") if title_tag else None

                        # 输出日志，若没有找到标题
                        if not title:
                            print(f"[未找到标题] class: feed-block-title, 跳过当前li")
                            continue

                        # 获取价格
                        price_tag = feed_content.find("a", class_="z-highlight")
                        price = price_tag.get_text(strip=True) if price_tag else None

                        # 输出日志，若没有找到价格
                        if not price:
                            print(f"[未找到价格] class: z-highlight, 跳过当前li")
                            continue

                        # 检查是否匹配白名单及价格区间
                        if match_white_key_and_price_range(title, price):
                            # 获取值得和不值得的值
                            zhi_tag = feed_content.find("a", class_="J_zhi_like_fav price-btn-up")
                            zhiV = zhi_tag.find("span", class_="unvoted-wrap").find("span").get_text(strip=True) if zhi_tag else None
                            if not zhiV:
                                print(f"[未找到值得] class: J_zhi_like_fav price-btn-up")

                            buzhi_tag = feed_content.find("a", class_="J_zhi_like_fav price-btn-down")
                            buzhiV = buzhi_tag.find("span", class_="unvoted-wrap").find("span").get_text(strip=True) if buzhi_tag else None
                            if not buzhiV:
                                print(f"[未找到不值] class: J_zhi_like_fav price-btn-down")

                            # 存储信息为字典
                            product_info = {
                                "title": title,
                                "price": price,
                                "href": href,
                                "zhi": zhiV,
                                "buzhi": buzhiV
                            }

                            # 将商品信息添加到列表
                            products.append(product_info)

                        else:
                            pass
                            #print("[不符合白名单或价格范围] 跳过当前li")

                    else:
                        print(f"[未找到z-feed-content标签] class: z-feed-content, 跳过当前li")

                except Exception as e:
                    print(f"[处理错误] 错误: {e}, 跳过当前li")

            # 成功获取页面后退出重试循环
            break

        except requests.RequestException as e:
            print(f"[请求异常] 错误: {e}, 尝试次数 {attempt + 1}")
            if attempt < max_retries - 1:
                print("[重试...]")
                time.sleep(2)
                continue
            else:
                print("[最大重试次数已达]")
                break
        except Exception as e:
            print(f"[爬虫异常] 错误: {e}")
            break

    return products

if __name__ == "__main__":
    # 执行爬取任务
    product_data = crawl_smzdm()
    file_manager = kMD5FileManager('smzdmMonitorMD5.txt')
    # 打印所有商品的字典数据
    if product_data:
        #print(f"[爬取完成] 获取到 {len(product_data)} 条商品数据：")
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
        #print("[没有获取到商品数据]")
