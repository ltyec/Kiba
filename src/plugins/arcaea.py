from nonebot import on_command, on_message, on_notice, require, get_driver, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from nonebot.adapters.cqhttp import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot import get_bot
import re
from src.libraries.config import Config

from src.libraries.arcapi import *
from src.libraries.arcsql import *
from src.libraries.arcdraw import *

archelp = on_command("arcaea.help")
@archelp.handle()
async def _(bot: Bot, event: Event, state: T_State):
    helper = '''▾ Arcaea 模块(Beta) - 帮助
请注意: 当前 Arcaea 模块正处于 BETA 测试中，带 * 的部分功能可能不稳定。依靠的 Arcaea 服务器更新时，本模块大部分命令均会失效。
arcinfo 查询b30，需等待1-2分钟
arcre*   使用本地查分器查询最近一次游玩成绩
arcre:  指令结尾带：使用est查分器查询最近一次游玩成绩
arcre: arcid  使用好友码查询TA人
arcre: @  使用@ 查询好友
arcup*   （超级管理员用）查询用账号添加完好友，使用该指令绑定查询账号，添加成功即可使用arcre指令。
arcbind [arcid] [arcname]   绑定用户
arcun   解除绑定'''
    await archelp.send(helper)


asql = arcsql()

arcinfo = on_command("arcinfo")
@arcinfo.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qqid = event.user_id
    msg = str(event.get_message()).strip().split(" ")
    if 'CQ:at' in str(event.get_message()):
        result = re.search(r'\[CQ:at,qq=(.*)\]', str(event.get_message()))
        qqid = int(result.group(1))
    result = asql.get_user(qqid)
    if msg[0]:
        if msg[0].isdigit() and len(msg[0]) == 9:
            arcid = msg[0]
        else:
            await arcinfo.finish('▿ Arc - Best 30 查询\n仅可以使用好友码查询。')
            return
    elif not result:
        await arcinfo.finish('▿ Arc - Best 30 查询 - 未绑定账户\n该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)')
        return
    else:
        arcid = result[0]
    await arcinfo.send('▾ Arc - Best 30 查询\n已找到您的账户，正在查询，请稍候。\n若 10min 后仍没有收到 Best 30 信息，请再试一次。')
    info = await draw_info(arcid)
    await arcinfo.send(info)

arcre = on_command('arcre')
@arcre.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qqid = event.user_id
    est = False
    msg = str(event.get_message()).strip().split(" ")
    if 'CQ:at' in str(event.get_message()):
        result = re.search(r'\[CQ:at,qq=(.*)\]', str(event.get_message()))
        qqid = int(result.group(1))
    result = asql.get_user(qqid)
    if msg[0]:
        if msg[0].isdigit() and len(msg[0]) == 9:
            result = asql.get_user_code(msg[0])
            if not result:
                await arcre.finish('▿ Arc - 最近成绩 - 未绑定账户\n该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)')
                return
            user_id = result[0]
        elif msg[0] == ':' or msg[0] == '：':
            if not result:
                await arcre.finish('▿ Arc - 最近成绩 - 未绑定账户\n该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)')
            else:
                est = True
                user_id = result[0]
        elif ':' in msg[0] or '：' in msg[0]:
            user_id = msg[0][1:]
            if user_id.isdigit() and len(user_id) == 9:
                est = True
            else:
                await arcre.finish('▿ Arc - 最近成绩\n请您输入正确的好友码。')
        else:
            await arcre.finish('▿ Arc - 最近成绩\n仅可以使用好友码查询。')
    elif not result:
        await arcre.finish('▿ Arc - 最近成绩 - 未绑定账户\n该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)')
    elif result[1] == None:
        await arcre.finish('▿ Arc - 最近成绩 - 注意\n该账号已绑定但尚未添加为好友，请联系 Kiba 管理员添加好友并执行 arcup 指令')
    else:
        user_id = result[1]
    info = await draw_score(user_id, est)
    await arcre.send(info)

arcup = on_command("arcup", aliases={'arcupdate'})
@arcup.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if str(event.user_id) not in Config.superuser:
        await arcup.finish('▿ Arc - Update\n请联系BOT管理员更新')
        return
    msg = await newbind()
    await arcup.send(msg)

bind = on_command('arcbind')
@bind.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qqid = event.user_id
    arcid = str(event.get_message()).strip().split(" ")
    try:
        if not arcid[0].isdigit() and len(arcid[0]) != 9:
            await bind.finish('▿ Arc - 绑定\n请输入您的 arcid(好友码)')
        elif not arcid[1]:
            await bind.finish('▿ Arc - 绑定\n请输入您的 用户名')
    except IndexError:
        await bind.finish('▿ Arc - 绑定\n请重新输入好友码和用户名\n例如：arcbind 114514810 sb616')
    result = asql.get_user(qqid)
    if result:
        await bot.finish('▿ Arc - 绑定\n您已绑定，如需要解绑请输入 arcunbind。')
    msg = await bindinfo(qqid, arcid[0], arcid[1])
    await bind.send(msg)

unbind = on_command('arcunbind')
@unbind.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qqid = event.user_id
    result = asql.get_user(qqid)
    if result:
        if asql.delete_user(qqid):
            msg = '▾ Arc - 解除绑定\n解绑成功!'
        else:
            msg = '▿ Arc - 解除绑定\n数据库错误......'
    else:
        msg = '▿ Arc - 解除绑定\n您未绑定，无需解绑。'
    await unbind.send(msg)