

import time
from pymongo import MongoClient
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WPshop:
    def __init__(self):
        self.mondo_client = MongoClient()
        self.collection = self.mondo_client['py_spider']['WP_shop']

        #创建浏览器对象
        option = webdriver.ChromeOptions()
        #屏蔽图片
        prefs = {"profile.managed_default_content_settings.images":2}
        option.add_experimental_option("prefs",prefs)

        self.browser = webdriver.Chrome(options=option)

    #访问指定页面并进行搜索
    def open_info(self):
        self.browser.get("https://www.vip.com")
        #创建页面等待对象
        wait = WebDriverWait(self.browser,10)
        #进行数据搜索
        el_input = wait.until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="J-search"]/div[1]/input')))
        el_input.send_keys('jk制服')

        el_button = wait.until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="J-search"]/div[1]/a'))
        )
        time.sleep(2)
        el_button.click()

        #设置休眠时间让浏览器渲染页面
        time.sleep(5)
    #页面滚动
    def roll(self):
        for i in range(1,13):
            js_code = f"document.documentElement.scrollTop={i*1500}"
            self.browser.execute_script(js_code)
            time.sleep(randint(1,2))

    #数据提取
    def parse_data(self):
        self.roll()
        div_list = self.browser.find_elements(
            By.XPATH, '//div[@class="c-goods-item  J-goods-item c-goods-item--auto-width"]'
        )
        for temp in div_list:
            price = temp.find_element(By.XPATH,'.//div[@class="c-goods-item__sale-price J-goods-item__sale-price"]').text
            name = temp.find_element(By.XPATH,'.//div[2]/div[2]').text
            item = {
                'name':name,
                'price':price
            }
            print(item)
            self.save_info(item)
        self.next_page()
    #数据保存
    def save_info(self,item):
        self.collection.insert_one(item)
        print('数据保存成功')
    #翻页
    def next_page(self):
        try:
            next_button = self.browser.find_element(By.XPATH,'//*[@id="J_nextPage_link"]/i')
            if next_button:
                next_button.click()
                self.parse_data()
            else:
                self.browser.close()
        except Exception as e:
            print('已经翻到最后一页:',e)

    def main(self):
        self.open_info()
        self.parse_data()

if __name__ == '__main__':
    wpshop = WPshop()
    wpshop.main()




