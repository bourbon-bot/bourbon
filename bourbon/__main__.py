from __future__ import annotations
from typing import TYPE_CHECKING

from nextcord.ext import commands
from nextcord import HTTPException
from logging import getLogger, StreamHandler
from dotenv import load_dotenv

load_dotenv()

from os import environ

__all__ = "Bourbon"

if TYPE_CHECKING:
    from bourbon.typehint import Self, Context, E
    from typing import List
    from logging import Logger

_log: Logger = getLogger("nextcord")
_log.addHandler(StreamHandler())


class Bourbon(commands.Bot):
    def __init__(self: Self) -> None:
        super().__init__(command_prefix="b!")

    def __load_bot_extensions(self: Self):
        self.load_extension("exts.moderation")

    def _format_missing_permissions_codeblock(
        self: Self, missing_perms: List[str]
    ) -> str:
        return """```{}```""".format("\n".join(missing_perms))

    async def on_command_error(self: Self, ctx: Context, exception: E) -> None:
        if isinstance(exception, commands.NoPrivateMessage):
            await ctx.send("This can't be used in private messages.")
        if isinstance(exception, HTTPException):
            await ctx.send(
                "You messed up with the bot. An error was occured. Good job."
            )
            await super().on_command_error(ctx, exception)
        if isinstance(exception, commands.MissingPermissions):
            await ctx.send(
                "You are missing some permissions!"
                + self._format_missing_permissions_codeblock(
                    exception.missing_permissions
                )
            )
        if isinstance(exception, commands.BotMissingPermissions):
            await ctx.send(
                "I am missing some permissions!" + 
                self._format_missing_permissions_codeblock(
                    exception.missing_permissions
                )
            )
        super().on_command_error(ctx, exception)
        


bourbon = Bourbon()
bourbon.run(environ["TOKEN"])
