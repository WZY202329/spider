import pymysql
import requests

class TXwork:
    def __init__(self):
        self.url = 'https://careers.tencent.com/tencentcareer/api/post/Query?timestamp=1708415678244&countryId=&cityId=&bgIds=&productId=&categoryId=&parentCategoryId=&attrId=&keyword=&pageIndex={}&pageSize=10&language=zh-cn&area=cn'
        self.headers={
            'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer':'https://careers.tencent.com/search.html?keywords=tsa&lid=2175&tid=0'
        }
        #创建数据库连接
        self.db = pymysql.connect(host='localhost',user='root',password='000000',db='py_spider')
        #创建数据库游标
        self.cursor = self.db.cursor()
    def __del__(self):
        self.cursor.close()
        self.db.close()
    #获取数据
    def get_info(self):
        for page in range(1,31):
            response = requests.get(self.url.format(page),self.headers).json()
            print("当前正在抓取第{}页".format(page))
            work_list = response['Data']['Posts']
            yield work_list   #抓取一页，就返回一页数据，而不是返回所有信息，防止因为数据过多加载太慢

    #创建数据表
    def create_table(self):
        sql ="""
            create table if not exists tx_work(
             id int primary key auto_increment,
             CategoryName varchar(100),
             workname varchar(100) not null, 
             LocationName varchar(20),
             work_info text 
            );
        """
        try:
            self.cursor.execute(sql)
            print("表单创建完成。")
        except Exception as e:
            print("表单创建失败！！！",e)
    #插入信息
    def insert_info(self,*args):
        """
        接收字段
        :param args:
        :return:
        id
        CategoryName
        workname
        LocationName
        work_info
        """
        sql = """
        insert into tx_work() values (%s,%s,%s,%s,%s);
        """
        try:
            self.cursor.execute(sql,args)
            self.db.commit()#需要手动提交数据后，才会保存：事务
            print("保存成功")
        except Exception as e:
            print("保存失败！！！",e)
            self.db.rollback()#回滚，mysql提交数据都要进行回滚

    #调用函数执行
    def main(self):
        self.create_table()
        all_work_obj = self.get_info()
        #返回的是可迭代的数据
        for work_info_list in all_work_obj:
            for work_info_1 in work_info_list:
                CategoryName = work_info_1['CategoryName']
                workname = work_info_1['RecruitPostName']
                LocationName = work_info_1['LocationName']
                work_info = work_info_1['Responsibility']

                self.insert_info(0,CategoryName,workname,LocationName,work_info)


if __name__ == '__main__':
    tx_work = TXwork()
    tx_work.main()