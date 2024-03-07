import redis
import hashlib
import asyncio
import aiohttp
import aiomysql
from lxml import etree
#判断返回的页码集的编码，反爬
import chardet

class CarSpider:
    #变成类属性会让他初始化一次
    redis_cilent = redis.Redis()
    def __init__(self):
        self.url = 'https://www.che168.com/china/a0_0msdgscncgpi1ltocsp{}exf4x0/?pvareaid=102179#currengpostion'
        self.api_url = 'https://cacheapigo.che168.com/CarProduct/GetParam.ashx?specid={}'
        self.headers={
            'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            }
    def __del__(self):
        self.redis_cilent.close()
    #获取汽车id
    async def get_car_id(self,page,session,pool):
        """
        :param page:翻页参数
        :param session:请求对象
        :param pool:数据库连接池对象
        :return:
        """
        async with session.get(self.url.format(page),headers=self.headers) as response:
            #使用response对象获取原始数据
            conten = await response.read()
            #获取页码编码集
            # 判断页面是否返回GB2312,没有问题，如果返回utf-8，说明加载过快
            encoding = chardet.detect(conten)['encoding']
            if encoding=='GB2312':
                result=conten.decode('gbk')
            else:
                result = conten.decode(encoding)
                print(f"访问频繁{encoding}")

            tree = etree.HTML(result)
            id_list = tree.xpath('//ul[@class="viewlist_ul"]/li/@specid')
            if id_list:
                tasks = [asyncio.create_task(self.get_info(spec_id,session,pool)) for spec_id in id_list]
                await asyncio.wait(tasks)

    async def get_info(self,spec_id,session,pool):
        async with session.get(self.api_url.format(spec_id),headers=self.headers,) as response:
            json_data = await response.json()

            if json_data['result'].get('paramtypeitems'):
                item = dict()
                item['name'] = json_data['result']['paramtypeitems'][0]['paramitems'][0]['value']
                item['value'] = json_data['result']['paramtypeitems'][0]['paramitems'][1]['value']
                item['brand'] = json_data['result']['paramtypeitems'][0]['paramitems'][2]['value']
                item['altitude'] = json_data['result']['paramtypeitems'][1]['paramitems'][2]['value']
                item['breadth'] = json_data['result']['paramtypeitems'][1]['paramitems'][1]['value']
                item['length'] = json_data['result']['paramtypeitems'][1]['paramitems'][0]['value']
                #提取完数据后进行保存,最好是单线程，所以没有设置tasks
                await self.save_info(item,pool)
            else:
                print("数据不存在")

    #在数据保存之前将数据打包成MD5去重
    @staticmethod
    def get_md5(dict_item):
        md5 = hashlib.md5(str(dict_item).encode('utf-8')).hexdigest()
        return md5

    async def save_info(self,item,pool):
        #使用异步上下文管理器的方式完成数据保存
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                val_md5 = self.get_md5(item)
                redis_result = self.redis_cilent.sadd('car:filter',val_md5)
                if redis_result:
                    sql="""
                    insert into car_info() value(%s,%s,%s,%s,%s,%s,%s);
                    """
                    try:
                        await cursor.execute(sql,(
                            0,
                            item['name'],
                            item['value'],
                            item['brand'],
                            item['altitude'],
                            item['breadth'],
                            item['length'],
                        ))
                        await conn.commit()
                        print(f"插入成功:{item}")
                    except Exception as e:
                        print("插入失败",e)
                        await conn.rollback()
                else:
                    print("数据重复")

    #创建启动函数
    async def main(self):
        #创建数据库连接池
        async with aiomysql.create_pool(host='localhost',user='root',password='000000',port=3306,db='py_spider') as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    #创建表
                    create_table_sql = """
                    create table car_info(
                    id int primary key auto_increment,
                    name varchar (100),
                    value varchar (100),
                    brand varchar (100),
                    altitude varchar (100),
                    breadth varchar (100),
                    length varchar(100)
                    );
                    """
                    #在异步代码中要先检查表是否存在
                    #1存在 0不存在
                    check_table = "show tables like 'car_info'"
                    result = await cursor.execute(check_table)
                    if not check_table:
                        await cursor.execute(create_table_sql)
                        print("连接创建成功")
                    else:
                        print("连接已存在")

            #创建请求对象
            async with aiohttp.ClientSession() as session:
                tasks=[asyncio.create_task(self.get_car_id(page,session,pool)) for page in range(1,51)]
                await asyncio.wait(tasks)

if __name__ == '__main__':
    car_spider=CarSpider()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(car_spider.main())
