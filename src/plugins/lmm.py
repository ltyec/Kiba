from nonebot.adapters.cqhttp import Message
from nonebot import on_keyword, on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot,Event
import requests
from nonebot.adapters.cqhttp.message import MessageSegment

help = on_command('help.lmm')


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_str = '''恋萌萌命令如下：
1   今日舞萌: 今天的舞萌运势
2   XXXmaimaiXXX什么: 随机一首歌
3   随个[dx/标准][绿黄红紫白]<难度>: 随机一首指定条件的乐曲
4   查歌<乐曲标题的一部分>: 查询符合条件的乐曲
5   [绿黄红紫白]id<歌曲编号>: 查询乐曲信息或谱面信息
6   <歌曲别名>是什么歌: 查询乐曲别名对应的乐曲
7   定数查歌 <定数> : 查询定数对应的乐曲
8   定数查歌 <定数下限> <定数上限>
9   分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看
10  缩写 [你想要查询的缩写]: 查询当前缩写的意思
11  ph图标 [黄圈外围显示的字] [黄圈内显示的字]: 生成一个以黄黑小网站logo样式的图片
12  分享 网易云音乐 或 链接: 以在群里下载歌曲
13  叫一声“恋萌萌”试试吧~~
14  @恋萌萌 搜图：启动搜图功能（支持iqdb/trace/sauce）
ver.0.2.2    by  未琉'''
    await help.send(Message([{
        "type": "image",
        "data": {
            "file": f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"
        }
    }]))


pic=on_keyword({'恋萌萌'})
@pic.handle()
async def _(bot:Bot,event:Event,state:T_State):
    msg = await suijitu()
    await pic.send(Message(msg))

async def suijitu():
    url='https://img.paulzzh.com/touhou/random'
    pic = requests.get(url)
    pic_ti = f"[CQ:image,file={pic.url}]"
    return pic_ti