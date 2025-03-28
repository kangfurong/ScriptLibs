import requests
import json
import os

def send_wecom_notification(title, content, env_var_name='WECOM_BOT_DEFAULT_KEY'):
    key = os.getenv(env_var_name)
    
    if not key:
        print(f"环境变量 {env_var_name} 未设置")
        return
    
    url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}'
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # 构造发送的数据
    data = {
        "msgtype": "text",
        "text": {
            "content": f"{title}\n\n{content}"
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200 and response.json().get('errcode') == 0:
            print("企业微信消息发送成功")
        else:
            print(f"企业微信消息发送失败: {response.json()} ")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == '__main__':
    title = "标题测试"
    content = "内容测试"
    env_var_name = 'WECOM_BOT_KEY'
    send_wecom_notification(title, content, env_var_name)
