# Third-party imports
import discord

from cog.core.sql import link_sql, end


class MessageSendError(Exception):  # 自定義的例外類型
    pass


class DBError(Exception):  # 自定義的例外類型
    pass


async def send_gift_button(
    self, target_user: discord.User, gift_type: str, count: int, sender: int
) -> None:
    # 產生按鈕物件
    view = self.Gift()
    view.type = gift_type
    view.count = count
    embed = discord.Embed(
        title=f"你收到了 {count} {gift_type}！",
        description=":gift:",
        color=discord.Color.blurple(),
    )

    async def record_db(
        btn_id: int, gift_type: str, count: int, recipient: str
    ) -> None:
        try:
            connection, cursor = link_sql()
            cursor.execute(
                "INSERT INTO `gift`(`btnID`, `type`, `count`, `recipient`,`sender`) VALUES (%s, %s, %s, %s,%s)",
                (btn_id, gift_type, count, recipient, sender),
            )
            end(connection, cursor)
        except Exception as e:
            end(connection, cursor)
            raise DBError("無法成功插入禮物資料進資料庫") from e

    try:
        await target_user.send(embed=embed)
        msg = await target_user.send(view=view)
        await record_db(msg.id, gift_type, count, target_user.name)
    except discord.Forbidden as exc:
        raise MessageSendError(
            f"無法向使用者 {target_user.name} 傳送訊息，可能是因為他們關閉了 DM"
        ) from exc
