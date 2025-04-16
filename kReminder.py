import hashlib
from datetime import datetime, timedelta
#import notify
import kCustomNotify

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
        #每天都要提醒的任务放在这里
        '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31':{
            '08:00':['和包APP,用邮政银行储蓄卡充值余额（有礼乐开花）'],
            '23:50':['微信小程序,乐惠畅玩-使用20元景区立减券',]
        },

        '1,11,21':{
            '09:50':['招商银行APP-会员-领取黄金（10点）',],
        },
        
        '8,18,28': {
            '17:30': ['电信APP-四川服务-精选月月选权益', ], 
             '18:00': [],
        },

        '9,19,29': {
            '09:50': ['邮政储蓄APP-权益专区-星级礼遇',], 
             '18:00': [],
        },
        
        '1': {
            '17:30': ['云闪付APP-会员权益-信用卡还款', '电信APP-四川服务-领取流量','支付宝积分兑换话费券-用电信APP充值-选择支付宝支付','农业银行-信用卡-天天返现报名',
                     '平安口袋银行-信用卡-我的积分-积分报名','微信信用卡还款-我的-惠用卡-领还款额度'],
            '20:00':['成都农商银行APP-成长等级-领取微信立减金','12580每天惠小程序-本地专区-兑红旗券',],     
        },
        '2':{
            '20:00':['中国移动APP-权益-领取乐惠畅玩流量','电信APP-四川服务-精选月月选权益','微信小程序-和悦乐惠-盒马券','微信小程序-12580惠生活-红旗连锁券','vx-交行小程序-美好集盒支付券',],
        },
        '7':{
            '20:00':['平安口袋银行-好车主白金卡畅享权益'],
        },
        '10':{
            '17:50':['中国建设银行-财富会员-领达标礼'],
        },
        '15':{
            '20:00':['平安好车主-每月会员权益领取'],
        },
        '16':{
            '11:50':['支付宝-搜索数币节-领数币红包'],
        },
        #用于每月最后几天，检查是否有任务未执行
        '27':{
            '09:50':['邮储信用卡APP-惠生活-蜜雪冰城-领券',],
            '18:00':['中国移动-铂金会员是否领取完毕','平安口袋银行-积分是否过期','微信小程序,乐惠畅玩-券是否已全部使用',],
        },
    }

    # 预定义星期几对应的时间和输出文本
    week_message_dict = {
        'Monday': {
            '09:40': ['领取云闪付-有礼乐开花奖励！','成都农商银行-新春周周礼','农行APP-生活-下滑茶饮优惠享(10点)',],
        },
        'Tuesday': {
            '07:50': ['农业银行APP-我的-星级权益（8点，月1次）',],
            '09:50': ['翼支付APP-权益-权益商城-月月领券（10点，月1次）',],
            '18:00': [],
        },
        'Wednesday': {
            '09:50': ['和包APP-领取金融券','中国移动云盘-活动中心-惊喜福利（微信立减金）','招商银行-生活-饭票-抢五折（十点）',],
        },
        'Thursday': {
            '08:50':['工行E生活APP-20积分抽立减金(9点)',],
            '09:55': ['平安银行-周四开盲盒','邮储银行-周四开盲盒',],
            '19:00': [],
        },
        'Friday': {
            '09:50': ['中国移动APP-权益-周五喝一杯（十点）','成都银行APP-我的-粉丝福利季（十点）','12580惠生活-红旗券是否使用完毕','平安口袋银行-金橙福利社（抽奖）',],
        },
        'Saturday': {
            '09:45': ['10点-邮政工会信用卡-200减40油卡'],
            '18:00': ['邮政信用卡APP-付款-20减6（月3次）','平安银行-我的-支付会员-我的会员权益（领立减金）'],
        },
        'Sunday': {
            '08:55':["邮储银行-搜索天天秒杀-领VX立减金(月1次)",],
            '18:00': ['检查vx-支付有优惠金币','CCB-任务中心-开宝盒（可充E卡）',],
        }
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
        notifytxt = "\n".join(messages_to_output)
        print(notifytxt)
        kCustomNotify.send_wecom_notification("定时提醒",notifytxt,"WECOM_BOT_GENERALNOTIFY_KEY")
        #notify.send("定时提醒", notifytxt)

    # 如果有新的MD5值，统一追加到文件中
    if new_md5s:
        append_new_md5s(new_md5s)

if __name__ == "__main__":
    main()

