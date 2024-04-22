import discord
from build.build import build
from discord.ext import commands

class admin_role(build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.roleView())

    # 成員身分組
    class roleView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None

        @discord.ui.button(label="領取身分組", style=discord.ButtonStyle.blurple, emoji="🥇"  ,custom_id="take_the_role")
        async def button_callback_1(self, button, interaction):
            role = discord.utils.get(interaction.guild.roles, name="ADMIN")
            await interaction.user.add_roles(role)
            await interaction.response.send_message("已領取身分組 `ヾ(≧▽≦*)o`", ephemeral=True)

    @discord.slash_command()
    async def create_role_button(self, ctx):
        if ctx.author.guild_permissions.administrator:
            embed = discord.Embed(color=0x16b0fe)
            embed.set_thumbnail(
                url="https://emojiisland.com/cdn/shop/products/Nerd_with_Glasses_Emoji_2a8485bc-f136-4156-9af6-297d8522d8d1_large.png?v=1571606036")
            embed.add_field(name="哈囉 點一下", value="  ", inline=False)
            await ctx.respond(embed=embed, view=self.roleView())
            
            
    class Gift(discord.ui.View):
        click : bool = None
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None
        @discord.ui.button(label="領取獎勵", style=discord.ButtonStyle.success)
        async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
            
            await interaction.response.send_message("獎勵已發送", ephemeral=True)
      
    @discord.slash_command(name="發送禮物",description="dm_gift")
    async def senddm(self, ctx,target,point):#dm gift
        manager=ctx.author
        target = await self.bot.fetch_user(target)#898141506588770334
        view = self.Gift()
        await target.send(view=view)
        await ctx.respond(f"{manager} 發送 {point} 電電點給 {target}")

def setup(bot):
    bot.add_cog(admin_role(bot))
