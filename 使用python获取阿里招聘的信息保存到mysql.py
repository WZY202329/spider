import pymysql
import requests

class ALIwork:
    def __init__(self):
        self.db = pymysql.connect(host='localhost',user='root',password='000000',db='py_spider')
        self.cursor = self.db.cursor()
        self.api_url = 'https://talent.taotian.com/position/search?_csrf=d85c4ea4-48a5-4b53-b40a-84fd8701b50f'
        self.headers = {
            'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer':'https://talent.taotian.com/off-campus/position-list?lang=zh',
            'Cookie':'XSRF-TOKEN=d85c4ea4-48a5-4b53-b40a-84fd8701b50f; prefered-lang=zh; SESSION=MDZGOTA2OTYzMERGRjlEMUExOTRDNDBCMDY3MDJBQzY=; cna=XllbHqz2CFkBASQJigR37SKE; xlly_s=1; isg=BPb2HErbj5XQnHtx-xMm-AVbRyz4FzpRU82TcGDdnlmfo5Q9yKKWYKYQu3_PCzJp; tfstk=eua2SWf6tZQV2QAQ000Z4uBlDt0xW2BBoPMss5ViGxDmCiCw78PnjFsxlfbaC8iglqNbURyUdm4fDSNMS5D-CxMbcfbaE8im5oMjsIUzLFTfHiFM7VgGd9_CRShjWVXBqI5iISeOonV1RwNYiV3Gd9_CMX1axiBSXMjPPcb8TY4PoaZDB9KsCFYgoNnqLNMqwbzyW0kQir-HxMcq0vVmUglDBbbIJPE2IhomwbkCa_lggpRjLXeXNhKtqDcrdsnMXhnmwbkCa_-9XmLnav1xj'
        }
    def __del__(self):
        self.cursor.close()
        self.db.close()
    #获取数据
    def get_info(self):
        for page in range(1,31):
            json_data = {
            "batchId":"",
            "categories":"",
            "channel":"group_official_site",
            "deptCodes":[],
            "key":"",
            "language":"zh",
            "myReferralShareCode":"",
            "pageIndex":1,
            "pageSize":10,
            "regions":"",
            "shareId":"",
            "shareType":"",
            "subCategories":""
            }
            response = requests.post(self.api_url,headers=self.headers,json=json_data).json()
            print('当前页数为{page}')
            yield response['content']['datas']

    # 创建数据表
    def create_table(self):
        sql = """
            create table if not exists ali_work(
            Name varchar(100) not null,
            workLocations varchar(20), 
            requirement text,
            description text 
               );
                """
        try:
            self.cursor.execute(sql)
            print("表单创建完成。")
        except Exception as e:
            print("表单创建失败！！！", e)

    # 插入信息
    def insert_info(self, *args):
        """
        接收字段
        :param args:
        :return:
        Name
        worklocationa
        requirement
        description
        """
        sql = """
        insert into ali_work() values (%s,%s,%s,%s,%s);
        """
        try:
            self.cursor.execute(sql, args)
            self.db.commit()  # 需要手动提交数据后，才会保存：事务
            print("保存成功")
        except Exception as e:
            print("保存失败！！！", e)
            self.db.rollback()  # 回滚，mysql提交数据都要进行回滚

    def main(self):
        self.create_table()
        all_work_list = self.get_info()
        for all_work in all_work_list:
            for work_info in all_work:
                Name = work_info['name']
                worklocationa = work_info['workLocations']
                requirement = work_info['requirement']
                description = work_info['description']
                self.insert_info(0,Name, worklocationa, requirement, description)



if __name__ == '__main__':
    ALI_work = ALIwork()
    ALI_work.main()