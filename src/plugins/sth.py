from nonebot import on_regex, on_notice
from nonebot.adapters.cqhttp import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot,Event
import requests
from nonebot.adapters.cqhttp.message import MessageSegment
import time

fudu = on_regex("[\s\S]*")

@fudu.handle()
async def _(bot: Bot, event: Event, state: T_State):
  msg = str(event.get_message())
  global msg
  fudu1 = on_command(msg)

@fudu1.handle()
async def _(bot: Bot, event: Event, state: T_State):
  await fudu.finish(msg)
