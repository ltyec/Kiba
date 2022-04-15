from nonebot import on_regex, on_keyword
from nonebot.adapters.cqhttp import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot,Event
import requests
from nonebot.adapters.cqhttp.message import MessageSegment
import time

msg1 = 0
msg2 = 0
msg3 = 0

fudu = on_regex("[\s\S]*")

@fudu.handle()
async def first_msg(bot: Bot, event: Event, state: T_State):
  global msg1
  msg1 = str(event.get_message())
  pass

@fudu.got("next")
async def next_msg(bot: Bot, event: Event, state: T_State):
  global msg1, msg2
  msg2 = str(event.get_message())
  if msg1 == msg2:
    pass
  else:
    return

@fudu.got("final")
async def final_msg(bot: Bot, event: Event, state: T_State):
  global msg2, msg3
  msg3 = str(event.get_message())
  if msg2 == msg3:
    await fudu.finish(msg1)
    pass
  else:
    return

blhx = on_keyword("granbluefantasy.jp")

@blhx.handle()
async def _(bot: Bot, event: Event, state: T_State):
  await fudu.finish("骑空士钓你妈呢🥵", at_sender=True)
