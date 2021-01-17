from selenium import webdriver
from tkinter import *
import time
import csv
import re
import os
# import pandas as pd



"""gui界面"""
class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)     # super代表父类的定义，而不是父类对象
        self.master = master
        self.grid()
        self.createwidet()

    def createwidet(self):
        """创建组件"""
        self.la1 = Label(self, text='商 品 名 称 :', width=10, height=1, font=('楷书', 20), fg='black', relief="raised")
        self.la1.grid(row=0, column=0, sticky=E)

        self.la2 = Label(self, text='页数(1-100)', width=10, height=1, font=('楷书', 20), fg='black', relief="raised")
        self.la2.grid(row=1, column=0, sticky=E)
        self.la2 = Label(self, text=' (缺省则自己爬取最大页数) ', width=20, height=1, font=('楷书', 10), fg='red')
        self.la2.grid(row=1, column=2, sticky=E)

        v1 = StringVar()  # stringvar与组件内容绑定，两者一者变化另一者也变化
        self.entry = Entry(self, textvariable=v1, font=('楷书', 20), relief="raised")
        # v1.set("请输入商品的关键字：")
        self.entry.grid(row=0, column=1)
        v2 = StringVar()
        self.entry2 = Entry(self, textvariable=v2, font=('楷书', 20), relief="raised")
        self.entry2.grid(row=1, column=1)

        self.bt1 = Button(self, text='搜索', font=('楷书', 20), relief="raised")
        self.bt1.grid(row=2, column=0, sticky=E)
        self.bt1["command"] = self.search

        self.tx1 = Text(root, width=120, height=30, font=('楷书', 10), fg='red', bg="gray")
        self.tx1.grid(row=3, column=0)
        self.tx1.insert(1.0, '数据已写入当前代码目录下的data.csv文件中，文本框只展示部分信息:\n格式为：名称，价格，付款人数，店铺名称，发货地址 \n\n')
        # 创建一个退出按钮
        self.btquit = Button(self, text='退出', font=('楷书', 20), command=root.destroy)
        self.btquit.grid(row=2, column=1, sticky=W)

    def search(self):
        # self.g()
        keyword = self.entry.get()
        Page = self.entry2.get()
        # print(keyword)
        # print(Page)
        taobao(key=keyword, PAGE=Page)
        self.tx1['fg'] = 'blue'
        if not Page:
            Page = 100
        self.tx1.insert(END, '共有{}页数据,请等待！\n'.format(Page))
        file_path = '../crawler/data.csv'
        if file_path is not None:
            # file_text = pd.read_csv(file_path)
            # file_path.head(10)
            i = 0
            with open(file=file_path, mode='r+', encoding='utf-8') as file:
                while i <25:
                    i += 1
                    file_text = file.readline()
                    self.tx1.insert('insert', i)
                    self.tx1.insert(END, ': ')
                    self.tx1.insert('insert', file_text)
            self.g()
            time.sleep(15)
            self.g()

    def g(self):
        if self.bt1['text'] == '搜索':
           self.bt1['text'] = '已完成'
           self.bt1['font'] = ('楷书', 15)
        else:
            self.bt1['text'] = '搜索'
            self.bt1['font'] = ('楷书', 20)


class taobao():
    def __init__(self, key, PAGE):
        self.keyword = key  # input("请输入你要搜索的商品的关键字：")
        self.page = PAGE
        # print(self.page)
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.taobao.com")
        self.main()


    def search_product(self):
        """模拟搜索商品，获取最大页数"""
        self.driver.find_element_by_id('q').send_keys(self.keyword)
        self.driver.find_element_by_class_name('btn-search').click()
        self.driver.maximize_window()
        time.sleep(15)
        print('请打开手机淘宝，扫码登陆！')
        if not self.page:
            print("ok!")
            page = self.driver.find_element_by_xpath('//*[@id="mainsrp-pager"]/div/div/div/div[1]').text  # 找到页数标签
            page = re.findall('(\d+)', page)[0]
            return int(page)
        else:
            return int(self.page)

    def get_product(self):
        divs = self.driver.find_elements_by_xpath('//div[@class="items"]/div[@class="item J_MouserOnverReq  "]')
        for div in divs:
            info = div.find_element_by_xpath('.//div[@class="row row-2 title"]/a').text  # 商品名称
            price = div.find_element_by_xpath('.//strong').text + "元"  # 商品价格
            deal = div.find_element_by_xpath('.//div[@class="deal-cnt"]').text  # 付款人数
            shopname = div.find_element_by_xpath('.//div[@class="shop"]/a').text  # 店铺名称
            addr = div.find_element_by_xpath('.//div[@class="location"]').text  # 发货地址
            """把读取到的信息写入csv文件"""
            file__path = '../taobaocrawls/data.csv'
            if (os.path.exists(file__path)and self.first):
                os.remove(file__path)
                # print("文件已存在，且已被删除！")
                self.first = False
            with open('data.csv', 'a', newline="") as filecsv:
                csvwriter = csv.writer(filecsv, delimiter='|')
                csvwriter.writerow([info, price, deal, shopname, addr])
            print(info, price, deal, shopname, addr, sep=' |')


    def main(self):
        page = self.search_product()
        # print("ok")
        # page = 2
        print('共有{}页数据,请等待！'.format(page))
        print('*' * 100)
        print('正在爬取第1页数据')
        print('*' * 100)
        self.first = True
        self.get_product()
        # self.first = False
        page_num = 1

        while page_num < page:
            print('*' * 100)
            # print(page, page_num)
            print('正在爬取第{}页数据'.format(page_num + 1))
            print('*' * 100)
            """ q不变 s=（页数-1）*44 """
            self.driver.get('https://s.taobao.com/search?q={}&s={}'.format(self.keyword, page_num * 44))  # 拼接URL地址
            self.driver.implicitly_wait(2)  # 浏览器等待时间
            self.driver.maximize_window()  # 最大化界面
            self.get_product()
            page_num += 1


if __name__ == "__main__":
    root = Tk()  # 创建窗口
    root.geometry('760x465+400+210')  # 窗口大小 窗口位置
    root.title('淘宝商品信息爬取')  # 标题
    app = Application(master=root)
    root.mainloop()
