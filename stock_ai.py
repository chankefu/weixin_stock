#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# #    File: reply_msg.py
# #    Project: Mocha-L/WechatPCAPI 
# #    Author: zzy
# #    mail: elliot.bia.8989@outlook.com
# #    github: https://github.com/elliot-bia
# #    Date: 2019-12-09 14:59:42
# #    LastEditors: zzy
# #    LastEditTime: 2020-01-03 10:03:11
# #    ---------------------------------
# #    Description: 对Mocha-L的WechatPCAPI进行调用,  实现功能: 自动接受的个人信息, 指定群信息发送到指定admin微信, 并且通过回复序列号(空格)信息进行回复


###
# -*- coding: utf-8 -*-
# @Time    : 2019/11/27 23:00
# @Author  : Leon
# @Email   : 1446684220@qq.com
# @File    : test.py
# @Desc    :
# @Software: PyCharm

from WechatPCAPI import WechatPCAPI
import time,datetime
import logging
from queue import Queue
import threading
from funds import fund_analysis
from stock_query import query_reply
from chinese_calendar import is_holiday
import os

with open('./all_stocks.txt') as f:
    stock_data = f.readlines()

logging.basicConfig(level=logging.INFO)
queue_recved_message = Queue()

def stock_exist(in_content,in_type):
    for item in stock_data:
        if in_content in item:
            if in_type=="code" or in_type==1:
                return in_content
            elif in_type=="name" or in_type==2:
                return item[:6]
    return False


def send_set_time():
    now = datetime.datetime.now()
    set_time = ['10:00', '10:30', '11:00', '11:30', '13:30', '14:00', '14:30', '15:00']
    time1_str = datetime.datetime.strftime(now,'%Y-%m-%d %H:%M:%S')[-8:-3]
    if time1_str in set_time and is_holiday(now)==False:
        return True
    else:
        return False



def on_message(message):
    queue_recved_message.put(message)


# 控制台微信
admin_wx = 'wxid_xxx'
# 单人黑名单列表
single_block_list = ['wxid_xxx']  # 最好把控制台微信加进去
# 单人白名单列表
single_receive_list = ['wxid_8uwkc1kqnow522']  #糖吉的微信ID
# 群组接受名单
# group_receive_list = ['17850081755@chatroom']  #预判逻辑交流群号
group_receive_list = ['17208516283@chatroom'] #爱国交流群号
# 创建remark_name字典
dict_remark_name = {}
# 定义信息ID字典
dict_msg_ID = {}
# 全局
ID_num = 0


def deal_remark_name(message):
    ###
    # #    描述: 字典好友信息, 每次启动微信都重新获取一份, 注重remark_name, 其他不管
    # #    description: save wechat's friends message, reload file when wechat start everytime
    # #    param: {message}
    # #    usage:
    # #    return: none
    ###
    wx_id = message.get('data', {}).get('wx_id', '')
    remark_name = message.get('data', {}).get('remark_name', '')
    dict_remark_name[wx_id] = remark_name


# 消息处理 分流
def thread_handle_message(wx_inst):
    global ID_num
    while True:
        message = queue_recved_message.get()
        print(message)
        
        if send_set_time()==True:
            url1='http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:2&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52865676&cb=jQuery1830317240029036183_1585970213997&_=1585970285606'
            bk1="行业板块"
            filepath1 = os.path.join(os.getcwd(),fund_analysis(url1,bk1))
            print(filepath1)
            wx_inst.send_img(to_user=from_chatroom_wxid, img_abspath=filepath1)
            url2= 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:3&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52860548&cb=jQuery183021539183328293965_1585815495642&_=1585816450894'
            bk2="概念板块"
            filepath2 = os.path.join(os.getcwd(),fund_analysis(url2,bk2))
            wx_inst.send_img(to_user=from_chatroom_wxid, img_abspath=filepath2)




        # 坑点: if和elif 慎用

        # 本地保存friends信息, 重点remark_name
        try:
            if 'friend::person' in message.get('type'):
                deal_remark_name(message)
        except:
            pass

        
        # 单人消息
        try:
            if 'msg::single' in message.get('type'):
                # 这里是判断收到的是消息 不是别的响应
                send_or_recv = message.get('data', {}).get('send_or_recv', '')
                # 判断微信id, 黑名单
                from_wxid = message.get('data', {}).get('from_wxid', '')
                data_type = message.get('data', {}).get('data_type', '') 
                if send_or_recv[0] == '0' and from_wxid in single_receive_list:
                    if data_type[0] == '1':
        #                 # 只接受文字
                        msg_content = message.get('data', {}).get('msg', '')
                        if msg_content == "你好":
                            # 设定特定的触发暗语
                            wx_inst.send_text(from_wxid, '哈哈哈')
        except:
            pass


                    # 0是收到的消息 1是发出的 对于1不要再回复了 不然会无限循环回复


        # 接受群组信息
        try: 
            if 'msg::chatroom' in message.get('type'):
                # 这里是判断收到的是消息 不是别的响应
                send_or_recv = message.get('data', {}).get('send_or_recv', '')
                data_type = message.get('data', {}).get('data_type', '') 
                # 判断群组id, 黑名单
                from_chatroom_wxid = message.get(
                    'data', {}).get('from_chatroom_wxid', '')
                if send_or_recv[0] == '0':
                    
                    if from_chatroom_wxid in group_receive_list:
                        if data_type[0] == '1':
                            msg_content = message.get('data', {}).get('msg', '')
                            from_wxid = message.get('data', {}).get('from_member_wxid', '')
                            from_chatroom_wxid = message.get('data', {}).get('from_chatroom_wxid', '')
                            # from_chatroom_nickname = message.get('data', {}).get('from_chatroom_nickname', '')
                            if msg_content[:3]=='@钩子':
                                if msg_content[4:10]=="":
                                    wx_inst.send_text(from_chatroom_wxid, '1、本程序在交易日开盘时间段每隔半小时自动发送行业、概念板块资金主力流向图\n2、自行查询行业、概念板块资金请使用"@糖吉 行业"的格式\n3、查询个股情况请输入“@糖吉 中国平安”的格式')
                                elif msg_content[4:10].replace(" ","")=="行业":
                                    url1='http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:2&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52865676&cb=jQuery1830317240029036183_1585970213997&_=1585970285606'
                                    bk1="行业板块"
                                    filepath1 = os.path.join(os.getcwd(),fund_analysis(url1,bk1))
                                    print(filepath1)
                                    wx_inst.send_img(to_user=from_chatroom_wxid, img_abspath=filepath1)
                                elif msg_content[4:10].replace(" ","")=="概念":
                                    url2= 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:3&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52860548&cb=jQuery183021539183328293965_1585815495642&_=1585816450894'
                                    bk2="概念板块"
                                    filepath2 = os.path.join(os.getcwd(),fund_analysis(url2,bk2))
                                    wx_inst.send_img(to_user=from_chatroom_wxid, img_abspath=filepath2)
                                else:           # msg_content[4:]!="":
                                    # print(msg_content)
                                    #判断是否直接输入了股票代码，是则直接查询
                                    if msg_content[4:10].isdecimal()==True:
                                        stock_code=msg_content[4:10]
                                        if len(stock_code)!=6:
                                            wx_inst.send_text(from_chatroom_wxid, '请输入完整的6位股票代码')
                                        else:
                                            if stock_exist(stock_code,1)!=False:
                                                reply=query_reply(stock_exist(stock_code,1),'f58','f43','f170','f137','f193','f140','f194','f49','f161')
                                                wx_inst.send_text(from_chatroom_wxid, reply)
                                            else:
                                                wx_inst.send_text(from_chatroom_wxid, '输入有误或者不存在该股票')
                                    #输入股票名称则进行转换再查询
                                    else:
                                        if "*ST" in msg_content[4:10]:
                                            stock_name=msg_content[4:9]
                                        else:
                                            stock_name=msg_content[4:8]
                                        stock_name=stock_name.replace(" ","")
                                        if stock_exist(stock_name,2)!=False:
                                            reply=query_reply(stock_exist(stock_name,2),'f58','f43','f170','f137','f193','f140','f194','f49','f161')
                                            wx_inst.send_text(from_chatroom_wxid, reply)
                                        else:
                                            wx_inst.send_text(from_chatroom_wxid, '输入有误或者不存在该股票')
                                       
                                        # for item in stock_data:
                                        #     if stock_name in item:
                                        #         stock_code=item[:6]
                                        #         reply=query_reply(stock_code,'f58','f43','f170','f137','f193','f140','f194','f49','f161')
                                        #         wx_inst.send_text(from_chatroom_wxid, reply)
                                        #         # wx_inst.send_text(from_chatroom_wxid, item[:6])
                                        #         break
                                            # else:
                                            #     wx_inst.send_text(from_chatroom_wxid, '输入有误或者不存在该股票')
                                            #     break
        except:
            pass


def main():
    wx_inst = WechatPCAPI(on_message=on_message, log=logging)
    wx_inst.start_wechat(block=True)

    while not wx_inst.get_myself():
        time.sleep(5)

    print('登陆成功')

    threading.Thread(target=thread_handle_message, args=(wx_inst,)).start()

    time.sleep(10)
    # wx_inst.send_text(to_user=admin_wx, msg='脚本开始')

if __name__ == '__main__':
    main()
