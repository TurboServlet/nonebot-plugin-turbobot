import sqlite3
from datetime import datetime
from typing import Optional

from nonebot import get_driver

from ..config import Config

plugin_config = Config()


def get_connection():
    """
    @Author: TurboServlet
    @Func: get_connection()
    @Description: 获取数据库连接
    @Return: sqlite3.Connection
    """
    return sqlite3.connect(plugin_config.database_path)


def is_already_bound(qqid: str) -> bool:
    """
    @Author: TurboServlet
    @Func: is_already_bound()
    @Description: 检查用户是否已经绑定
    @Param {str} qqid: 用户QQ号
    @Return: bool
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM user WHERE QQID = ?', (qqid,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def get_bot_key(qqid: str) -> Optional[str]:
    """
    @Author: TurboServlet
    @Func: get_bot_key()
    @Description: 获取用户的bot_key
    @Param {str} qqid: 用户QQ号
    @Return: Optional[str]
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT bot_key FROM user WHERE QQID = ?', (qqid,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def bind_user(qqid: str, bot_token: str, bot_key: str):
    """
    @Author: TurboServlet
    @Func: bind_user()
    @Description: 绑定用户信息到数据库
    @Param {str} qqid: 用户的QQID（不是QQ号）
    @Param {str} bot_token: 用户的bot_token
    @Param {str} bot_key: 用户的bot_key
    """
    bind_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
    INSERT INTO user (QQID, bot_token, bot_key, bind_time) 
    VALUES (?, ?, ?, ?)
    ''',
        (qqid, bot_token, bot_key, bind_time),
    )
    conn.commit()
    conn.close()


def unbind_user(qqid: str):
    """
    @Author: TurboServlet
    @Func: unbind_user()
    @Description: 解除用户绑定
    @Param {str} qqid: 用户的QQID（不是QQ号）
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE QQID = ?", (qqid,))
    conn.commit()
    conn.close()
