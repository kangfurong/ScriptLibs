# -*- coding: utf-8 -*-
"""
name: 快手极速版多用户版
cron: 20 10 08-23/3 * * *
"""

import os
import sys
import requests
import time
import random
import json
import kCustomNotify
import hashlib
import traceback



# ===== 环境变量 =====
cookie_text = os.getenv("KSJS_COOKIE")

if not cookie_text:
    print("❌ 未设置 KSJS_COOKIE")
    exit(0)

cookies = cookie_text.splitlines()


def get_baoxiang(token, __NS_sig3):
    print('💎💎💎💎开始领取宝箱💎💎💎💎')
    baoxianV = "宝箱:"
    try:
        url = "https://nebula.kuaishou.com/rest/wd/encourage/unionTask/treasureBox/report?__NS_sig3=" + __NS_sig3 + "&sigCatVer=1"

        # 定义请求头
        headers = {
            "Host": "nebula.kuaishou.com",
            "Connection": "keep-alive",
            "Content-Length": "2",
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 23113RKC6C Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.226 KsWebView/1.8.90.675 (rel) Mobile Safari/537.36 Yoda/3.1.7-alpha33-intercept1 ksNebula/12.5.20.8014 OS_PRO_BIT/64 MAX_PHY_MEM/15199 AZPREFIX/az4 ICFO/0 StatusHT/34 TitleHT/43 NetType/WIFI ISLP/0 ISDM/0 ISLB/0 locale/zh-cn DPS/19.822 DPP/99 CT/0 ISLM/0",
            "content-type": "application/json",
            "Accept": "*/*",
            "Origin": "https://nebula.kuaishou.com",
            "X-Requested-With": "com.kuaishou.nebula",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://nebula.kuaishou.com/nebula/task/earning?source=timer&layoutType=4&hyId=nebula_earning",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": token
        }

        # 发送 POST 请求
        resp = requests.post(url, headers=headers, data=json.dumps({}))
        resp_json = resp.json()
        if resp_json['result'] == 1:
            title_reward_count = resp_json['data']['title']['rewardCount']
            baoxianV += f"金币：{title_reward_count}"
        else:
            baoxianV += resp_json['error_msg']
    except:
        baoxianV += f"异常:{traceback.format_exc()}"
        
    print(baoxianV)
    return baoxianV

def get_money(token):
    print('🥰🥰🥰🥰🥰开始获取当前的现金💰️💰️💰️💰️💰️')
    moneyrtn = ''
    try:
        url = "https://nebula.kuaishou.com/rest/n/nebula/activity/earn/overview/basicInfo"

        # 定义请求头
        headers = {
            "Host": "nebula.kuaishou.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 23113RKC6C Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.226 KsWebView/1.8.90.675 (rel) Mobile Safari/537.36 Yoda/3.1.7-alpha33-intercept1 ksNebula/12.5.20.8014 OS_PRO_BIT/64 MAX_PHY_MEM/15199 AZPREFIX/az4 ICFO/0 StatusHT/34 TitleHT/43 NetType/WIFI ISLP/0 ISDM/0 ISLB/0 locale/zh-cn DPS/19.822 DPP/99 CT/0 ISLM/0",
            "content-type": "application/json",
            "Accept": "*/*",
            "X-Requested-With": "com.kuaishou.nebula",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://nebula.kuaishou.com/nebula/task/earning?source=timer&layoutType=4&hyId=nebula_earning",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": token
        }

        # 发送 POST 请求
        resp = requests.get(url, headers=headers)
        
        resp_json = resp.json()
        money = resp_json['data']['allCash']
        coin = resp_json['data']['totalCoin']
        #print(resp_json)
        nickname = resp_json['data']['userData']['nickname']
        
        moneyrtn = f"用户：{nickname}\n余额：{money}\n总金币：{coin}\n"
        print(moneyrtn)
    except:
        print(f"获取异常:{traceback.format_exc()}")

    return moneyrtn


def get_qiandao(token, __NS_sig3):
    print('❤❤❤❤❤开始执行签到❤❤❤❤❤')
    qiandaoV = "签到:"
    try:
        url = "https://nebula.kuaishou.com/rest/wd/encourage/unionTask/signIn/report?__NS_sig3=" + __NS_sig3 + "&sigCatVer=1"

        # 定义请求头
        headers = {
            "Host": "nebula.kuaishou.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; 23113RKC6C Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.226 KsWebView/1.8.90.675 (rel) Mobile Safari/537.36 Yoda/3.1.7-alpha33-intercept1 ksNebula/12.5.20.8014 OS_PRO_BIT/64 MAX_PHY_MEM/15199 AZPREFIX/az4 ICFO/0 StatusHT/34 TitleHT/43 NetType/WIFI ISLP/0 ISDM/0 ISLB/0 locale/zh-cn DPS/19.822 DPP/99 CT/0 ISLM/0",
            "content-type": "application/json",
            "Accept": "*/*",
            "X-Requested-With": "com.kuaishou.nebula",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://nebula.kuaishou.com/nebula/task/earning?source=timer&layoutType=4&hyId=nebula_earning",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": token
        }

        # 发送 POST 请求
        resp = requests.get(url, headers=headers)
        resp_json = resp.json()

        #print(resp.text)

        if resp_json['result'] == 1:
            if 'reportRewardResult' in resp_json['data']:
                title = resp_json['data']['reportRewardResult']['awardToast']['title']
                print(f"{title}")
                bsd1 = resp_json['data']['reportRewardResult']['awardToast']['basicSignInAwardResultShow']['bottomText']
                bsd2 = resp_json['data']['reportRewardResult']['awardToast']['basicSignInAwardResultShow']['bottomText']
                print(f"正常：{bsd1}  额外：{bsd2}")
            elif 'signInUnionSpecialAreaData' in resp_json['data']:
                subtitle = resp_json['data']['signInUnionSpecialAreaData']['subtitle']
                todaySignInAmount = resp_json['data']['signInUnionSpecialAreaData']['todaySignInAmount']
                print(f"{subtitle}")
                print(f"今日签到得到：{todaySignInAmount}元")
                qiandaoV += f"{todaySignInAmount}"
        else:
            qiandaoV += resp_json['error_msg']
    except:
        qiandaoV += f"异常:{traceback.format_exc()}"
    
    print(qiandaoV)
    return  qiandaoV

def gen_tokensig(sig,salt=""):
    v = sig + salt
    return hashlib.sha256(v.encode('utf-8')).hexdigest()

def gen_sig(params,data):
    dd = dict(params,**data)
    dict_sort_res = dict(sorted(dd.items(),key=lambda x:x[0]))
    ss = ""
    for key,value in dict_sort_res.items():
        if key not in ["sig","__NS_sig3","sig2"]:
            ss += f"{key}={value}"
    ss += "ca8e86efb32e"
    return hashlib.md5(ss.encode()).hexdigest()



def execCheckin(cookieitem):
    baoxianRtn = get_baoxiang(cookieitem, "273770408664a7a2ea7b10787f7e62718c6a7e50b5b0f4654b2568686e6e6d6c5373")
    
    qiandaoRtn = get_qiandao(cookieitem, "0b1b5c6c1243e48ec657335453525d3e5ff0b056f69cd8490b5e4444424241407f5f")
    value = get_money(cookieitem)
    value += baoxianRtn
    value += '\n'
    value += qiandaoRtn
    value += '\n\n'
    
    return value
    
    




# ===== 主程序 =====
def main():
    print("🚀 快手任务开始\n")

    msg = "【快手极速版】\n\n"

    for i, ck in enumerate(cookies):
        if ck.strip():
            msg += execCheckin(ck)
            wait = random.randint(30, 60)
            print(f"等待 {wait} 秒\n")
            time.sleep(wait)

    print(msg)
    kCustomNotify.send_wecom_notification("快手极速版签到",msg,"WECOM_BOT_GENERALNOTIFY_KEY")

if __name__ == "__main__":
    main()