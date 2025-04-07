import os
import requests
import kCustomNotify

OIL_API_URL = "https://v3.alapi.cn/api/oil"


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
                line = print(f"92#={item['o92']}元, \n95#={item['o95']}元, \n98#={item['o98']}元, \n0#柴油={item['o0']}元")
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

