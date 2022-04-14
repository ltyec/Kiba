from nonebot import on_command, on_notice
from nonebot.adapters.cqhttp import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot,Event
import requests
from nonebot.adapters.cqhttp.message import MessageSegment
import time

msg = 0

fudu = on_command(priority=10)

@fudu.handle()
async def _(bot: Bot, event: Event, state: T_State):
  msg1 = str(event.get_message())
  if msg == 0 :
    msg = msg1
  elif msg == msg1 :
    await fudu.finish(msg)
    msg = 0
  return
 
@on_notice('group_increase')
async def _(session: NoticeSession):
    await session.send('欢迎新群友～')
