from nonebot import on_command, on_startswith
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.message import Message

import urllib3
import json

today = on_command("today", aliases={'调试/日报', })

@today.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    try:
        try:
            url = 'http://www.tianque.top/d2api/today/'

            r = urllib3.PoolManager().request('GET', url)
            hjson = json.loads(r.data.decode())

            img_url = hjson["img_url"]

            #print(img_url)
            cq = "[CQ:image,file=" + img_url + ",id=40000]"
            await today.send(Message('json：\n'+str(hjson)+
                                    '\nimg_url：\n'+img_url+
                                    '\n'+cq))
        except:
            url = 'http://www.tianque.top/d2api/today/'

            r = urllib3.PoolManager().request('GET', url)
            hjson = json.loads(r.data.decode())

            error_url = hjson["error"]
            await today.send("获取日报失败\n"+
                            "error:\n"+
                            error_url)
    except :
        await today.send("获取日报失败:\n服务器错误")


