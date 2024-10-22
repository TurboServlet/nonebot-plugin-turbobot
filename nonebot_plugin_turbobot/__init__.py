from datetime import datetime
import html

import httpx
from nonebot import (
    on_command,
)
from nonebot.adapters.qq import (  # type: ignore
    Message,
    MessageEvent,
)
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .config import Config
from .libraries.db_utils import bind_user, get_bot_key, is_already_bound, unbind_user
from .permission.models import UserPermission

plugin_config = Config()

__plugin_meta__ = PluginMetadata(
    name="turbo",
    description="给turbo用户提供指令服务的插件",
    usage="",
    type="application",
    extra={},
)

help = on_command('help', aliases={'帮助'}, priority=5)
set_name = on_command('setName', aliases={'setname', '设置名称', '修改名称'}, priority=5)
reset_name = on_command('resetName', aliases={'resetname', '重置名称', '删除名称'}, priority=5)
show_name = on_command('name', aliases={'showName', '查询名称', '查看名称'}, priority=5)
set_ticket = on_command('setTicket', aliases={'setticket', '设置票', '锁定票'}, priority=5)
reset_ticket = on_command('resetTicket', aliases={'resetticket', '重置票', '取消票'}, priority=5)
show_ticket = on_command('ticket', aliases={'showTicket', '查询票', '查看票'}, priority=5)
bind = on_command('bind', aliases={'绑定'}, priority=5)
unbind = on_command('unbind', aliases={'解绑'}, priority=5)
network = on_command('network', aliases={'网络状态', '查询网络'}, priority=5)
show_permission = on_command('showPermission', aliases={'permission', '获取权限', '展示权限', '权限', '权限查询'}, priority=5)
show_friends = on_command('showFriends', aliases={'showfriends', 'friends', 'friendslist','好友', '好友列表', '查询好友', '查看好友'}, priority=5)
show_friend_requests = on_command('showFriendRequests', aliases={'showfriendrequests', '好友请求', '好友请求列表', '查询好友请求'}, priority=5)
add_friend = on_command('addFriend', aliases={'addfriend', 'add', '加好友', '添加好友', '好友添加'}, priority=5)
accept_friend = on_command('acceptFriend', aliases={'acceptfriend', 'accept', '同意好友', '同意好友申请', '同意好友请求', '接受好友请求'}, priority=5)
deny_friend = on_command('denyFriend', aliases={'denyfriend', 'deny', '拒绝好友', '拒绝好友请求', '拒绝好友申请'}, priority=5)
remove_friend = on_command('removeFriend', aliases={'removefriend', 'remove', '删除好友', '移除好友'}, priority=5)
arcade_info_detail = on_command('arcadeInfo', aliases={'arcadeinfo', 'info', 'arcade', '机厅', '查卡', '机厅信息'})

@help.handle()
async def handle_help(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_help()
    @Description: 输出所有指令的帮助信息
    @Param {MessageEvent} event: 消息事件
    """
    
    help_message = """
指令帮助信息：
1. /setName 或 /设置名称 或 /修改名称 - 设置您的名称
2. /resetName 或 /重置名称 或 /删除名称 - 重置或删除您的名称
3. /name 或 /查询名称 或 /查看名称 - 查看当前名称
4. /setTicket 或 /设置票 或 /锁定票 - 锁定功能票
5. /resetTicket 或 /重置票 或 /取消票 - 重置功能票
6. /ticket 或 /查询票 或 /查看票 - 查看功能票状态
7. /bind 或 /绑定 - 绑定您的Turbo账号
8. /unbind 或 /解绑 - 解绑您的Turbo账号
9. /network 或 /网络状态 或 /查询网络 - 查看当前网络状态
10. /showPermission 或 /权限查询 - 显示您的权限信息
11. /showFriends 或 /好友 或 /好友列表 或 /查询好友 或 /查看好友 - 查看您的好友列表
12. /showFriendRequests 或 /好友请求 或 /查询好友请求 - 查看待处理的好友请求
13. /addFriend 或 /加好友 或 /添加好友 或 /好友添加 - 添加好友
14. /acceptFriend 或 /同意好友 或 /接受好友请求 - 接受好友请求
15. /denyFriend 或 /拒绝好友请求 - 拒绝好友请求
16. /removeFriend 或 /删除好友 或 /移除好友 - 删除好友
17. /info 或 /机厅 或 /查卡 - 查询机厅信息
    """
    
    await help.send(help_message)


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
            bot_key = response_data["botKey"]
            bind_user(qqid, bot_token, bot_key)
            await bind.send("绑定成功！请及时撤回您的botToken信息！")
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
            unbind_user(qqid)
            await unbind.send("解绑成功！")
        else:
            await unbind.send(f"解绑失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await unbind.send(f"解绑过程中出现错误：{e}")


@set_name.handle()
async def handle_set_name(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_set_name()
    @Description: 处理用户修改maimai名称操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数
    """
    qqid = str(event.get_user_id())
    new_name = str(arg).strip()

    if not new_name:
        await set_name.send("修改名称命令后需要包含新的名称。")
        return

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await set_name.send("您尚未绑定，请先使用/bind 指令绑定。")
        return

    payload = {"maimaiName": new_name}

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{plugin_config.api_base_url}/web/setMaimaiName', json=payload, headers=headers
            )

        if response.status_code == 200:
            await set_name.send("名称修改成功！")
        elif response.status_code == 400:
            await set_name.send("修改名称失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await set_name.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await set_name.send("权限不足，无法修改名称。")
        elif response.status_code == 410:
            await set_name.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await set_name.send(f"{error_message}")
        else:
            await set_name.send(f"修改名称失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await set_name.send(f"修改名称过程中出现错误：{e}")



@reset_name.handle()
async def handle_reset_name(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_reset_name()
    @Description: 处理用户重置名称操作
    @Param {MessageEvent} event: 消息事件
    """
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await reset_name.send("您尚未绑定，请先使用/bind 指令绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/web/resetMaimaiName', headers=headers)

        if response.status_code == 200:
            await reset_name.send("名称重置成功！")
        elif response.status_code == 400:
            await reset_name.send("重置名称失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await reset_name.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await reset_name.send("权限不足，无法重置名称。")
        elif response.status_code == 410:
            await reset_name.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await reset_name.send(f"{error_message}")
        else:
            await reset_name.send(f"重置名称失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await reset_name.send(f"重置名称过程中出现错误：{e}")

@show_name.handle()
async def handle_show_name(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_show_name()
    @Description: 处理用户查询当前名称操作
    @Param {MessageEvent} event: 消息事件
    """

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_name.send("您尚未绑定，请先绑定。")
        return

    headers = {
        "Authorization": f"BotKey {bot_key}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{plugin_config.api_base_url}/web/showMaimaiName', headers=headers)

            if response.status_code == 200:
                current_name = response.text
                await show_name.send(f"您当前的ID为：{current_name}")
            elif response.status_code == 400:
                await show_name.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_name.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_name.send("权限不足，无法获取当前ID。")
            elif response.status_code == 410:
                await show_name.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_name.send(f"{error_message}")
            else:
                await show_name.send(f"获取ID失败，HTTP响应状态码为：{response.status_code}。")
    except Exception as e:
        await show_name.send(f"获取ID过程中出现错误：{e}")



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
                f'{plugin_config.api_base_url}/web/setTickets', json=payload, headers=headers
            )

        if response.status_code == 200:
            ticket_description = get_ticket_description(ticket_id)
            await set_ticket.send(f"用户功能票成功锁定为：{ticket_description}")
        elif response.status_code == 400:
            await set_ticket.send("设置票失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await set_ticket.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await set_ticket.send("权限不足，无法设置票。")
        elif response.status_code == 410:
            await set_ticket.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await set_ticket.send(f"{error_message}")
        else:
            await set_ticket.send(f"设置票失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await set_ticket.send(f"设置票过程中出现错误：{e}")



@reset_ticket.handle()
async def handle_reset_ticket(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_reset_ticket()
    @Description: 处理用户取消锁定功能票操作
    @Param {MessageEvent} event: 消息事件
    """
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await reset_ticket.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{plugin_config.api_base_url}/web/resetTickets', headers=headers
            )

        if response.status_code == 200:
            await reset_ticket.send("用户功能票取消锁定成功！")
        elif response.status_code == 400:
            await reset_ticket.send("取消票失败，验证码验证失败或数据不合法。")
        elif response.status_code == 401:
            await reset_ticket.send("请求的Token缺失或不合法，请检查权限。")
        elif response.status_code == 403:
            await reset_ticket.send("权限不足，无法取消票。")
        elif response.status_code == 410:
            await reset_ticket.send("该用户已被封禁，请联系管理员。")
        elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await reset_ticket.send(f"{error_message}")
        else:
            await reset_ticket.send(f"取消票失败，HTTP响应状态码为{response.status_code}。")
    except Exception as e:
        await reset_ticket.send(f"取消票过程中出现错误：{e}")

@show_ticket.handle()
async def handle_show_ticket(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_show_ticket()
    @Description: 处理用户查询当前功能票信息操作
    @Param {MessageEvent} event: 消息事件
    """

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_ticket.send("您尚未绑定，请先绑定。")
        return

    headers = {
        "Authorization": f"BotKey {bot_key}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{plugin_config.api_base_url}/web/currentTickets', headers=headers)

            if response.status_code == 200:
                ticket_data = response.json()

                turbo_ticket = ticket_data.get("turboTicket", {})
                is_enable = turbo_ticket.get("isEnable", False)
                ticket_id = turbo_ticket.get("ticketId", 0)

                if is_enable:
                    ticket_description = get_ticket_description(ticket_id)
                    message = f"已启用功能票锁定，当前锁定功能票为：{ticket_description}\n"
                else:
                    message = "未启用功能票锁定\n"

                maimai_tickets = ticket_data.get("maimaiTickets", [])
                available_tickets = []

                for ticket in maimai_tickets:
                    stock = ticket.get("stock", 0)
                    if stock > 0:
                        ticket_desc = get_ticket_description(ticket.get("ticketId", 0))
                        available_tickets.append(f"{ticket_desc}：{stock}张")

                if available_tickets:
                    message += "\n账号内功能票库存：\n" + "\n".join(available_tickets)

                await show_ticket.send(message)
            elif response.status_code == 400:
                await show_ticket.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_ticket.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_ticket.send("权限不足，无法获取功能票信息。")
            elif response.status_code == 410:
                await show_ticket.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_ticket.send(f"{error_message}")
            else:
                await show_ticket.send(f"获取功能票信息失败，HTTP响应状态码为：{response.status_code}。")
    except Exception as e:
        await show_ticket.send(f"获取功能票信息过程中出现错误：{e}")


@network.handle()
async def handle_network(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_network()
    @Description: 处理获取网络相关信息的操作
    @Param {Event} event: 事件信息
    """

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)
    
    if not bot_key:
        await network.send("您尚未绑定，请先绑定。")
        return

    headers = {
        "Authorization": f"BotKey {bot_key}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response_network = await client.get('https://api.mai-turbo.net/web/showServerRequests', headers=headers)

            if response_network.status_code == 200:
                network_data = response_network.json()

                if network_data:
                    all_requests_count = network_data.get("requestsCount", 0)
                    exception_requests_count = network_data.get("exceptionRequestsCount", 0)
                    zlib_skipped_requests_count = network_data.get("zlibSkippedRequestsCount", 0)
                    retry_requests_count = network_data.get("retryRequestsCount", 0)
                    panic_requests_count = network_data.get("panicRequestsCount", 0)
                    exception_requests_rate = network_data.get("exceptionRequestsRate", 0)
                    black_room_probability = 1 - (1 - exception_requests_rate / 100) ** 10

                    message = (
                        f"\n一小时内总请求数：{all_requests_count}\n"
                        f"异常请求数：{exception_requests_count}\n"
                        f"异常请求占比：{exception_requests_rate:.2f}%\n"
                        f"Z-LIB 跳过数量：{zlib_skipped_requests_count}\n"
                        f"重试请求数：{retry_requests_count}\n"
                        f"失败请求数：{panic_requests_count}\n\n"
                        f"10pc至少有一次小黑屋的预估概率：{black_room_probability:.2%}\n\n"
                    )
                    message += (
                        "响应数据的「Z-LIB」压缩跳过率与请求重试次数可以反应当前网络情况。\n"
                        "压缩跳过率超过「3%」时，可能会出现网络不稳定现象。\n"
                        "请求重试率和失败率较高时，网络或服务器可能存在问题。\n"
                        "小黑屋率为使用一小时异常率估算的数据，仅供参考。"
                    )

                    await network.send(message)
                else:
                    await network.send("获取网络数据失败。")
            elif response_network.status_code == 400:
                await network.send("请求数据不合法，请检查请求。")
            elif response_network.status_code == 401:
                await network.send("请求的Token缺失或不合法，请检查权限。")
            elif response_network.status_code == 403:
                await network.send("权限不足，无法获取网络数据。")
            elif response_network.status_code == 410:
                await network.send("该用户已被封禁，请联系管理员。")
            elif response_network.status_code == 500:
                error_message = response_network.json().get("message", "服务器内部错误")
                await network.send(f"{error_message}")
            else:
                await network.send(f"获取数据失败，HTTP响应状态码为：{response_network.status_code}。")
    except Exception as e:
        await network.send(f"获取数据过程中出现错误：{e}")


@show_permission.handle()
async def handle_show_permission(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_show_permission()
    @Description: 处理用户获取权限操作
    @Param {MessageEvent} event: 消息事件
    """
    qqid = str(event.get_user_id())

    bot_key = get_bot_key(qqid)
    if not bot_key:
        await show_permission.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{plugin_config.api_base_url}/permission/showPermission', headers=headers)

            if response.status_code == 200:
                permission_text = response.text.strip().replace('"', '')
                response_data = UserPermission(permission=permission_text)
                permission_level = response_data.get_permission_level()
                message = f"用户权限级别：{permission_level}\n"
            elif response.status_code == 400:
                await show_permission.send("请求数据不合法，请检查请求。")
                return
            elif response.status_code == 401:
                await show_permission.send("请求的Token缺失或不合法，请检查权限。")
                return
            elif response.status_code == 403:
                await show_permission.send("权限不足，无法获取权限信息。")
                return
            elif response.status_code == 410:
                await show_permission.send("该用户已被封禁，请联系管理员。")
                return
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_permission.send(f"{error_message}")
                return
            else:
                await show_permission.send(f"获取权限信息失败，HTTP响应状态码为 {response.status_code}。")
                return

            response_turbo = await client.get(f'{plugin_config.api_base_url}/web/showTurboPermission', headers=headers)

            if response_turbo.status_code == 200:
                turbo_permissions = response_turbo.json()
                if turbo_permissions:
                    granted_permissions = []
                    for permission in turbo_permissions:
                        description = permission.get("permissionDescription", "未知权限")
                        is_granted = permission.get("isGranted", False)
                        if is_granted:
                            description = html.unescape(description)
                            granted_permissions.append(description)

                    if granted_permissions:
                        message += "\n已授予的详细权限：\n" + "\n".join(granted_permissions)
                    else:
                        message += "\n未授予任何详细权限。"
                else:
                    message += "\n无法获取详细权限信息。"
            elif response_turbo.status_code == 400:
                message += "\n请求数据不合法，请检查请求。"
            elif response_turbo.status_code == 401:
                message += "\n请求的Token缺失或不合法，请检查权限。"
            elif response_turbo.status_code == 403:
                message += "\n权限不足，无法获取详细Turbo权限信息。"
            elif response_turbo.status_code == 410:
                message += "\n该用户已被封禁，请联系管理员。"
            elif response_turbo.status_code == 500:
                error_message = response_turbo.json().get("message", "服务器内部错误")
                message += f"\n{error_message}"
            else:
                message += f"\n获取详细Turbo权限失败，HTTP响应状态码为 {response_turbo.status_code}。"

            await show_permission.send(message)

    except Exception as e:
        await show_permission.send(f"获取用户权限过程中出现错误：{e}")

@show_friends.handle()
async def handle_show_friends(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_show_friends()
    @Description: 处理用户获取好友列表操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 命令参数（可选）
    """

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)
    
    page_str = str(arg).strip()
    if page_str.isdigit():
        page = int(page_str)
    else:
        page = 1

    if not bot_key:
        await show_friends.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{plugin_config.api_base_url}/web/showFriends', params={"page": page}, headers=headers)

            if response.status_code == 200:
                friends_data = response.json()

                content = friends_data.get("content", [])
                total_elements = friends_data.get("totalElements", 0)
                total_pages = friends_data.get("totalPages", 0)

                if not content:
                    await show_friends.send("您目前还没有添加好友。")
                    return

                friend_names = [friend["turboName"] for friend in content]
                friend_list_message = "好友列表：\n" + "\n".join(friend_names)

                message = (
                    f"{friend_list_message}\n\n"
                    f"共 {total_elements} 位好友，当前 {page}/{total_pages} 页。"
                )

                if total_pages > 1:
                    message += "\n可以在命令后添加页数查看对应页数的好友。"

                await show_friends.send(message)

            elif response.status_code == 400:
                await show_friends.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_friends.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_friends.send("权限不足，无法获取好友列表。")
            elif response.status_code == 410:
                await show_friends.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_friends.send(f"{error_message}")
            else:
                await show_friends.send(f"获取好友列表失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await show_friends.send(f"获取好友列表过程中出现错误：{e}")

@show_friend_requests.handle()
async def handle_show_friend_requests(event: MessageEvent):
    """
    @Author: TurboServlet
    @Func: handle_show_friend_requests()
    @Description: 处理用户获取好友请求操作
    @Param {MessageEvent} event: 消息事件
    """

    qqid = str(event.get_user_id())
    bot_key = get_bot_key(qqid)

    if not bot_key:
        await show_friend_requests.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{plugin_config.api_base_url}/web/showFriendRequests', headers=headers)

            if response.status_code == 200:
                friend_requests = response.json()

                if not friend_requests:
                    await show_friend_requests.send("当前没有待处理的好友请求。")
                    return

                requests_message = "好友请求列表：\n"
                for request in friend_requests:
                    turbo_name = request.get("turboName", "未知用户")
                    request_time = request.get("requestTime", "")

                    try:
                        formatted_time = datetime.strptime(request_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d %H:%M:%S")
                    except ValueError:
                        formatted_time = request_time

                    requests_message += f"{turbo_name} - 请求时间：{formatted_time}\n"

                await show_friend_requests.send(requests_message)

            elif response.status_code == 400:
                await show_friend_requests.send("请求数据不合法，请检查请求。")
            elif response.status_code == 401:
                await show_friend_requests.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await show_friend_requests.send("权限不足，无法获取好友请求。")
            elif response.status_code == 410:
                await show_friend_requests.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await show_friend_requests.send(f"{error_message}")
            else:
                await show_friend_requests.send(f"获取好友请求失败，HTTP响应状态码为 {response.status_code}。")

    except Exception as e:
        await show_friend_requests.send(f"获取好友请求过程中出现错误：{e}")

@add_friend.handle()
async def handle_add_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_add_friend()
    @Description: 处理用户添加好友操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """

    qqid = str(event.get_user_id())
    turbo_name = str(arg).strip()

    if not turbo_name:
        await add_friend.send("请提供要添加好友的名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await add_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/web/addFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await add_friend.send(f"好友请求已发送给：{turbo_name}")
            elif response.status_code == 400:
                await add_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await add_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await add_friend.send("权限不足，无法添加好友。")
            elif response.status_code == 410:
                await add_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await add_friend.send(f"{error_message}")
            else:
                await add_friend.send(f"添加好友失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await add_friend.send(f"添加好友过程中出现错误：{e}")

@accept_friend.handle()
async def handle_accept_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_accept_friend()
    @Description: 处理用户接受好友请求操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """

    qqid = str(event.get_user_id())
    turbo_name = str(arg).strip()

    if not turbo_name:
        await accept_friend.send("请提供要接受好友请求的名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await accept_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/web/acceptFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await accept_friend.send(f"您已接受 {turbo_name} 的好友请求。")
            elif response.status_code == 400:
                await accept_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await accept_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await accept_friend.send("权限不足，无法接受好友请求。")
            elif response.status_code == 410:
                await accept_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await accept_friend.send(f"{error_message}")
            else:
                await accept_friend.send(f"接受好友请求失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await accept_friend.send(f"接受好友请求过程中出现错误：{e}")

@deny_friend.handle()
async def handle_deny_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_deny_friend()
    @Description: 处理用户拒绝好友请求操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """

    qqid = str(event.get_user_id())
    turbo_name = str(arg).strip()

    if not turbo_name:
        await deny_friend.send("请提供要拒绝的好友请求的名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await deny_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/web/denyFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await deny_friend.send(f"您已拒绝 {turbo_name} 的好友请求。")
            elif response.status_code == 400:
                await deny_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await deny_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await deny_friend.send("权限不足，无法拒绝好友请求。")
            elif response.status_code == 410:
                await deny_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await deny_friend.send(f"{error_message}")
            else:
                await deny_friend.send(f"拒绝好友请求失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await deny_friend.send(f"拒绝好友请求过程中出现错误：{e}")

@remove_friend.handle()
async def handle_remove_friend(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_remove_friend()
    @Description: 处理用户删除好友操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: 用户输入的好友名称
    """

    qqid = str(event.get_user_id())
    turbo_name = str(arg).strip()

    if not turbo_name:
        await remove_friend.send("请提供要删除的好友名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await remove_friend.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    payload = {"turboName": turbo_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{plugin_config.api_base_url}/web/removeFriend', json=payload, headers=headers)

            if response.status_code == 200:
                await remove_friend.send(f"您已成功删除好友：{turbo_name}")
            elif response.status_code == 400:
                await remove_friend.send("请求数据不合法，请检查输入的好友名称。")
            elif response.status_code == 401:
                await remove_friend.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await remove_friend.send("权限不足，无法删除好友。")
            elif response.status_code == 410:
                await remove_friend.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await remove_friend.send(f"{error_message}")
            else:
                await remove_friend.send(f"删除好友失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await remove_friend.send(f"删除好友过程中出现错误：{e}")

@arcade_info_detail.handle()
async def handle_arcade_info_detail(event: MessageEvent, arg: Message = CommandArg()):
    """
    @Author: TurboServlet
    @Func: handle_arcade_info_detail()
    @Description: 处理用户获取机厅信息操作
    @Param {MessageEvent} event: 消息事件
    @Param {Message} arg: arcadeName 参数
    """
    
    qqid = str(event.get_user_id())
    arcade_name = str(arg).strip()

    if not arcade_name:
        await arcade_info_detail.send("请提供要查询的机厅名称。")
        return

    bot_key = get_bot_key(qqid)

    if not bot_key:
        await arcade_info_detail.send("您尚未绑定，请先绑定。")
        return

    headers = {"Authorization": f"BotKey {bot_key}"}
    params = {"arcadeName": arcade_name}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{plugin_config.api_base_url}/web/arcadeInfoDetail', params=params, headers=headers)

            if response.status_code == 200:
                arcade_data = response.json()

                arcade_info = arcade_data.get("arcadeInfo", {})
                arcade_name_display = arcade_info.get("arcadeName", "未知机厅")
                
                thirty_minutes_player = arcade_data.get("thirtyMinutesPlayer", 0)
                one_hour_player = arcade_data.get("oneHourPlayer", 0)
                two_hours_player = arcade_data.get("twoHoursPlayer", 0)
                thirty_minutes_play_count = arcade_data.get("thirtyMinutesPlayCount", 0)
                one_hour_play_count = arcade_data.get("oneHourPlayCount", 0)
                two_hours_play_count = arcade_data.get("twoHoursPlayCount", 0)

                player_list = arcade_data.get("playerList", [])
                recent_players = [player.get("maimaiName", "未知玩家") for player in player_list[:6]]

                arcade_requested = arcade_info.get("arcadeRequested", 0)
                arcade_cached_request = arcade_info.get("arcadeCachedRequest", 0)
                arcade_fixed_request = arcade_info.get("arcadeFixedRequest", 0)
                arcade_cached_hit_rate = arcade_info.get("arcadeCachedHitRate", 0)

                cache_hit_rate = (arcade_cached_hit_rate / 100) if arcade_cached_hit_rate > 0 else 0
                error_fix_rate = (arcade_fixed_request / arcade_requested * 100) if arcade_requested > 0 else 0

                message = (
                    f"{arcade_name_display}\n\n"
                    f"30 分钟内有 {thirty_minutes_player} 名玩家，共 {thirty_minutes_play_count} pc\n"
                    f"1 小时内有 {one_hour_player} 名玩家，共 {one_hour_play_count} pc\n"
                    f"2 小时内有 {two_hours_player} 名玩家，共 {two_hours_play_count} pc\n\n"
                )

                if recent_players:
                    message += "最近游玩的 6 名玩家：\n" + "\n".join(recent_players) + "\n\n"
                else:
                    message += "最近游玩的 6 名玩家：无\n\n"

                message += (
                    f"在 {arcade_requested} 次网络请求中，缓存击中 {arcade_cached_request} 次，"
                    f"修复 {arcade_fixed_request} 次错误，缓存击中率 {cache_hit_rate:.2%}，"
                    f"缓外错误率 {error_fix_rate:.2%}"
                )

                await arcade_info_detail.send(message)

            elif response.status_code == 400:
                await arcade_info_detail.send("请求数据不合法，请检查机厅名称。")
            elif response.status_code == 401:
                await arcade_info_detail.send("请求的Token缺失或不合法，请检查权限。")
            elif response.status_code == 403:
                await arcade_info_detail.send("权限不足，无法获取机厅信息。")
            elif response.status_code == 410:
                await arcade_info_detail.send("该用户已被封禁，请联系管理员。")
            elif response.status_code == 500:
                error_message = response.json().get("message", "服务器内部错误")
                await arcade_info_detail.send(f"{error_message}")
            else:
                await arcade_info_detail.send(f"获取机厅信息失败，HTTP响应状态码为 {response.status_code}。")
    except Exception as e:
        await arcade_info_detail.send(f"获取机厅信息过程中出现错误：{e}")


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
