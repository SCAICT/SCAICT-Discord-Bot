import discord
import json
import os
import asyncio

bot = discord.Bot(intents = discord.Intents.all())
with open("token.json","r") as file:
    token = json.load(file)

for i in os.listdir("./cog"):
    if i.endswith(".py"):
        bot.load_extension(f"cog.{i[:-3]}")

# 頻道總人數(每10分鐘刷新一次 因為API限制)
async def update_channel():
    await bot.wait_until_ready() 

    guild = bot.get_guild(863649110473048105)  #YOUR_GUILD_ID

    if guild is None:
        print("找不到指定的服务器")
        return

    channel = guild.get_channel(1208106247115505674)  #YOUR_CHANNEL_ID

    if channel is None:
        print("找不到指定的频道")
        return

    while not bot.is_closed():
        total_members = guild.member_count

        await channel.edit(name=f"社群總人數: {total_members} 位")
        await asyncio.sleep(600)


@bot.event
async def on_ready():
    print(f">>{bot.user} is online<<")
    bot.add_view(token_verify_button())
    bot.loop.create_task(update_channel())  



# modal
# 你問我為甚麼寫在main不是Cog 因為操Cog吃不到modal我不知道為甚麼我好爛嗚嗚嗚嗚嗚 所以我放棄直接丟回來者邊沒關係的吧

class token_modal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.input_field = discord.ui.InputText(label="課程代碼輸入")
        self.add_item(self.input_field)

    async def callback(self, interaction: discord.Interaction):
        user_token = self.input_field.value

        # 二月主題課程token: ZGlzY29yZCBib3QgcHljMHJkCg==
        # 度其實就是 discord bot pyc0rd base64 而已ㄏㄏ
        # 我只是想順便show modal 和測試而已
        # 創建嵌入並發送至 Discord 伺服器
        if user_token == "ZGlzY29yZCBib3QgcHljMHJkCg==":
            role = discord.utils.get(interaction.guild.roles, name="二月主題課程")
            await interaction.user.add_roles(role)

            embed=discord.Embed(color=0x3dbd46)
            embed.set_thumbnail(url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/47298/check-mark-button-emoji-clipart-md.png")
            embed.add_field(name="已領取二月主題課程身分組", value=" 課程主題: Discord Bot", inline=False)
            embed.add_field(name=f"用戶: {interaction.user.name}", value=" 講師: OsGa", inline=False)
            embed.set_footer(text=" ")
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            embed=discord.Embed(color=0xbd3d3d)
            embed.set_thumbnail(url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/47329/cross-mark-button-emoji-clipart-md.png")
            embed.add_field(name="領取失敗", value="", inline=False)
            embed.add_field(name=f"用戶: {interaction.user.name}", value="請重新確認課程代碼", inline=False)
            embed.set_footer(text=" ")
            await interaction.response.send_message(embed=embed,ephemeral=True)

class token_verify_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="輸入課程代碼",style=discord.ButtonStyle.blurple,emoji="🏷️",custom_id="button")
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(token_modal(title="請輸入token"))

@bot.slash_command()
async def send_modal(ctx):
    if ctx.author.guild_permissions.administrator:
        embed=discord.Embed(color=0x4be1ec)
        embed.set_thumbnail(url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/56531/label-emoji-clipart-md.png")
        embed.add_field(name="點下方按鈕輸入token", value="", inline=False)
        embed.add_field(name="領取課程身分組!", value="", inline=False)
        await ctx.respond(embed=embed,view=token_verify_button())

bot.run(token["token"])