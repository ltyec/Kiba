from nonebot import on_regex, on_notice
from nonebot.adapters.cqhttp import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot,Event
import requests
from nonebot.adapters.cqhttp.message import MessageSegment
import time

fudu = on_regex("[\s\S]*")

@fudu.handle()
async def first_msg(bot: Bot, event: Event, state: T_State):
  msg1 = str(event.get_message())
  pass

@fudu.got("next")
async def next_msg(bot: Bot, event: Event, state: T_State):
  msg2 = str(event.get_message())
  pass

@fudu.got("final")
async def final_msg(bot: Bot, event: Event, state: T_State):
  msg3 = str(event.get_message())
  if msg1==msg2==msg3:
    await fudu.finish(msg)
  else:
    return
