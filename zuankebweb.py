import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import hashlib
# import notify
import kCustomNotify

# 关键词组合列表：每组内关键词需全部匹配，任意一组匹配即可
keywords = [
    ["微信立减金"],
    ["支付有优惠"],
    ["有礼乐开花"],
    ["加油卡"],
    ["一元购","visa"], #必须同时满足
    ["bug"],
    ["一键价保"],
    ["金币兑换"],
    ["百度地图打车"],
    ["爱购8.8"],
    ["历史最低"],
]

# 用来存储已存在的 MD5 哈希值
existing_md5_set = set()
# 用来存储计算得到的 MD5 哈希值
calculated_md5_list = []

def is_match_keywords(title, keyword_groups):
    """
    检查标题是否匹配任意一组关键词组合
    每组关键词中的所有词都必须出现在 title 中
    """
    title = title.lower()
    for group in keyword_groups:
        if all(keyword.lower() in title for keyword in group):
            return True
    return False

def fetch_and_check_links(url):
    try:
        # 创建新的变量，不改变传入参数的 url 值
        target_url = urljoin(url, '/list-1-0.html')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有 class 为 'list-group' 且 id 为 'redtag' 的 div 标签
        divs = soup.find_all('div', class_='list-group', id='redtag')

        for div in divs:
            # 查找 div 下的所有 a 标签
            a_tags = div.find_all('a')
            for a_tag in a_tags:
                title = a_tag.get('title', '').lower()  # 小写化标题进行匹配
                href = a_tag.get('href', '')

                # 判断 title 是否匹配任意一组关键词组合
                if is_match_keywords(title, keywords):
                    full_url = urljoin(url, href)  # 使用原始 URL 处理相对路径
                    print(f"符合条件的链接: {title} -> {full_url}")
                    if full_url:
                        fetch_post_content(full_url)
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"出现未知错误: {e}")

def fetch_post_content(post_url):
    try:
        response = requests.get(post_url)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找 class 为 'post-head' 的 div 标签并获取其下的 h1 标签
        post_head = soup.find('div', class_='post-head')
        postheaderV = "标题:\n"

        if post_head:
            h1_tag = post_head.find('h1')
            if h1_tag:
                postheaderV += h1_tag.get_text(strip=True)
            else:
                print("未找到 h1 标签")
        else:
            print("未找到 class 为 'post-head' 的 div 标签")

        # 查找同时满足 class 为 'post-content' 且 id 为 'xbcontent' 的 div 标签
        post_content = soup.find('div', class_='post-content', id='xbcontent')
        postcontentV = "\r\n正文:\n"
        if post_content:
            # 获取所有 p 标签内容（去除最后3个）
            p_tags = post_content.find_all('p')
            if len(p_tags) > 3:
                text = " ".join(p_tag.get_text(strip=True) for p_tag in p_tags[:-3])
                postcontentV += text
            else:
                print("error:p标签不足3个，请检查content内容")
                text = " ".join(p_tag.get_text(strip=True) for p_tag in p_tags)
                postcontentV += text
        else:
            print("未找到 class 为 'post-content' 且 id 为 'xbcontent' 的内容")

        postdataV = postheaderV + postcontentV

        # 计算 postdataV 的 MD5 哈希
        postdata_md5 = hashlib.md5(postdataV.encode('utf-8')).hexdigest()

        # 将 MD5 哈希值添加到列表
        calculated_md5_list.append(postdata_md5)

        # 如果是新的内容（MD5未存在），则发送通知
        if not is_md5_exists(postdata_md5):
            kCustomNotify.send_wecom_notification("0818提醒", postdataV, "WECOM_BOT_GENERALNOTIFY_KEY")

    except requests.exceptions.RequestException as e:
        print(f"获取文章内容时请求错误: {e}")
    except Exception as e:
        print(f"获取文章内容时出错: {e}")

def save_md5_to_file():
    try:
        # 先清空 md5.txt 文件
        with open('zuankebwebmd5.txt', 'w', encoding='utf-8') as file:
            pass  # 只打开并清空文件

        # 将计算出的 MD5 哈希值批量写入文件
        with open('zuankebwebmd5.txt', 'a', encoding='utf-8') as file:
            for md5_hash in calculated_md5_list:
                file.write(md5_hash + '\n')  # 每个MD5哈希值占一行
        print(f"所有 MD5 哈希值已保存到 zuankebwebmd5.txt 文件，共写入 {len(calculated_md5_list)} 个 MD5 哈希值")

    except Exception as e:
        print(f"保存MD5时出现错误: {e}")

def is_md5_exists(md5_hash):
    # 使用已加载的集合检查 md5 哈希值是否存在
    return md5_hash in existing_md5_set

def load_existing_md5():
    # 从文件按行读取并加载已存在的 MD5 哈希值到集合
    if os.path.exists('zuankebwebmd5.txt'):
        with open('zuankebwebmd5.txt', 'r', encoding='utf-8') as file:
            for line in file:
                existing_md5_set.add(line.strip())

if __name__ == '__main__':
    # 从文件加载已有的 MD5 哈希值
    load_existing_md5()

    # 从环境变量获取 URL，默认值是示例链接
    url = os.getenv('ZKBWEB_KEY', 'http://www.baidu.com')
    fetch_and_check_links(url)

    # 所有链接处理完毕后，统一将计算的 MD5 保存到文件
    save_md5_to_file()
