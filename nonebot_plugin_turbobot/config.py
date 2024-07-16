from pydantic import BaseSettings, Field, validator

class Config(BaseSettings):
    database_path: str = Field(default='src/plugins/nonebot_plugin_turbobot/database/botKey.db')
    api_base_url: str = Field(default='https://api.mai-turbo.net')
    bot_name: str = Field(default="Salt二号机")
