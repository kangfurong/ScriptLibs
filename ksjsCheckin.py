# -*- coding: utf-8 -*-
"""
name: 快手极速版账号信息版
cron: 40 1 * * *
"""

import os
import requests
import time
import random
import json
import kCustomNotify

# ===== 环境变量 =====
cookie_text = os.getenv("KSJS_COOKIE")

if not cookie_text:
    print("❌ 未设置 KSJS_COOKIE")
    exit(0)

cookies = cookie_text.splitlines()

# ===== 接口 =====
sign_url = "https://nebula.kuaishou.com/rest/wd/encourage/unionTask/signIn/report"
box_url = "https://nebula.kuaishou.com/rest/wd/encourage/unionTask/treasureBox/report"
info_url = "https://nebula.kuaishou.com/rest/wd/encourage/incentive/userInfo"

# ===== UA =====
UA_LIST = [
    "kwai-android/11.3.20 (Linux; Android 11; Redmi K30)",
    "kwai-android/11.0.10 (Linux; Android 10; MI 8)",
    "kwai-android/10.8.30 (Linux; Android 9; ONEPLUS A6000)",
    "kwai-android/11.5.40 (Linux; Android 12; Mi 11)",
]



# ===== 请求头 =====
def build_headers(cookie):
    return {
        "Host": "nebula.kuaishou.com",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": random.choice(UA_LIST),
        "Referer": "https://nebula.kuaishou.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": cookie.strip()
    }

# ===== 请求 =====
def request(url, headers):
    try:
        time.sleep(random.uniform(1.5, 4.5))
        res = requests.get(url, headers=headers, timeout=10)
        return res.text
    except Exception as e:
        return ""

# ===== 获取用户信息 =====
def get_user_info(headers):
    text = request(info_url, headers)

    try:
        data = json.loads(text)

        nickname = data["data"]["user"]["nickname"]
        coin = data["data"]["totalCoin"]
        money = data["data"]["totalCash"]

        return nickname, coin, money
    except:
        return "获取失败", 0, 0

# ===== 执行账号任务 =====
def run(cookie, index):
    headers = build_headers(cookie)

    print(f"\n========== 账号 {index+1} ==========")

    # 获取信息
    nickname, coin, money = get_user_info(headers)
    print("昵称:", nickname)
    print("金币:", coin)
    print("余额:", money)

    # 签到
    sign_res = request(sign_url, headers)
    print("签到:", sign_res)

    time.sleep(random.randint(5, 10))

    # 宝箱
    box_res = request(box_url, headers)
    print("宝箱:", box_res)

    return nickname, coin, money

# ===== 主程序 =====
def main():
    print("🚀 快手任务开始\n")

    msg = "【快手极速版】\n\n"

    for i, ck in enumerate(cookies):
        if ck.strip():
            nickname, coin, money = run(ck, i)

            msg += f"{nickname}\n金币: {coin}\n余额: {money}\n\n"

            wait = random.randint(30, 60)
            print(f"等待 {wait} 秒\n")
            time.sleep(wait)

    print(msg)
    kCustomNotify.send_wecom_notification("快手极速版签到",msg,"WECOM_BOT_GENERALNOTIFY_KEY")

if __name__ == "__main__":
    main()