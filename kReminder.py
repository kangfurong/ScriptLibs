import hashlib
from datetime import datetime, timedelta
import notify

def check_and_update_date():
    try:
        # 获取当前日期
        current_date = datetime.now()
        current_date_str = current_date.strftime('%Y-%m-%d')

        # 从文件读取日期
        with open('notifyDateRec.txt', 'r') as file:
            file_date = file.read().strip()

        # 如果文件中的日期与当前日期不一致，清空文件并写入当前日期
        if file_date != current_date_str:
            # 清空 notifyMD5Rec.txt 文件
            with open('notifyMD5Rec.txt', 'w') as md5_file:
                md5_file.truncate(0)  # 清空文件
            print(f"日期不一致，已清空 notifyMD5Rec.txt 文件并更新为 {current_date_str}")
            
            # 更新 notifyDateRec.txt 文件
            with open('notifyDateRec.txt', 'w') as file:
                file.write(current_date_str)
            print(f"已更新 notifyDateRec.txt 文件为 {current_date_str}")

        return current_date_str
    
    except FileNotFoundError:
        # 如果文件不存在，则创建并写入当前日期
        with open('notifyDateRec.txt', 'w') as file:
            file.write(current_date_str)
        print(f"notifyDateRec.txt 文件不存在，已创建并写入当前日期 {current_date_str}")
        
        # 如果 notifyMD5Rec.txt 文件也不存在，创建空文件
        with open('notifyMD5Rec.txt', 'w') as md5_file:
            pass
        
        return current_date_str

def calculate_md5(date, time, weekday, message):
    """计算由日期、时间、星期和消息组成的MD5值"""
    # 拼接字符串：当前日期 + 当前时间 + 当前星期 + 消息
    md5_input = f"{date} {time} {weekday} {message}"
    md5 = hashlib.md5()
    md5.update(md5_input.encode('utf-8'))
    return md5.hexdigest()

def load_existing_md5():
    """加载notifyMD5Rec.txt中的现有MD5记录"""
    try:
        with open('notifyMD5Rec.txt', 'r') as file:
            md5_records = file.readlines()
        return set(md5.strip() for md5 in md5_records)
    except FileNotFoundError:
        # 如果文件不存在，返回一个空集合
        return set()

def append_new_md5s(new_md5s):
    """将新的MD5值批量追加到notifyMD5Rec.txt文件中"""
    with open('notifyMD5Rec.txt', 'a') as file:
        for md5 in new_md5s:
            file.write(md5 + '\n')
    print(f"已将 {len(new_md5s)} 个新的MD5值追加到文件。")

def print_message_by_day_or_week(message_dict, week_message_dict, current_date_str, existing_md5):
    new_md5s = []  # 存储待写入文件的新MD5值
    messages_to_output = []  # 用于存储需要输出的消息
    try:
        # 获取当前日期和时间
        current_date = datetime.now()
        day = current_date.day
        current_time = current_date.strftime('%H:%M')  # 当前时间（小时:分钟）
        weekday = current_date.strftime('%A')  # 当前星期几（如 Monday, Tuesday）

        # 获取当前日期号数对应的日期
        year = current_date.year
        month = current_date.month
        input_datetime = datetime(year, month, day)

        # 查找字典中对应的日期号数（按日期查找）
        date_str = input_datetime.strftime('%Y-%m-%d')

        # 先按号数（日期）查找
        for key in message_dict:
            # 将key转为整数列表，支持类似 "8,18,28"
            days = [int(x) for x in key.split(',')]
            if day in days:
                messages = message_dict[key]
                for time, message_list in messages.items():
                    # 将字典中的时间转换为 datetime 格式以进行比较
                    time_obj = datetime.strptime(time, '%H:%M').replace(year=year, month=month, day=day)
                    time_diff = abs(current_date - time_obj)

                    # 判断当前时间与字典中的时间差是否在6分钟以内
                    if time_diff <= timedelta(minutes=6):
                        for message in message_list:
                            #messages_to_output.append(f"日期: {date_str} 时间: {time} - {message}")
                            # 计算文本的MD5值并检查
                            calculated_md5 = calculate_md5(date_str, time, weekday, message)
                        
                            # 如果MD5值不在现有的MD5记录中，添加到新MD5集合
                            if calculated_md5 not in existing_md5:
                                messages_to_output.append(f"- {message}")
                                new_md5s.append(calculated_md5)

        # 按星期几查找
        if weekday in week_message_dict:
            messages = week_message_dict[weekday]
            for time, message_list in messages.items():
                # 将字典中的时间转换为 datetime 格式以进行比较
                time_obj = datetime.strptime(time, '%H:%M').replace(year=year, month=month, day=day)
                time_diff = abs(current_date - time_obj)

                # 判断当前时间与字典中的时间差是否在6分钟以内
                if time_diff <= timedelta(minutes=6):
                    for message in message_list:
                        #messages_to_output.append(f"星期: {weekday} 时间: {time} - {message}")
                        
                        # 计算文本的MD5值并检查
                        calculated_md5 = calculate_md5(date_str, time, weekday, message)
                        
                        # 如果MD5值不在现有的MD5记录中，添加到新MD5集合
                        if calculated_md5 not in existing_md5:
                            messages_to_output.append(f"- {message}")
                            new_md5s.append(calculated_md5)

        else:
            print(f"{date_str} 或 {weekday} - 没有找到对应的输出文本。")
    
    except ValueError as e:
        print(f"错误: {e}，请检查日期号数的输入。")

    return new_md5s, messages_to_output

def main():
    # 预定义日期号数对应的时间和输出文本
    day_message_dict = {
        8,18,28: {'17:30': ['电信APP-四川服务-精选月月选权益', ], 
             '18:00': []},
        1: {'17:30': ['云闪付APP-会员权益-信用卡还款', '电信APP-四川服务-领取流量'],
            '20:00':[''],},
        2:{'20:00':['中国移动APP-权益-领取乐惠畅玩流量','电信APP-四川服务-精选月月选权益','微信小程序-和悦乐惠-盒马券','微信小程序-12580惠生活-红旗连锁券']},
        7:{'20:00':['平安口袋银行-好车主白金卡畅享权益']},
        15:{'20:00':['平安好车主-每月会员权益领取']}
    }

    # 预定义星期几对应的时间和输出文本
    week_message_dict = {
        'Monday': {'09:40': ['检查云闪付-有礼乐开花！',],
                   },
        'Tuesday': {'08:00': ['微信小程序-京东有礼-E卡-云闪付5减1'],
                    '18:00': []},
        'Wednesday': {'08:30': [''],
                      '15:00': ['']},
        'Thursday': {'09:55': ['平安银行-周四开盲盒',],
                     '17:30': []},
        'Friday': {'09:30': [],
                   '14:00': []},
        'Saturday': {'09:45': ['10点-邮政工会信用卡-200减40油卡'],
                     '07:00': ['微信小程序-京东有礼-E卡-云闪付5减1',]},
        'Sunday': {'08:00': [],
                   '16:00': []}
    }

    # 检查并更新文件中的日期
    current_date_str = check_and_update_date()

    # 加载已存在的MD5值
    existing_md5 = load_existing_md5()

    # 自动获取当前日期并查询对应的输出文本
    new_md5s, messages_to_output = print_message_by_day_or_week(day_message_dict, week_message_dict, current_date_str, existing_md5)

    # 输出合并的消息文本
    if messages_to_output:
        print("\n--- 输出的消息 ---")
        print("\n".join(messages_to_output))
        notify.send("定时提醒", messages_to_output)

    # 如果有新的MD5值，统一追加到文件中
    if new_md5s:
        append_new_md5s(new_md5s)

if __name__ == "__main__":
    main()

