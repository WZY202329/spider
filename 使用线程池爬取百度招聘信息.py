import requests
import pymysql
from concurrent.futures import ThreadPoolExecutor

class BaiDuWork:
    def __init__(self):
        self.db = pymysql.connect(host='localhost',user='root',password='000000',db='py_spider')
        self.cursor = self.db.cursor()
        self.api_url='https://talent.baidu.com/httservice/getPostListNew'
        self.headers={
            'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Cookie':'BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BIDUPSID=06E1AA4D0D2F1E541B2C11E80F66A6BA; PSTM=1708094781; BAIDUID=06E1AA4D0D2F1E541B2C11E80F66A6BA:FG=1; H_PS_PSSID=40170_40203_39662_40207_40211_40215_40223_40249_40265_40079_40272; H_WISE_SIDS=40170_40203_39662_40207_40211_40215_40223_40249_40265_40079; H_WISE_SIDS_BFESS=40170_40203_39662_40207_40211_40215_40223_40249_40265_40079; ZFY=j7RYzgpfHvY0:BKvGHr75UjJP9uKSGG8:BaMJDWqyBxKI:C; BAIDUID_BFESS=06E1AA4D0D2F1E541B2C11E80F66A6BA:FG=1; BAIDU_WISE_UID=wapp_1708606849709_126; arialoadData=false; Hm_lvt_50e85ccdd6c1e538eb1290bc92327926=1708651329; Hm_lpvt_50e85ccdd6c1e538eb1290bc92327926=1708652611; RT="z=1&dm=baidu.com&si=ba818de4-a886-4a97-9c4a-b13e9eee4f63&ss=lsxyvlec&sl=1&tt=agb&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"',
            'Referer':'https://talent.baidu.com/jobs/social-list?search=python'
        }
    def __del__(self):
        self.cursor.close()
        self.db.close()
    def get_info(self,page):
        from_data = {
            'recruitType': 'SOCIAL',
            'pageSize': 10,
            'keyWord': 'python',
            'curPage': page,
            'projectType':''
        }
        json_data = requests.post(self.api_url,headers=self.headers,data=from_data).json()
        return json_data
    def parse_info(self,response):
        work_info=response['data']['list']
        for work in work_info:
            education = work['education'] if work['education'] else '空'
            name = work['name']
            service=work['serviceCondition']
            workContent = work['workContent']
            print(name,service,workContent,)
            self.save_info(0,education,name,service,workContent)
    def create_table(self):
        create_table_sql ="""
        create table if not exists baiduWork_threadPool(
        id int primary key auto_increment,
        education varchar (100),
        name varchar (100),
        service text,
        workContent text
        );
        """
        try:
            self.cursor.execute(create_table_sql)
            print("表单创建成功")
        except Exception as e:
            print("表单构建失败",e)
    def save_info(self,*args):
        sql = """
        insert into baiduWork_threadPool(id,education,name,service,workContent) values (%s,%s,%s,%s,%s);
        """
        try:
            self.cursor.execute(sql,args)
            self.db.commit()
            print("数据保存成功",*args)
        except Exception as e:
            print("数据保存失败",e)
            self.db.rollback()
    def main(self):
        self.create_table()
        #创建线程
        with ThreadPoolExecutor(max_workers=5) as pool:
            for page in range(1,31):
                response = pool.submit(self.get_info,page)
                self.parse_info(response.result())




if __name__ == '__main__':
    baiduwork = BaiDuWork()
    baiduwork.main()