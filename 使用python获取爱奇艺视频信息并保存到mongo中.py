import pymongo
import requests

class AQY:
    def __init__(self):
        #打开mongo数据库
        self.mongo_client = pymongo.MongoClient(host='localhost',port=27017)
        #连接集合，不要集合一定存在
        self.db = self.mongo_client['py_spider']['AQY']
        self.url = "https://mesh.if.iqiyi.com/portal/videolib/pcw/data"
        self.headers = {
            'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer':'https://www.iqiyi.com/list/%E7%94%B5%E8%A7%86%E5%89%A7/%E7%BB%BC%E5%90%88_%E5%86%85%E5%9C%B0?vfrm=pcw_dianshiju&vfrmblk=711219_dianshiju_tbrb&vfrmrst=711219_dianshiju_tbrb_tag1',
        }

    def get_info(self,params):
        response = requests.get(self.url,headers=self.headers,params=params).json()
        return response['data']
    def parse_info(self,response):
        for parse in response:
            item = dict()
            item['desc']=parse['desc']
            item['name']=parse['title']
            item['firstEpisodeTitle']=parse['firstEpisodeTitle']
            self.save_info(item)
    def save_info(self,item):
        self.db.insert_one(item)
        print(f'保存成功：{item}')



if __name__ == '__main__':
    aiqiyi = AQY()
    for page in range(1,10):
        params = {
            "version": "1.0",
            "ret_num": "30",
            "page_id": str(page),
            "device_id": "d90b6b5eed6b8550e56a520d76b981e9",
            "passport_id": "",
            "recent_selected_tag": "综合;内地",
            "recent_search_query": "",
            "scale": "150",
            "dfp": "a04e70d8c57ebb4643b0232c496a734fbbffb829205f3475a367aaa9d86e6678d8",
            "channel_id": "2",
            "tagName": "",
            "mode": "24",
            "three_category_id_v2": "8052642132978633"
        }
        result = aiqiyi.get_info(params)
        aiqiyi.parse_info(result)
