# nonebot2-plugin-turbobot
## 简介

Turbo Bot 是一个为 Turbo 用户提供指令服务的 Nonebot 插件。通过该插件，用户可以进行设置和管理用户功能票等操作。

## 功能

- 绑定和解绑用户的 botToken
- 修改和删除用户名称
- 设置和删除用户功能票
- 获取网络数据

## 安装

1. 克隆此仓库到你的本地机器：
    ```sh
    git clone https://github.com/TurboServlet/nonebot2-plugin-turbobot.git
    ```

2. 将插件文件夹放入 Nonebot 目录下的 plugins 文件夹中

## 使用方法

- 使用 `/bind` 指令绑定，后面跟上你的 botToken。
- 使用 `/unbind` 指令解绑。
- 使用 `/setName` 指令修改你的名称，后面跟上新的名称。
- 使用 `/removeName` 指令删除你修改的名称。
- 使用 `/setTicket` 指令锁定你的用户功能票，后面跟上 ticketId。
- 使用 `/removeTicket` 指令删除你的用户功能票锁定。
- 使用 `/network` 指令获取网络数据。

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

如有任何问题，请提交 issues 或通过以下方式联系我：

- 邮箱: yuuluo@hotmail.com
- GitHub: [YuuLuo](https://github.com/YuuLuo)