# -*- coding: utf-8 -*-
"""
name: 快手极速版多账号真实请求版
cron: 30 1 * * *
"""

import os
import requests
import time
import random

# ========= 环境变量 =========
cookie_text = os.getenv("KSJS_COOKIE")
QYWX_KEY = os.getenv("QYWX_KEY")

if not cookie_text:
    print("❌ 未设置 KS_COOKIE")
    exit(0)

cookies = cookie_text.splitlines()

# ========= 接口 =========
sign_url = "https://nebula.kuaishou.com/rest/wd/encourage/unionTask/signIn/report"
box_url = "https://nebula.kuaishou.com/rest/wd/encourage/unionTask/treasureBox/report"

# ========= 随机UA =========
UA_LIST = [
    "kwai-android/11.3.20 (Linux; Android 11; Redmi K30)",
    "kwai-android/11.0.10 (Linux; Android 10; MI 8)",
    "kwai-android/10.8.30 (Linux; Android 9; ONEPLUS A6000)",
    "kwai-android/11.5.40 (Linux; Android 12; Mi 11)",
]

# ========= 企业微信推送 =========
def send_qywx(msg):
    if not QYWX_KEY:
        print("⚠️ 未配置企业微信推送")
        return

    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_KEY}"

    data = {
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }

    try:
        requests.post(url, json=data)
    except Exception as e:
        print("推送失败:", e)

# ========= 构造真实请求头 =========
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

# ========= 请求 =========
def request(url, headers):
    try:
        time.sleep(random.uniform(1.5, 4.5))
        res = requests.get(url, headers=headers, timeout=10)
        return res.text
    except Exception as e:
        return f"请求失败: {e}"

# ========= 判断Cookie =========
def check_cookie(text):
    if "未登录" in text or "error" in text:
        return False
    return True

# ========= 单账号执行 =========
def run(cookie, index):
    headers = build_headers(cookie)

    print(f"\n========== 👤 账号 {index+1} ==========")

    sign_res = request(sign_url, headers)
    print("📅 签到结果:", sign_res)

    valid = check_cookie(sign_res)

    time.sleep(random.randint(5, 10))

    box_res = request(box_url, headers)
    print("🎁 宝箱结果:", box_res)

    return valid

# ========= 主程序 =========
def main():
    print("🚀 快手极速版任务开始\n")

    ok_list = []
    fail_list = []

    for i, ck in enumerate(cookies):
        if ck.strip():
            valid = run(ck, i)

            if valid:
                ok_list.append(f"账号{i+1} 正常")
            else:
                fail_list.append(f"账号{i+1} Cookie失效")

            wait = random.randint(30, 60)
            print(f"⏳ 等待 {wait} 秒进入下一个账号\n")
            time.sleep(wait)

    # ========= 汇总 =========
    msg = "【快手极速版任务结果】\n\n"

    if ok_list:
        msg += "正常账号：\n" + "\n".join(ok_list) + "\n\n"

    if fail_list:
        msg += "失效账号：\n" + "\n".join(fail_list) + "\n\n"

    print(msg)
    send_qywx(msg)

if __name__ == "__main__":
    main()