import asyncio
import aiomysql
import aiohttp
#创建文件夹
import os
#替换成异步文件对象
import aiofile

class WZRY:
    def __init__(self):
        self.api_url = 'https://pvp.qq.com/web201605/js/herolist.json'
        self.skin_url = 'https://game.gtimg.cn/images/yxzj/img201606/heroimg/{}/{}-mobileskin-{}.jpg'
        self.headers = {
            'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
    async def get_info(self,session,e_name,c_name):
        for skin_id in range(1,11):
            async with session.get(self.skin_url.format(e_name,e_name,skin_id),headers=self.headers) as response:
                if response.status == 200:
                    content = await response.read()
                    async with aiofile.async_open('./images/'+c_name+'_'+str(skin_id)+'.jpg','wb') as f:
                        await f.write(content)
                        print("保存成功：",c_name+'_'+str(skin_id))
                else:
                    break
    async def main(self):
        tasks = list()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url,headers=self.headers) as response:
                result = await response.json(content_type=None)
                for item in result:
                    e_name=item['ename']
                    c_name=item['cname']

                    coro_obj = self.get_info(session,e_name,c_name)
                    tasks.append(coro_obj)
                await asyncio.wait(tasks)


if __name__ == '__main__':
    if not os.path.exists("./images"):
        os.mkdir("./images")
    hero_skin = WZRY()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hero_skin.main())
