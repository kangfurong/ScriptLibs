import os
import requests
import kCustomNotify

API_URL = "https://v3.alapi.cn/api/zaobao"

def fetch_zaobao():
    # 从环境变量中获取 Token
    token = os.getenv("ALAPI_NEWS_KEY")

    if not token:
        print("❌ 未设置环境变量 ALAPI_NEWS_KEY，请先设置 token。")
        return

    params = {
        "token": token,
        "format": "json"
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("success") and data.get("code") == 200:
            zaobao = data["data"]
            news_combined = "\n".join(zaobao["news"])

            #print(f"\n📅 日期：{zaobao['date']}")
            #print("\n📰 今日早报（合并内容）：\n")
            print(news_combined)
            kCustomNotify.send_wecom_notification("今日早报",news_combined,"WECOM_BOT_DAILYNOTIFY_KEY")
            #print("\n💬 微语：", zaobao["weiyu"])
            #print("\n🖼️ 图片链接：", zaobao["image"])
            #print("🔊 音频链接：", zaobao["audio"])
        else:
            print(f"❌ 获取早报失败：{data.get('message', '未知错误')}")
    except requests.RequestException as e:
        print(f"❌ 网络请求错误：{e}")

if __name__ == "__main__":
    fetch_zaobao()
