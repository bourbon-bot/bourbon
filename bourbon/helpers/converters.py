from __future__ import annotations
# from nextcord.ext import commands
# from bourbon.typehint import Context
from typing import TYPE_CHECKING
from dateparser import parse
if TYPE_CHECKING:
    from typing import Self, Callable
    from datetime import datetime
__all__ = "TimeConverter"
class TimeConverter:
    @classmethod
    async def convert(cls: TimeConverter, argument: str) -> datetime:
        return parse(argument)



