import os
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import kCustomNotify

# 从环境变量读取 BASE_URL，如果不存在，使用默认值
BASE_URL = os.getenv("BASE_URL_KEY", "https://new.xianbao.fun/")
URL = BASE_URL

# 关键词
KEYWORDS = ["微信支付立减金", "支付有优惠",'历史最低','bug']

# MD5 记录文件
MD5_FILE = "xianbaokuMD5.txt"

# 获取当前日期
def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# 计算 MD5
def calculate_md5(text):
    today = get_today()
    md5_input = today + text  # 确保每天的 MD5 值不同
    return hashlib.md5(md5_input.encode("utf-8")).hexdigest()

# 读取 MD5 记录，同时检查日期
def load_md5_history():
    if not os.path.exists(MD5_FILE):
        return set(), None
    
    try:
        with open(MD5_FILE, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
            if not lines:
                return set(), None

            last_date = lines[0]  # 取第一行作为日期
            md5_set = set(lines[1:])  # 取剩余行作为 MD5 记录
            return md5_set, last_date
    except Exception as e:
        print(f"[错误] 读取 MD5 记录失败: {e}")
        return set(), None

# 清空 MD5 记录并写入新日期
def reset_md5_file():
    try:
        with open(MD5_FILE, "w", encoding="utf-8") as file:
            file.write(get_today() + "\n")  # 先写入日期
    except Exception as e:
        print(f"[错误] 重置 MD5 记录失败: {e}")

# 追加新 MD5 记录，同时更新 md5_history，避免重复推送
def save_md5_history(md5_hash, md5_history):
    try:
        with open(MD5_FILE, "a", encoding="utf-8") as file:
            file.write(md5_hash + "\n")
        md5_history.add(md5_hash)  # 立即更新 md5_history，防止重复推送
    except Exception as e:
        print(f"[错误] 写入 MD5 记录失败: {e}")

# 发送企业微信通知
def send_wechat_message(messages):
    if not messages:
        print("没有新的推送内容，不推送")
        return
    
    content = "\n\n".join(messages)  # 合并多条消息
    kCustomNotify.send_wecom_notification("线报提醒",content,"WECOM_BOT_GENERALNOTIFY_KEY")

# 爬取并解析网页
def scrape_and_notify():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()  # 处理 HTTP 错误（404、500 等）
    except requests.exceptions.RequestException as e:
        print(f"[错误] 无法请求 {URL}: {e}")
        return

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找 class="new-post" 里的所有 article-list
        new_post_section = soup.find(class_="new-post")
        if not new_post_section:
            print("未找到 new-post 区块")
            return
        
        article_lists = new_post_section.find_all(class_="article-list")
        if not article_lists:
            print("未找到 article-list")
            return

        # 读取 MD5 记录
        md5_history, last_date = load_md5_history()
        today = get_today()

        # 如果日期变了，清空 MD5 文件
        if last_date != today:
            print(f"日期变更（{last_date} -> {today}），清空 MD5 记录")
            reset_md5_file()
            md5_history = set()  # 清空 MD5 记录

        messages = []  # 存储待推送的消息

        # 遍历所有 article-list
        for article_list in article_lists:
            for a_tag in article_list.find_all("a", href=True):
                text = a_tag.get_text().strip()
                link = urljoin(BASE_URL, a_tag["href"])  # 转换为绝对路径

                # 判断是否包含指定关键词
                if any(keyword in text for keyword in KEYWORDS):
                    message = f"标题: {text} \n链接: {link}"
                    
                    # 计算当前消息的 MD5
                    md5_hash = calculate_md5(message)

                    # 检查 MD5 是否已存在
                    if md5_hash not in md5_history:
                        messages.append(message)
                        save_md5_history(md5_hash, md5_history)  # 立即更新 md5_history，避免重复发送

        # 发送通知（批量推送）
        send_wechat_message(messages)

    except Exception as e:
        print(f"[错误] 解析 HTML 失败: {e}")

# 执行爬取和通知
if __name__ == "__main__":
    try:
        scrape_and_notify()
    except Exception as e:
        print(f"[错误] 脚本运行出错: {e}")
