from nextcord.ext.commands import FlagConverter


class BaseFlag(FlagConverter, delimiter=" ", prefix="--"):
    pass
