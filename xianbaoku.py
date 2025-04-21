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

# 多关键词组定义：组内所有关键词都需匹配，组间满足任一组即可匹配（即：组内 and，组间 or）
KEYWORD_GROUPS = [
    ["微信支付立减金"],
    ["visa","一元购"], #多个关键字同时满足
    ["支付有优惠"],
    ["历史最低"],
    ["历史低价"],
    ["bug"]
]

# MD5 记录文件
MD5_FILE = "xianbaokuMD5.txt"

# 获取当前日期
def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# 计算 MD5 值（加上日期，避免每日重复）
def calculate_md5(text):
    today = get_today()
    md5_input = today + text  # 确保每天的 MD5 值不同
    return hashlib.md5(md5_input.encode("utf-8")).hexdigest()

# 读取 MD5 历史记录，同时返回上次日期
def load_md5_history():
    if not os.path.exists(MD5_FILE):
        return set(), None
    
    try:
        with open(MD5_FILE, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
            if not lines:
                return set(), None

            last_date = lines[0]  # 第一行是日期
            md5_set = set(lines[1:])  # 后续行是 MD5 值
            return md5_set, last_date
    except Exception as e:
        print(f"[错误] 读取 MD5 记录失败: {e}")
        return set(), None

# 清空 MD5 文件，写入新的日期
def reset_md5_file():
    try:
        with open(MD5_FILE, "w", encoding="utf-8") as file:
            file.write(get_today() + "\n")  # 写入新日期
    except Exception as e:
        print(f"[错误] 重置 MD5 记录失败: {e}")

# 写入新的 MD5 值，并更新内存中的记录集合
def save_md5_history(md5_hash, md5_history):
    try:
        with open(MD5_FILE, "a", encoding="utf-8") as file:
            file.write(md5_hash + "\n")
        md5_history.add(md5_hash)  # 立即更新，防止重复推送
    except Exception as e:
        print(f"[错误] 写入 MD5 记录失败: {e}")

# 企业微信通知封装
def send_wechat_message(messages):
    if not messages:
        print("没有新的推送内容，不推送")
        return
    
    content = "\n\n".join(messages)
    kCustomNotify.send_wecom_notification("线报酷提醒", content, "WECOM_BOT_GENERALNOTIFY_KEY")

# 判断是否匹配关键词组逻辑（组间 or，组内 and）
def is_keyword_match(text):
    text_lower = text.lower()  # 不区分大小写
    for group in KEYWORD_GROUPS:
        if all(keyword.lower() in text_lower for keyword in group):
            return True
    return False

# 主爬虫逻辑
def scrape_and_notify():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[错误] 无法请求 {URL}: {e}")
        return

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找 class="new-post" 区块下的所有 article-list
        new_post_section = soup.find(class_="new-post")
        if not new_post_section:
            print("未找到 new-post 区块")
            return
        
        article_lists = new_post_section.find_all(class_="article-list")
        if not article_lists:
            print("未找到 article-list")
            return

        # 加载 MD5 历史记录
        md5_history, last_date = load_md5_history()
        today = get_today()

        # 如果日期变化，清空旧记录
        if last_date != today:
            print(f"日期变更（{last_date} -> {today}），清空 MD5 记录")
            reset_md5_file()
            md5_history = set()

        messages = []  # 存储待推送的消息

        # 遍历所有文章列表
        for article_list in article_lists:
            for a_tag in article_list.find_all("a", href=True):
                text = a_tag.get_text().strip()
                link = urljoin(BASE_URL, a_tag["href"])  # 构造完整链接

                # 判断是否匹配关键词组逻辑
                if is_keyword_match(text):
                    message = f"标题: {text} \n链接: {link}"
                    
                    # 计算 MD5 用于去重
                    md5_hash = calculate_md5(message)

                    if md5_hash not in md5_history:
                        messages.append(message)
                        save_md5_history(md5_hash, md5_history)

        # 推送匹配结果
        send_wechat_message(messages)

    except Exception as e:
        print(f"[错误] 解析 HTML 失败: {e}")

# 脚本入口
if __name__ == "__main__":
    try:
        scrape_and_notify()
    except Exception as e:
        print(f"[错误] 脚本运行出错: {e}")
