import os
import requests
import kCustomNotify

OIL_API_URL = "https://v3.alapi.cn/api/oil"

def fetch_tiaojiaorili():
    url = 'https://www.liugeyou.com/tiaojiaorili.html'
    result = []  # 用于保存输出的结果

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误
        response.encoding = 'utf-8'
    except requests.RequestException as e:
        print(f"❌ 网络请求失败：{e}")
        return

    try:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找 intro 区域
        intro_div = soup.find('div', class_='intro')
        if not intro_div:
            print("⚠️ 未找到 class 为 'intro' 的 div 标签。")
            return

        # 找 list_box 区域
        list_box_div = intro_div.find('div', class_='list_box')
        if not list_box_div:
            print("⚠️ 未找到 class 为 'list_box' 的 div 标签。")
            return

        # 提取内容
        list_time_divs = list_box_div.find_all('div', class_='list_time')
        list_text_divs = list_box_div.find_all('div', class_='list_text')

        if not list_time_divs or not list_text_divs:
            print("⚠️ 未找到 class 为 'list_time' 或 'list_text' 的内容。")
            return

        # 将内容格式化并加入结果列表
        for time_div, text_div in zip(list_time_divs, list_text_divs):
            time_text = time_div.get_text(strip=True)
            text_content = text_div.get_text(strip=True)
            result.append(f"下轮调价日: {time_text}\n")
            #result.append(f"下轮调价日: {time_text}\n内容: {text_content}\n")

    except Exception as e:
        print(f"❌ 解析 HTML 出错：{e}")

    return result  # 返回结果
    
def fetch_oil_prices(token, target_province=None):
    params = {
        "token": token
    }

    try:
        response = requests.get(OIL_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("success") and data.get("code") == 200:
            provinces = data["data"]

            print("\n⛽ 今日全国油价信息（部分省份）：\n")

            for item in provinces:
                province = item["province"]
                if target_province and target_province not in province:
                    continue
                line = f"92号:{item['o92']}元, \n95号:{item['o95']}元, \n98号:{item['o98']}元, \n0号柴油:{item['o0']}元"
                line = line + fetch_tiaojiaorili()[0]
                print(line)
                kCustomNotify.send_wecom_notification("今日四川油价",line,"WECOM_BOT_DAILYNOTIFY_KEY")

        else:
            print(f"❌ 获取油价失败：{data.get('message', '未知错误')}")
    except requests.RequestException as e:
        print(f"❌ 网络请求错误（油价）：{e}")

if __name__ == "__main__":
    token = os.getenv("ALAPI_FREE_KEY")
    if not token:
        print("❌ 请设置环境变量 ALAPI_FREE_KEY")
    else:
        fetch_oil_prices(token,"四川")  # 你也可以传入 target_province="北京" 来单独看一个省

