import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import hashlib
import notify

# 关键词列表，可外部修改
keywords = ["微信立减金", "支付有优惠", "有礼乐开花", "加油卡","bug","一键价保"]

# 用来存储已存在的 MD5 哈希值
existing_md5_set = set()
# 用来存储计算得到的 MD5 哈希值
calculated_md5_list = []

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
                
                # 判断 title 是否包含关键词列表中的任何一个
                if any(keyword.lower() in title for keyword in keywords):
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
        postheaderV = "title:\r\n"

        if post_head:
            h1_tag = post_head.find('h1')
            if h1_tag:
                postheaderV = postheaderV + h1_tag.get_text(strip=True)
                #print(f"文章标题: {h1_tag.get_text(strip=True)}")
            else:
                print("未找到 h1 标签")
        else:
            print("未找到 class 为 'post-head' 的 div 标签")
        
        # 查找同时满足 class 为 'post-content' 且 id 为 'xbcontent' 的 div 标签
        post_content = soup.find('div', class_='post-content', id='xbcontent')
        postcontentV = "\r\ncontent:\r\n"
        if post_content:
            #print("获取的文章内容:")
            p_tags = post_content.find_all('p')
            
            # 排除最后三个 p 标签，合并其余内容为一个字符串
            if len(p_tags) > 3:
                text = " ".join(p_tag.get_text(strip=True) for p_tag in p_tags[:-3])
                postcontentV = postcontentV + text
                #print(text)
            else:
                print("error:p标签不足3个，请检查content内容")
                text = " ".join(p_tag.get_text(strip=True) for p_tag in p_tags)
                #print(text)
        else:
            print("未找到 class 为 'post-content' 且 id 为 'xbcontent' 的内容")
        
        postdataV = postheaderV + postcontentV
        #print(postdataV)
        
        # 计算 postdataV 的 MD5 哈希
        postdata_md5 = hashlib.md5(postdataV.encode('utf-8')).hexdigest()
        #print(f"MD5 哈希值: {postdata_md5}")
        
        # 将 MD5 哈希值添加到列表
        calculated_md5_list.append(postdata_md5)

        # 如果 MD5 哈希值不在已存在的 MD5 集合中，打印出来
        if not is_md5_exists(postdata_md5):
            #print(f"新的 MD5 哈希值: {postdata_md5}")
            #print(postdataV)
            notify.send("优惠信息", postdataV)

    except requests.exceptions.RequestException as e:
        print(f"获取文章内容时请求错误: {e}")
    except Exception as e:
        print(f"获取文章内容时出错: {e}")

def save_md5_to_file():
    try:
        # 先清空 md5.txt 文件
        with open('md5.txt', 'w', encoding='utf-8') as file:
            pass  # 只打开并清空文件
        
        # 将计算出的 MD5 哈希值批量写入文件
        with open('md5.txt', 'a', encoding='utf-8') as file:
            for md5_hash in calculated_md5_list:
                file.write(md5_hash + '\n')  # 每个MD5哈希值占一行
        print(f"所有 MD5 哈希值已保存到 md5.txt 文件，共写入 {len(calculated_md5_list)} 个 MD5 哈希值")
    
    except Exception as e:
        print(f"保存MD5时出现错误: {e}")

def is_md5_exists(md5_hash):
    # 使用已加载的集合检查 md5 哈希值是否存在
    return md5_hash in existing_md5_set

def load_existing_md5():
    # 从文件按行读取并加载已存在的 MD5 哈希值到集合
    if os.path.exists('md5.txt'):
        with open('md5.txt', 'r', encoding='utf-8') as file:
            for line in file:
                # 按行读取并去除行末的换行符
                existing_md5_set.add(line.strip())  # 去掉换行符并添加到集合

if __name__ == '__main__':
    # 从文件加载已有的 MD5 哈希值
    load_existing_md5()
    
    # 从环境变量获取 URL，默认值是示例链接
    url = os.getenv('ZKBWEB_KEY', 'http://www.baidu.com')
    fetch_and_check_links(url)
    
    # 所有链接处理完毕后，统一将计算的 MD5 保存到文件
    save_md5_to_file()
