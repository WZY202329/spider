import time
import redis
import requests
import pymongo
import hashlib
from multiprocessing import Process, JoinableQueue as Queue

class MangGuoTV:
    mongo_client = pymongo.MongoClient()
    collection = mongo_client['py_spider']['mg_tv_process']
    redis_client = redis.Redis()
    def __init__(self):
        self.headers = {
            'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        self.url = "https://pianku.api.mgtv.com/rider/list/pcweb/v3"

        self.params_queue = Queue()
        self.json_queue=Queue()
        self.conent_queue=Queue()#保存提取到的字典数据
    def get_params(self):
        for page in range(1,10):
            params = {
                "allowedRC": "1",
                "platform": "pcweb",
                "channelId": "2",
                "pn": str(page),
                "pc": "80",
                "hudong": "1",
                "_support": "10000000",
                "kind": "19",
                "area": "10",
                "year": "all",
                "chargeInfo": "a1",
                "sort": "c2",
                "feature": "all"
            }
            self.params_queue.put(params)
    def get_info(self):
        while True:
            params = self.params_queue.get()
            response = requests.get(self.url,headers=self.headers,params=params).json()
            self.json_queue.put(response)
            self.params_queue.task_done()
    def parse_info(self):
        while True:
            json = self.json_queue.get()
            movie_info = json['data']['hitDocs']
            for info in movie_info:
                item = dict()
                item['name']=info['title']
                item['subtitle']=info['subtitle']
                item['story']=info['story']
                self.conent_queue.put(item)
            self.json_queue.task_done()

    @staticmethod
    def MD5(value):
        md5_hashlib = hashlib.md5(str(value).encode('utf-8')).hexdigest()
        return md5_hashlib

    def save_info(self):
        while True:
            item = self.conent_queue.get()
            md5_info = self.MD5(item)
            result = self.redis_client.sadd('mg_movie:filter',md5_info)
            if result:
                self.collection.insert_one(item)
                print("数据保存成功",item)
            else:
                print("数据重复")
            self.conent_queue.task_done()


    def main(self):
        process_list = list()

        p_get_params = Process(target=self.get_params)
        process_list.append(p_get_params)

        for _ in range(5):
            p_get_info = Process(target=self.get_info)
            process_list.append(p_get_info)

        for _ in range(3):
            p_parse_info = Process(target=self.parse_info)
            process_list.append(p_parse_info)

        p_save_info = Process(target=self.save_info)
        process_list.append(p_save_info)

        for process in process_list:
            process.daemon = True
            process.start()

        time.sleep(10)

        for i in [self.params_queue,self.json_queue,self.conent_queue]:
            i.join()
        self.redis_client.close()
        self.mongo_client.close()

        print("主进程结束")
if __name__ == '__main__':
    mangguotv = MangGuoTV()
    mangguotv.main()

