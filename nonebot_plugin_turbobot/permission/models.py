from typing import Optional

from pydantic import BaseModel


class UserPermission(BaseModel):
    isSuccess: bool
    data: Optional[str]

    def get_permission_level(self) -> str:
        if self.data:
            permission_level = self.data
            if permission_level == "ADMIN":
                return "全权管理员"
            elif permission_level == "BUILDER":
                return "技术实施员"
            elif permission_level == "AUTHORIZER":
                return "许可用户"
            elif permission_level == "USER":
                return "标准用户"
            elif permission_level == "BANNED":
                return "封禁中"
            else:
                return "未知"
        return "未知"
