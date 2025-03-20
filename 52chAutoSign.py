import requests
import json
import os
import notify

if __name__ == '__main__':
    #从环境变量中获取cookie，请自行设置该环境变量
    cookie = os.getenv("WoAiCH_KEY")
    header = {
        "cookie": cookie,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Origin":"https://www.52ch.net",
        "Host":"www.52ch.net",
        #"Content-Length":"74",
        #"Referer":"https://www.52ch.net/dsu_paulsign-sign.html?needlogin=1&themecolor=F08200",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MAGAPPX|6.4.0-6.4.0-164|iOS 15.4.1 iPhone 12|wachwl|BF204ADF-8D36-4C0E-AE55-D440C9510170|fb534a1a4cb8f3d2dd77b819412a5eea|f3acae52f0d4ac662dba63b38b095d30|9eb96e07f0d1d141cc8f6a34c1bf9613"
    }
    requrl = "https://www.52ch.net/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=0&inajax=0&mobile=2"

    try:
        results = requests.post(requrl, headers=header)
        print(results.text)
        notify.send("52CH", results.text)
    except Exception as e:
        print(e)
        notify.send("52CH", e)

