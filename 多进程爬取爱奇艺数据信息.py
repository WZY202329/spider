import pymongo
import requests
import threading
from queue import Queue

class AIQIYI:
    def __init__(self):
        self.mongo_client = pymongo.MongoClient()
        self.collection = self.mongo_client['py_spider']['thread_aiqiyi']
        self.api_url='https://pcw-api.iqiyi.com/search/recommend/list?channel_id=2&data_type=1&mode=11&page_id={}&ret_num=48&session=032d987e7b4d654c424176afbe53a9cb&three_category_id=15;must'
        self.hreaders={
            'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer':'https://list.iqiyi.com/www/2/15-------------11-1-1-iqiyi--.html?s_source=PCW_SC',
        }
        #创建队列，保存数据
        self.url_queue = Queue()
        self.json_queue=Queue()
        self.conent_dict_queue=Queue()#保存提取到的字典数据
    #获取url
    def get_url(self):
        for page in range(1,10):
            self.url_queue.put(self.api_url.format(page))
    #发送请求并获取数据
    def get_info(self):
        while True:
            url = self.url_queue.get()
            response = requests.get(url=url,headers=self.hreaders).json()
            self.json_queue.put(response)
            self.url_queue.task_done()#执行一次，队列中的计数器减1
    #数据解析
    def parse_info(self):
        while True:
            item = self.json_queue.get()
            category = item['data']['list']
            for info in category:
                item=dict()
                item['name'] = info['title']
                item['url'] = info['playUrl']
                item['description'] = info['description']
                #将组织好的字典组织到队列
                self.conent_dict_queue.put(item)
            self.json_queue.task_done()
    #保存数据
    def save_info(self):
        while True:
            item = self.conent_dict_queue.get()
            self.collection.insert_one(item)
            self.conent_dict_queue.task_done()
            print("插入成功",item)

    def main(self):
        #创建列表保存线程
        tread_list = list()

        t_url = threading.Thread(target=self.get_url)
        tread_list.append(t_url)
        #获取数据可以使用多个线程
        for _ in range(1,3):
            t_get_info = threading.Thread(target=self.get_info)
            tread_list.append(t_get_info)
        t_parse_info = threading.Thread(target=self.parse_info)
        tread_list.append(t_parse_info)
        #保存数据只能用一个线程
        t_save_info = threading.Thread(target=self.save_info)
        tread_list.append(t_save_info)

        #循环线程列表并启动线程
        for thread_obj in tread_list:
            thread_obj.daemon = True #子线程为守护线程
            thread_obj.start()
        #判断所有队列中的计数器是否为0，如果为0，则释放主线程，否则就会阻塞
        for queue in [self.url_queue,self.json_queue,self.conent_dict_queue]:
            queue.join()

        print("主线程结束")
        self.mongo_client.close()
        print("数据库链接已经关闭")

if __name__ == '__main__':
    aiqiyi = AIQIYI()
    aiqiyi.main()


