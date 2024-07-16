import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import httpx
import nonebot
from nonebot import (
    get_bot,
    get_driver,
    on_command,
    on_endswith,
    on_message,
    on_regex,
    require,
)
from nonebot.adapters.qq import (  # type: ignore
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Endswith, RegexGroup, RegexMatched
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from pydantic import ValidationError

from .config import Config
from .libraries.db_utils import bind_user, get_bot_key, is_already_bound, unbind_user
from .network.models import Packets, ResponseData

plugin_config = Config()

__plugin_meta__ = PluginMetadata(
    name="turbo",
    description="给turbo用户提供指令服务的插件",
    usage="",
    type="application",
    extra={},
)


change_name = on_command('setName', aliases={'setname'}, priority=5)
remove_name = on_command('removeName', aliases={'removename'}, priority=5)
set_ticket = on_command('setTicket', aliases={'setticket'}, priority=5)
remove_ticket = on_command('removeTicket', aliases={'removeticket'}, priority=5)
bind = on_command('bind', priority=5)
unbind = on_command('unbind', priority=5)
network = on_command('network', priority=5)


@bind.handle()
async def handle_bind(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_bind()
    @Description: 处理用户绑定操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数
    """
    qqid = str(event.get_user_id())
    bot_token = str(arg).strip()

    if not bot_token:
        await bind.send("绑定命令后需要包含botToken。")
        return
    if is_already_bound(qqid):
        await bind.send("您已经绑定过一个bot_token，无需重复绑定。")
        return

    payload = {"botToken": bot_token, "botName": plugin_config.bot_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/bot/bind', json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("isSuccess"):
                bot_key = response_data["data"]["botKey"]
                bind_user(qqid, bot_token, bot_key)
                await bind.send("绑定成功！请及时撤回您的botToken信息！")
            else:
                await bind.send("绑定失败，返回响应中isSuccess为false。")
        elif response.status_code == 500:
            await bind.send("绑定失败，请检查botToken是否正确。")
        else:
            await bind.send(f"绑定失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await bind.send(f"绑定过程中出现错误：{e}")


@unbind.handle()
async def handle_unbind(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_unbind()
    @Description: 处理用户解绑操作
    @Param {MessageEvent} event: 消息事件
    """
    qqid = str(event.get_user_id())
    if not is_already_bound(qqid):
        await unbind.send("您还未绑定bot，无法解绑！")
        return
    bot_key = get_bot_key(qqid)
    payload = {"botKey": bot_key}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/bot/unbind', json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("isSuccess"):
                unbind_user(qqid)
                await unbind.send("解绑成功！")
            else:
                await unbind.send("解绑失败，返回响应中isSuccess为false。")
        else:
            await unbind.send(f"解绑失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await unbind.send(f"解绑过程中出现错误：{e}")


@change_name.handle()
async def handle_change_name(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_change_name()
    @Description: 处理用户修改名称操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数
    """
    qqid = str(event.get_user_id())
    new_name = str(arg).strip()

    if not new_name:
        await change_name.send("修改名称命令后需要包含新的名称。")
        return

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await change_name.send("您尚未绑定，请先使用/bind 指令绑定。")
        return

    payload = {"turboName": new_name}

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{plugin_config.api_base_url}/web/userOption/upsertUserName', json=payload, headers=headers
            )

        if response.status_code == 200:
            await change_name.send("名称修改成功！")
        elif response.status_code == 401:
            await change_name.send("修改名称失败，请检查权限。")
        else:
            await change_name.send(f"修改名称失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await change_name.send(f"修改名称过程中出现错误：{e}")


@remove_name.handle()
async def handle_remove_name(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_remove_name()
    @Description: 处理用户删除名称操作
    @Param {MessageEvent} event: 消息事件
    """
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await remove_name.send("您尚未绑定，请先使用/bind 指令绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/web/userOption/deleteUserName', headers=headers)

        if response.status_code == 200:
            await remove_name.send("名称删除成功！")
        elif response.status_code == 401:
            await remove_name.send("删除名称失败，请检查权限。")
        else:
            await remove_name.send(f"删除名称失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await remove_name.send(f"删除名称过程中出现错误：{e}")


@set_ticket.handle()
async def handle_set_ticket(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_set_ticket()
    @Description: 处理用户设置锁定功能票操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数
    """
    qqid = str(event.get_user_id())
    ticket_id_str = str(arg).strip()

    if not ticket_id_str.isdigit():
        await set_ticket.send("设置票的命令后需要跟一个数字作为ticketId。")
        return

    ticket_id = int(ticket_id_str)

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await set_ticket.send("您尚未绑定，请先绑定。")
        return

    payload = {"ticketId": ticket_id}

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{plugin_config.api_base_url}/web/userOption/upsertTicketWhitelist', json=payload, headers=headers
            )

        if response.status_code == 200:
            ticket_description = get_ticket_description(ticket_id)
            await set_ticket.send(f"用户功能票成功锁定为：{ticket_description}")
        elif response.status_code == 401:
            await set_ticket.send("设置票失败，请检查权限。")
        else:
            await set_ticket.send(f"设置票失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await set_ticket.send(f"设置票过程中出现错误：{e}")


@remove_ticket.handle()
async def handle_remove_ticket(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_remove_ticket()
    @Description: 处理用户取消锁定功能票操作
    @Param {MessageEvent} event: 消息事件
    """
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await remove_ticket.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{plugin_config.api_base_url}/web/userOption/deleteTicketWhitelist', headers=headers
            )

        if response.status_code == 200:
            await remove_ticket.send("用户功能票取消锁定成功！")
        elif response.status_code == 401:
            await remove_ticket.send("删除票失败，请检查权限。")
        else:
            await remove_ticket.send(f"删除票失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await remove_ticket.send(f"删除票过程中出现错误：{e}")


@network.handle()
async def handle_network(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_network()
    @Description: 处理用户获取网络数据操作
    @Param {MessageEvent} event: 消息事件
    """
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await network.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{plugin_config.api_base_url}/web/network', headers=headers)

        if response.status_code == 200:
            try:
                response_data = ResponseData(**response.json())
                if response_data.isSuccess:
                    packets = response_data.get_packets()
                    if packets:
                        total_exception_count = packets.retryExceptionCount + packets.zlibSkippedCount
                        exception_ratio = (
                            (total_exception_count / packets.allPacketNums * 100) if packets.allPacketNums > 0 else 0
                        )
                        black_room_probability = 1 - (1 - exception_ratio) ** 10
                        message = (
                            f"一小时内总包数：{packets.allPacketNums}\n"
                            f"一小时内总异常包数：{total_exception_count}\n"
                            f"一小时内异常包数占比：{exception_ratio:.2f}%\n"
                            f"Z-LIB 跳过数量：{packets.zlibSkippedCount}\n"
                            f"尝试重试数量：{packets.retryExceptionCount}\n"
                            f"尝试失败数量：{packets.panicCount}\n"
                            f"10pc至少有一次小黑屋的预估概率：{black_room_probability:.2%}\n\n"
                        )
                        message += (
                            "数据的异常率可以反应当前网络情况。\n"
                            "异常率超过「3%」时，可能会出现网络不稳定现象。\n"
                            "请求重试率和失败率较高时，网络或服务器可能存在问题。\n"
                            "小黑屋率为使用一小时异常率估算的数据，仅供参考。\n"
                        )
                        await network.send(message)
                    else:
                        await network.send("获取网络数据失败，返回的数据中不包含 packets 信息。")
                else:
                    await network.send("获取网络数据失败，返回响应中 isSuccess 为 false。")
            except ValidationError as e:
                await network.send(f"解析网络数据时出现错误：{e}")
        else:
            await network.send(f"获取网络数据失败，HTTP 响应状态码为 {response.status_code}。")
    except Exception as e:
        await network.send(f"获取网络数据过程中出现错误：{e}")


def get_ticket_description(ticket_id: int) -> str:
    """
    @Author: TurboServlet
    @Func: get_ticket_description()
    @Description: 获取功能票的描述信息
    @Param {int} ticket_id: 票的ID
    @Return: str
    """
    ticket_descriptions = {
        2: '付费2倍票',
        3: '付费3倍票',
        4: '付费4倍票',
        5: '付费5倍票',
        6: '付费6倍票',
        10005: '活动5倍票 (类型1)',
        10105: '活动5倍票 (类型2)',
        10205: '活动5倍票 (类型3)',
        11001: '免费1.5倍票',
        11002: '免费2倍票',
        11003: '免费3倍票',
        11005: '免费5倍票',
        30001: '特殊2倍票',
        'default': '没有票',
    }
    return ticket_descriptions.get(ticket_id, ticket_descriptions['default'])
