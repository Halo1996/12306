from selenium import webdriver  #导入selenium下的webdriver
from selenium.webdriver.support.ui import WebDriverWait  #导入等待需要的包
from selenium.webdriver.support import expected_conditions as EC #导入等待条件的包并重命名为EC
from selenium.webdriver.common.by import By  #导入By包
import time
#定义一个抢票类
class QiangPiao(object):

    def __init__(self):  #构造函数   初始化
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument("--proxy-server-http://47.106.120.36:8118")#设置代理ip
        self.initmy_url = 'https://kyfw.12306.cn/otn/view/index.html'#登陆成功后的网址
        self.login_url = 'https://kyfw.12306.cn/otn/resources/login.html'#定义一个登陆网址属性
        self.search_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'#定义一个查询界面网址
        self.driver = webdriver.Firefox(firefox_options=self.options) # 创建一个Firefox WebDriver的实例 要写上驱动所在路径
        self.passengers_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'#确认乘客信息界面
        #定义一个函数输入乘车信息

    def _wait_input(self):
        self.from_station = input("出发地")
        self.to_station = input("目的地")
        self.depart_time = input("出发时间")
        self.passengers = input("乘客姓名（如有多个乘客，用英文逗号隔开）：").split(",")
        self.trains = input("车次（如有多个车次，用英文逗号隔开）：").split(",")

    #定义一个函数实现登陆
    def _login(self):#_下划线表示不想被外界调用
        self.driver.get(self.login_url)#driver.get 方法将打开URL中填写的地址
        #显式等待
        #显式等待是在代码中定义等待一定条件发生后再进一步执行你的代码
        #隐式等待
        #如果某些元素不是立即可用的，隐式等待是告诉WebDriver去等待一定的时间后去查找元素。
        #  默认等待时间是0秒，一旦设置该值，隐式等待是设置该WebDriver的实例的生命周期
        WebDriverWait(self.driver,1000).until(  #设置等待和等待条件 1000为超时时间
            EC.url_to_be(self.initmy_url)  #当前url是否等于initmy_url  当等于时将接着执行
        )
        print("登录成功！")

    #定义一个函数实现自动订票
    def _order_ticket(self):
        #1.跳转到查余票的界面
        self.driver.get(self.search_url)    #跳转到查询余票界面

        #2.等待出发地是否输入正确
        WebDriverWait(self.driver,1000).until(  ##设置等待和等待条件 1000为超时时间
            EC.text_to_be_present_in_element_value((By.ID,
                "fromStationText"),self.from_station)# 等待文本呈现在元素的值当中  传递的是一个元组

        )

        #3.等待目的地是否输入正确
        WebDriverWait(self.driver, 1000).until(  ##设置等待和等待条件 1000为超时时间
            EC.text_to_be_present_in_element_value((By.ID,
                "toStationText"), self.to_station)
            # 等待文本呈现在元素的值当中  传递的是一个元组
        )

        # 4.等待出发日期是否输入正确
        WebDriverWait(self.driver, 1000).until(  ##设置等待和等待条件 1000为超时时间
            EC.text_to_be_present_in_element_value((By.ID,
                "train_date"), self.depart_time)
            # 等待文本呈现在元素的值当中  传递的是一个元组
        )
        #5.等待查询按钮是否可用
        WebDriverWait(self.driver,1000).until(
            EC.element_to_be_clickable((By.ID,"query_ticket"))
        )

        #6.如果能够被点击了，那么就找到这个查询按钮，执行点击事件
        searchBtn = self.driver.find_element_by_id("query_ticket")   #找到查询按钮
        searchBtn.click()  #点击查询按钮

        #7.点击查询按钮后，等待车次信息是否显示出来
        WebDriverWait(self.driver,1000).until(
            EC.presence_of_element_located((By.XPATH,
                ".//tbody[@id='queryLeftTable']/tr"))  #等待tr元素加载完毕
        )

        #8.找到所有没有datatran属性的tr标签，这些标签是存储了车次信息的
        tr_list = self.driver.find_elements_by_xpath(".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")#找到所有tbody下没有datatran属性的tr
        print(type(tr_list))
        for tr in tr_list:#遍历这些tr
            train_number = tr.find_element_by_class_name("number").text# 获取车次信息
            print(train_number)
            if train_number in self.trains: #如果获取到的车次信息在输入的车次里
                left_ticket_td = tr.find_element_by_xpath(".//td[4]").text #获取二等座的td标签的文本信息  返回来的是个列表
                if left_ticket_td =="有" or left_ticket_td.isdigit: #如果这个文本信息为”有“或为数字则
                    orderBtn = tr.find_element_by_class_name("btn72") #找到预订按钮
                    orderBtn.click()  #执行点击事件

                    #等待是否来到了确认乘客的页面
                    WebDriverWait(self.driver,1000).until(
                        EC.url_to_be(self.passengers_url)
                    )

                    #遍历乘车人信息看是否与输入相同，相同则执行点击事件
                    li_list = self.driver.find_elements_by_xpath(".//ul[@id='normal_passenger_id']/li")#返回的多个要用elements
                    print(type(li_list))
                    for li in li_list:
                        inp = li.find_element_by_xpath(".//input[@class='check']")
                        print(type(inp))
                        name = li.find_element_by_xpath(".//label").text
                        print(name)
                        if name in self.passengers:
                            inp.click()

                            # #找到提交按钮，并执行点击事件
                            submitBtn = self.driver.find_element_by_id('submitOrder_id')
                            submitBtn.click()

                            #等待弹出框弹出
                            time.sleep(5)

                            #找到确认按钮，并执行点击事件
                            qrBtn = self.driver.find_element_by_id('qr_submit_id')
                            qrBtn.click()

    #定义执行函数调用登陆自动抢票
    def run(self):
        self._wait_input()  #输入信息
        self._login()       #登录
        self._order_ticket()#自动订票4

if __name__ == '__main__':
    spider = QiangPiao()       #初始化QiangPiao类的对象
    spider.run()    #调用run方法

