from nextcord.ext import commands
from typing_extensions import Self
from typing import TypeVar

__all__ = ("Context", "Self", "E")
Context = commands.Context
E = TypeVar("E", bound=Exception)
