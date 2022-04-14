from nonebot import on_regex, on_notice
from nonebot.adapters.cqhttp import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot,Event
import requests
from nonebot.adapters.cqhttp.message import MessageSegment
import time

msg = 0

fudu = on_regex("[\s\S]*")

@fudu.handle()
async def _(bot: Bot, event: Event, state: T_State):
  msg1 = str(event.get_message())
  global msg
  if msg == 0 :
    msg = msg1
  elif msg == msg1 :
    await fudu.finish(msg)
    msg = 0
    return
  else:
    return
