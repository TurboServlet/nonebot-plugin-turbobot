from pydantic import BaseModel
from typing import Optional

class Packets(BaseModel):
    allPacketNums: int
    retryExceptionCount: int
    zlibSkippedCount: int
    panicCount: int

class ResponseData(BaseModel):
    isSuccess: bool
    data: Optional[dict]

    def get_packets(self) -> Optional[Packets]:
        if self.data and "packets" in self.data:
            return Packets(**self.data["packets"])
        return None
