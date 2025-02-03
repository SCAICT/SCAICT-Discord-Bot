# Standard imports
# import csv
# from datetime import datetime, timedelta
# import json
# import os

# Third-party imports
import discord
from build.build import Build

# Local imports


class ManagerCommand(Build):
    @discord.slash_command(name="reload", description="你是管理員才讓你用")
    async def reload(self, ctx, package):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("你沒有權限使用這個指令！", ephemeral=True)
            return
        self.bot.reload_extension(f"cog.{package}")
        await ctx.respond(f"🔄 {package} reloaded")


def setup(bot):
    bot.add_cog(ManagerCommand(bot))
