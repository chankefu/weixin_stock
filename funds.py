#资金流向分析



import json
import re
import datetime
from urllib.request import urlopen
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from chinese_calendar import is_holiday
except:
    import os
    os.system('pip install matplotlib')
    os.system('pip install chinese_calendar')
    import matplotlib.pyplot as plt
    import matplotlib as mpl
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

# 解决中文乱码问题
#sans-serif就是无衬线字体，是一种通用字体族。
#常见的无衬线字体有 Trebuchet MS, Tahoma, Verdana, Arial, Helvetica, 中文的幼圆、隶书等等。
mpl.rcParams['font.sans-serif']=['SimHei'] #指定默认字体 SimHei为黑体
mpl.rcParams['axes.unicode_minus']=False #用来正常显示负号


#处理网页返回的jQuery格式的数据，转换为多维数组（自定义）。注意，输入参数应该为用decode()解码后的网页数据，否则报错。
#*args的参数输入为用,号隔开的多个字符串，如'f14','f62','f66','f69','f124','f184','f204'
def deal_data(data, *args):
    pattern = re.compile(r'.*?(\[.*?\])')
    temp_data = re.match(pattern, data).group(1)
    datas = json.loads(temp_data)
    result = []
    canshu = []
    for index in datas:
        for arg in args:
            canshu.append(index[arg])
        result.append(canshu)
        canshu = []
    return result

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2.- 0.2, 1.03*height, '%s' % int(height))


def fund_analysis(url,bk):
    response = urlopen(url)
    html = response.read().decode();
    # print(html)
    result=deal_data(html,'f14','f62','f184','f204')
    print(result)
    # print(len(result))
    name_list = []
    inflows_list = []
    inflow_ratio_list = []
    leader_list = []
    for index in range(0, 10):
        name_list.append(result[index][0])
        inflows_list.append(result[index][1])
        inflow_ratio_list.append(result[index][2])
        leader_list.append(result[index][3])
    for index in range(len(result)-10, len(result)):
        name_list.append(result[index][0])
        inflows_list.append(result[index][1])
        inflow_ratio_list.append(result[index][2])
        leader_list.append(result[index][3])
    # print(name_list)
    inflows_list = [round(x/100000000,2) for x in inflows_list]
    leader_list=[x.replace("","\n") for x in leader_list]
    # print(num_list)

    #标题加上日期、时间、板块类别
    pic_time = tradetime(datetime.datetime.now())
    pic_title=pic_time.strftime("%Y{y}%m{m}%d{d}%H{h}%M{M}").format(y = "年",m = "月",d = "日",h = "时",M = "分")+"\n"+bk+"主力资金净流入前、末十名"
    # print(pic_title)

    # 画柱状图
    plt.title(pic_title,fontsize=16)
    plt.xlabel("",fontsize=8)
    plt.xticks(rotation=60)  #横坐标标签倾斜60度
    plt.ylabel("金额 (亿元)", fontsize=14)
    autolabel(plt.bar(range(len(inflows_list)), inflows_list, color=['r']*10+['g']*10, tick_label=name_list))


    if abs(inflows_list[0])>abs(inflows_list[-1]):
        y_height=inflows_list[0]*0.3
    else:
        y_height=inflows_list[-1]*0.3
    
    
    for x_height,leader in zip(range(len(inflows_list)),leader_list):
        plt.text(x_height,y_height, leader, ha='center', va='bottom', fontsize=12,rotation=0,color="blue")

    #保存图片 dpi为图像分辨率
    plt.savefig(pic_title.replace("\n", "")+".png",dpi=600,bbox_inches = 'tight')


    plt.ion()  # 打开交互模式
    plt.show()
    # plt.pause(3)  # 该句显示图片3秒
    plt.ioff()  # 显示完后一定要配合使用plt.ioff()关闭交互模式，否则可能出奇怪的问题
    # plt.clf()
    plt.close()



if __name__ == '__main__':
    #行业板块
    #短数据链接
    # url = 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&fields=f12,f13,f14,f62&fid=f62&fs=m:90+t:2&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18305065465637410975_1585815026465&_=1585816040642'
    #长数据链接
    url1='http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:2&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52865676&cb=jQuery1830317240029036183_1585970213997&_=1585970285606'
    bk1="行业板块"


    #概念板块
    #短数据链接
    # url = 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&fields=f12,f13,f14,f62&fid=f62&fs=m:90+t:3&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery183021539183328293965_1585815495642&_=1585816449996'

    #长数据链接，以下两个链接不同的地方在于排序方式，区别可能在最后的rt=52865663&cb=jQuery18303613470837162893_1585969883735&_=1585969895914的部分。

    # url='http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=50&po=0&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:3&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52865663&cb=jQuery18303613470837162893_1585969883735&_=1585969895914' 
    url2= 'http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid=f62&fs=m:90+t:3&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=52860548&cb=jQuery183021539183328293965_1585815495642&_=1585816450894'
    bk2="概念板块"

    fund_analysis(url1,bk1)
    # time.sleep(5)
    fund_analysis(url2,bk2)
    # time.sleep(1800)












