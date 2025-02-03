# Standard imports
from datetime import datetime
import traceback

# Third-party imports
import discord
from discord.ext import commands

# Local imports
from build.build import Build
from cog.core.sql import link_sql, read, write, end
from cog.core.sendgift import send_gift_button


class SendGift(Build):
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bot.add_view(self.Gift())

    # 禮物按鈕
    class Gift(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # Timeout of the view must be set to None
            self.type = None  # 存放這個按鈕是送電電點還是抽獎券，預設 None ，在建立按鈕時會設定 see view.type = gift_type
            self.count = 0  # 存放這個按鈕是送多少電電點/抽獎券

        # 發送獎勵
        @staticmethod
        def __reward(uid: int, username: str, bonus_type: str, bonus: int) -> None:
            connection, cursor = link_sql()
            current_point = read(uid, bonus_type, cursor)
            write(uid, bonus_type, current_point + bonus, cursor)
            end(connection, cursor)
            print(f"{uid} {username} get {bonus} {bonus_type} by Gift {datetime.now()}")

        # 存資料庫存取按鈕屬性(包括獎勵類型、數量)
        def __get_btn_attr(self, btn_id: int):
            try:
                connection, cursor = link_sql()
                cursor.execute(
                    f"SELECT type, count FROM `gift` WHERE `btnID`={btn_id} and `received`=0"
                )
                ret = cursor.fetchall()
                if len(ret) == 0:
                    return None, None
                cursor.execute(f"UPDATE `gift` SET `received`=1 WHERE `btnID`={btn_id}")
                end(connection, cursor)
                return ret[0][0], ret[0][1]  # type, count
            except Exception as e:
                print(e)
                return None, None

        # 點擊後會觸發的動作
        @discord.ui.button(
            label="領取獎勵", style=discord.ButtonStyle.success, custom_id="get_gift"
        )
        async def get_gift(self, button: discord.ui.Button, ctx) -> None:
            self.type, self.count = self.__get_btn_attr(
                ctx.message.id
            )  # 傳入按鈕的訊息 ID，得到按鈕的屬性
            if self.type is None or self.count is None:
                button.label = "出問題了"  # Change the button's label to "已領取"
                button.disabled = True  # 關閉按鈕，避免錯誤再被觸發
                await ctx.response.edit_message(view=self)
                button.disabled = True  # 關閉按鈕，避免重複點擊
                print(
                    f"{ctx.user.id},{ctx.user} throw error by get_gift {datetime.now()}"
                )
                return await ctx.respond(
                    "好像出了點問題，你可能已經領過或伺服器內部錯誤。若有異議請在收到此訊息兩天內截圖此畫面提交客服單回報",
                    ephemeral=False,
                )
            self.type = "point" if self.type == "電電點" else "ticket"
            self.__reward(ctx.user.id, ctx.user, self.type, self.count)
            # log
            button.label = "已領取"  # Change the button's label to "已領取"
            button.disabled = True  # 關閉按鈕，避免重複點擊
            await ctx.response.edit_message(view=self)

    def cache_users_by_name(self):
        # 將所有使用者名稱和對應的使用者物件存入字典
        return {user.name: user for user in self.bot.users}

    @discord.slash_command(name="發送禮物", description="dm_gift")
    async def send_dm_gift(
        self,
        ctx,
        target_str: discord.Option(
            str, "發送對象（用半形逗號分隔多個使用者名稱）", required=True
        ),
        gift_type: discord.Option(str, "送禮內容", choices=["電電點", "抽獎券"]),
        count: discord.Option(int, "數量"),
    ) -> None:
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("你沒有權限使用這個指令！", ephemeral=True)
            return
        SendGift.user_cache = self.cache_users_by_name()
        try:
            await ctx.defer()  # 確保機器人請求不會超時
            # 不能發送負數
            if count <= 0:
                await ctx.respond("不能發送 0 以下個禮物！", ephemeral=True)
                return
            manager = ctx.author  # return <class 'discord.member.Member'>
            target_usernames = target_str.split(",")
            target_users = []

            async def fetch_user_by_name(name):
                user_obj = discord.utils.find(lambda u: u.name == name, self.bot.users)
                if user_obj:
                    try:
                        return await self.bot.fetch_user(user_obj.id)
                    except Exception as e:
                        print(f"Failed to fetch user with ID {user_obj.id}: {str(e)}")
                        return None

            for username in target_usernames:
                username = username.strip()
                if username not in SendGift.user_cache:
                    continue
                try:
                    user = await fetch_user_by_name(username)
                    target_users.append(user)
                except (ValueError, Exception) as e:
                    await ctx.respond(f"找不到使用者 ： {username}{e}", ephemeral=True)
                    return
            # DM 一個 Embed 和領取按鈕
            for target_user in target_users:
                await send_gift_button(
                    self, target_user, gift_type, count, manager.name
                )
            # 管理者介面提示
            await ctx.respond(
                f"{manager} 已發送 {count} {gift_type} 給 {', '.join([user.name for user in target_users])}"
            )
        except Exception as e:
            traceback.print_exc()
            await ctx.respond(f"伺服器內部出現錯誤：{e}", ephemeral=True)


def setup(bot):
    bot.add_cog(SendGift(bot))
