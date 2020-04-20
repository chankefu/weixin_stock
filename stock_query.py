#个股行情查询

import json
import re
from urllib.request import urlopen
import datetime
from chinese_calendar import is_holiday

#判断是否交易日函数
def workday(input_datetime):
    while is_holiday(input_datetime):
        input_datetime = input_datetime - datetime.timedelta(days=1)
    return input_datetime

#判断是否开盘时间，否则返回最近一个交易时间段的最后时间点
def tradetime(input_datetime):
    current = workday(input_datetime)
    # print(current)
    d_time = datetime.datetime.strptime(str(current.date())+'9:30', '%Y-%m-%d%H:%M')
    d_time1 = datetime.datetime.strptime(str(current.date())+'11:30', '%Y-%m-%d%H:%M')
    d_time2 = datetime.datetime.strptime(str(current.date())+'13:00', '%Y-%m-%d%H:%M')
    d_time3 = datetime.datetime.strptime(str(current.date())+'15:00', '%Y-%m-%d%H:%M')
    if current != input_datetime:
        current = datetime.datetime.strptime(str(current.date())+'15:00', '%Y-%m-%d%H:%M')
    elif current < d_time:
        current = current - datetime.timedelta(days=1)
        current = workday(current)
        current = datetime.datetime.strptime(str(current.date())+'15:00', '%Y-%m-%d%H:%M')
    elif d_time1 < current < d_time2:
        current = datetime.datetime.strptime(str(current.date())+'11:30', '%Y-%m-%d%H:%M')
    elif current > d_time3:
        current = datetime.datetime.strptime(str(current.date())+'15:00', '%Y-%m-%d%H:%M')
    # elif current 
    return current



# def crab_data(url,title):
#     response = urlopen(url)
#     html = response.read().decode();
#     print(html)
#     #设置标题
#     data_time = tradetime(datetime.datetime.now())
#     data_title=data_time.strftime("%Y{y}%m{m}%d{d}%H{h}%M{M}").format(y = "年",m = "月",d = "日",h = "时",M = "分")+title+"数据抓取结果"
#     with open(f'{data_title}.txt','w') as data_file:
#         data_file.write(html)
#     print(f'已经生成{data_title}')
#     return html

#处理网页返回的jQuery格式的数据，转换为多维数组（自定义）。注意，输入参数应该为用decode()解码后的网页数据，否则报错。
#*args的参数输入为用,号隔开的多个字符串，如'f14','f62','f66','f69','f124','f184','f204'
def stock_deal_data(data, *args):
    pattern = re.compile(r'.*?data\":({.*?})}')
    temp_data = re.match(pattern, data).group(1)
    datas = json.loads(temp_data)
    value = []
    for arg in args:
        value.append(datas[arg])
    return value


def url_build(stock_code):
    if stock_code[:1]=="6":
        code_id=f'1.{stock_code}'   #深市股票用0表示，沪市股票用1表示？
    elif stock_code[:1]=="3" or stock_code[:1]=="0":
        code_id=f'0.{stock_code}'
    fixed_url=f'http://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&invt=2&fltt=2&fields=f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196,f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287&secid={code_id}&cb=jQuery1124045031730971081374_1586764278775&_=1586764278819'
    return fixed_url


def query_reply(stock_code,*args):
    if datetime.datetime.now()!=workday(datetime.datetime.now()):
        tips="温馨提醒：当前不是交易日，查询结果为上一个收盘日的数据：\n"
    else:
        tips="查询结果如下：\n"
    response = urlopen(url_build(stock_code))
    html = response.read().decode();
    # print(html)
    result=stock_deal_data(html,*args)
    reply=f'{tips}{result[0]},当前股价{result[1]},当前涨幅{result[2]}%，\n主力净流入{round(result[3]/100000000,2)}亿元，主力净占比{result[4]}%，\n超大单净流入{round(result[5]/100000000,2)}亿元，超大单净占比{result[6]}%，\n当前外盘为{round(result[7]/10000,2)}万手，内盘为{round(result[8]/10000,2)}万手'
    return reply


if __name__ == '__main__':
    #行业板块
    #短数据链接
    # url = 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&fields=f12,f13,f14,f62&fid=f62&fs=m:90+t:2&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18305065465637410975_1585815026465&_=1585816040642'
    #长数据链接
    # url='http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:2&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52865676&cb=jQuery1830317240029036183_1585970213997&_=1585970285606'
    #真实可用 url='http://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&invt=2&fltt=2&fields=f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196,f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287&secid=0.002317&cb=jQuery1124045031730971081374_1586764278775&_=1586764278819'
    # url='http://47.push2.eastmoney.com/api/qt/stock/sse?ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&fields=f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f206,f207,f208,f209,f210,f211,f212,f213,f214,f215,f86,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275&secid=0.002317'
    #真实可用 url='http://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&invt=2&fltt=2&fields=f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196,f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287&secid=1.603882&cb=jQuery1124045031730971081374_1586764278775&_=1586764278819'
    # title="金域医学"
    # title="众生药业"
    # return_html=crab_data(url,title)
    # return_html=query_reply(url_build("603882"))
    # # list1=['f58','f43','f170','f137','f193','f140','f194','f49','f161']  #顺序是名称、当前价、当前涨幅、主力净流入额、主力净占比、超大单净流入额、超大单净占比、外盘、内盘
    # result=stock_deal_data(return_html[0],'f58','f43','f170','f137','f193','f140','f194','f49','f161')
    # # print(result)
    # print(f'{return_html[1]}{result[0]},当前股价{result[1]},当前涨幅{result[2]}%，主力净流入{round(result[3]/100000000,2)}亿元，主力净占比{result[4]}%，超大单净流入{round(result[5]/100000000,2)}亿元，超大单净占比{result[6]}%，当前外盘为{round(result[7]/10000,2)}万手，内盘为{round(result[8]/10000,2)}万手')
    answer=query_reply("603882",'f58','f43','f170','f137','f193','f140','f194','f49','f161')
    print(answer)