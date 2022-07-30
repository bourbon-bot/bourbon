from __future__ import annotations

from typing import TYPE_CHECKING

from nextcord.ext import commands, application_checks as checks
from nextcord import User, slash_command, SlashOption
from helpers.flags import BaseFlag
from helpers.converters import TimeConverter
from datetime import timedelta

if TYPE_CHECKING:
    from typing import Union, Optional
    from bourbon.__main__ import Bourbon
    from bourbon.typehint import Context, Self
    from nextcord import Member, Interaction
    from datetime import datetime

__all__ = "Moderation"


class BaseModerationFlag(BaseFlag):
    reason: Optional[str] = commands.flag(name="reason", default=lambda ctx: None)


class BanFlag(BaseModerationFlag):
    delete_message_days: Optional[int] = commands.flag(
        name="delete_message_days", default=lambda ctx: 3
    )


class TimeoutFlag(BaseModerationFlag):
    until: Optional[str] = commands.flag(
        name="until", default=lambda ctx: ctx.message.created_at + timedelta(hour=1)
    )


class Moderation(commands.Cog):
    def __init__(self: Self, bot: Bourbon) -> None:
        self._bot: Bourbon = bot

    _invoke_reason = "Action done by {} (ID {})"
    _invoke_reason_with_uinput_reason = "Action done by {} (ID {}): {}"
    _bot_success_respond: str = "[OK] Action succeeded."

    @slash_command()
    async def moderation(self: Self, interaction: Interaction):
        """Moderation related commands."""
        pass

    def _is_executable(
        self: Self, *, bot: Member, user: Member, target: Union[Member, User]
    ) -> bool:
        """
        Check if one can execute moderative action on another user.

        This check follows these following ways:
        1. Check if the target is not in the server (returns True if condition met).
        2. Check if the target have admin permissions (returns False if condition met).
        3. Check if the taget's top role position is higher than the bot's top role position. (returns False if condition met).
        4. Check if the target's top role position is higher than the executor's top role position. (returns False if condition met).
        5. Check if the target is the server owner (returns False if condition met).

        All other condition should be treated as True.
        """
        if isinstance(target, User):
            return True
        if target.guild_permissions.administrator:
            return False
        if target.top_role > bot.top_role:
            return False
        if target.top_role > user.top_role:
            return False
        if target.id == bot.guild.owner_id:
            return False
        return True

    def _format_reason(self: Self, author: Member, reason: Optional[str] = None) -> str:
        """Format a reason to show up on the audit log."""
        if reason is None:
            return self._invoke_reason.format(str(author), author.id)
        else:
            return self._invoke_reason_with_uinput_reason.format(
                str(author), author.id, reason
            )

    @moderation.subcommand(name="ban", dm_permission=False)
    @checks.bot_has_guild_permissions(ban_members=True)
    @checks.has_guild_permissions(ban_members=True)
    async def ban_slash(
        self: Self,
        interaction: Interaction,
        member: Member = SlashOption(description="The member to ban.", required=False),
        reason: Optional[str] = SlashOption(
            description="The reason to ban this member", required=False
        ),
        delete_message_days: Optional[int] = SlashOption(
            description="The number of days to delete message from. Default to 3.",
            required=False,
            default=3,
        ),
    ):
        if not self._is_executable(
            bot=interaction.guild.me, user=interaction.user, target=member
        ):
            return await interaction.send(
                "You or the bot's permission are not high enough to target this member."
            )
        reason = self._format_reason(interaction.user, reason)
        await interaction.guild.ban(
            member, reason=reason, delete_message_days=delete_message_days
        )

    @commands.command()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(
        self: Self, ctx: Context, member: commands.UserConverter, flags: BanFlag
    ) -> None:
        """Ban a member from your server. Your name and ID will be shown up on the audit log."""
        if not self._is_executable(bot=ctx.guild.me, user=ctx.author, target=member):
            return await ctx.send(
                "You or the bot's permission are not high enough to target this member."
            )
        reason = self._format_reason(ctx.author, flags.reason)
        await ctx.guild.ban(
            member, reason=reason, delete_message_days=flags.delete_message_days
        )
        await ctx.send(self._bot_success_respond)

    @commands.command()
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    async def kick(
        self: Self,
        ctx: Context,
        member: commands.UserConverter,
        flags: BaseModerationFlag,
    ):
        """Kick a member from your server. Your name and ID will be shown up on the audit log."""
        if not self._is_executable(bot=ctx.guild.me, user=ctx.author, target=member):
            return await ctx.send(
                "You or the bot's permission are not high enough to target this member."
            )
        reason = self._format_reason(ctx.author, flags.reason)
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(self._bot_success_respond)

    @commands.command(aliases=["mute"])
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.has_guild_permissions(moderate_members=True)
    async def timeout(
        self: Self, ctx: Context, member: commands.MemberConverter, flags: TimeoutFlag
    ):
        """Time-out an user. The user's highest role must not be higher than you and the bot."""
        if not self._is_executable(bot=ctx.guild.me, user=ctx.author, target=member):
            return await ctx.send(
                "You or the bot's permission are not high enough to target this member."
            )
        time_to_timeout: datetime = TimeConverter.convert(flags.until)
        reason = self._format_reason(flags.reason)
        await member.edit(timeout=time_to_timeout, reason=reason)
        await ctx.send(self._bot_success_respond)

    @commands.command(aliases=["unmute"])
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.has_guild_permissions(moderate_members=True)
    async def remove_timeout(
        self: Self,
        ctx: Context,
        member: commands.MemberConverter,
        flags: BaseModerationFlag,
    ):
        reason = self._format_reason(flags.reason)
        await member.edit(timeout=None, reason=reason)
        await ctx.send(self._bot_success_respond)

    @commands.command()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(
        self: Self,
        ctx: Context,
        member: commands.UserConverter,
        flags: BaseModerationFlag,
    ):
        reason = self._format_reason(flags.reason)
        await ctx.guild.unban(member, reason=reason)
        await ctx.send(self._bot_success_respond)


def setup(bot: Bourbon) -> None:
    bot.add_cog(Moderation(bot))
