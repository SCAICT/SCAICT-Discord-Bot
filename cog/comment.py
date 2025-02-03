# Standard imports
from datetime import datetime
from datetime import date
from datetime import timedelta
import json
import os
import random
import re

# Third-party imports
import discord
from discord.ext import commands

# Local imports
from cog.core.sql import read
from cog.core.sql import write
from cog.core.sql import user_id_exists
from cog.core.sql import end  # 用於結束和SQL資料庫的會話
from cog.core.sql import link_sql

try:
    with open(
        f"{os.getcwd()}/DataBase/server.config.json", "r", encoding="utf-8"
    ) as file:
        stickers = json.load(file)["SCAICT-alpha"]["stickers"]
except FileNotFoundError:
    print("Configuration file not found.")
    stickers = {}
except json.JSONDecodeError:
    print("Error decoding JSON.")
    stickers = {}


def insert_user(user_id, table, cursor):
    """
    初始化（新增）傳入該ID的資料表
    """
    try:
        cursor.execute(
            f"INSERT INTO {table} (uid) VALUE({user_id})"
        )  # 其他屬性在新增時MySQL會給預設值
    # pylint: disable-next = broad-exception-caught
    except Exception as exception:
        print(f"Error inserting user {user_id} into {table}: {exception}")


def get_channels():  # 要特殊用途頻道的列表，這裡會用來判斷是否在簽到頻道簽到，否則不予受理
    # os.chdir("./")
    try:
        with open(
            f"{os.getcwd()}/DataBase/server.config.json", "r", encoding="utf-8"
        ) as config_file:
            return json.load(config_file)["SCAICT-alpha"]["channel"]
    except FileNotFoundError:
        print("Configuration file not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except KeyError as exception:
        print(f"Key error in configuration file: {exception}")

    return {}


def reset(message, now, cursor):
    user_id = message.author.id
    try:
        write(user_id, "today_comments", 0, cursor)  # 歸零發言次數
        write(user_id, "last_comment", str(now), cursor)
        write(
            user_id, "times", 2, cursor, table="comment_points"
        )  # 初始化達標後能獲得的電電點
        write(user_id, "next_reward", 1, cursor, table="comment_points")
    # pylint: disable-next = broad-exception-caught
    except Exception as exception:
        print(f"Error resetting user {user_id}: {exception}")


def reward(message, cursor):
    user_id = message.author.id
    user_display_name = message.author
    try:
        # 讀user資料表的東西
        today_comments = read(user_id, "today_comments", cursor)
        point = read(user_id, "point", cursor)
        # 讀comment_points 資料表裡面的東西，這個表格記錄有關發言次數非線性加分的資料
        next_reward = read(user_id, "next_reward", cursor, table="comment_points")
        times = read(user_id, "times", cursor, table="comment_points")

        today_comments += 1

        if today_comments == next_reward:
            point += 2
            next_reward += times**2
            times += 1
            write(user_id, "point", point, cursor)
            write(user_id, "next_reward", next_reward, cursor, table="comment_points")
            write(user_id, "times", times, cursor, table="comment_points")

            # 紀錄log
            print(
                f"{user_id}, {user_display_name} Get 2 point by comment {datetime.now()}"
            )
        write(user_id, "today_comments", today_comments, cursor)
    # pylint: disable-next = broad-exception-caught
    except Exception as exception:
        print(f"Error rewarding user {user_id}: {exception}")


class Comment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sp_channel = get_channels()  # 特殊用途的channel

        self.sp_channel_handler = {
            self.sp_channel["countChannel"]: self.count,
            self.sp_channel["colorChannel"]: self.nice_color,
        }

    # 數數判定
    @commands.Cog.listener()
    async def on_message(self, message):
        user_id = message.author.id
        try:
            if user_id != self.bot.user.id:  # 機器人發言不可當成觸發條件，必須排除
                handler = self.sp_channel_handler.get(message.channel.id)
                # 根據訊息頻道 ID 切換要呼叫的函數
                if handler:
                    await handler(message)
                if message.channel.id not in self.sp_channel["exclude_point"]:
                    # 平方發言加電電點，列表中頻道不算發言次數
                    connection, cursor = link_sql()  # SQL 會話
                    self.today_comment(user_id, message, cursor)
                    end(connection, cursor)
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error in comment for user {user_id}: {exception}")

    @staticmethod
    def today_comment(user_id, message, cursor):
        try:
            # 新增該user的資料表
            if not user_id_exists(user_id, "user", cursor):
                # 該 user id 不在user資料表內，插入該筆使用者資料
                insert_user(user_id, "user", cursor)
            if not user_id_exists(user_id, "comment_points", cursor):
                insert_user(user_id, "comment_points", cursor)
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error: {exception}")

        now = date.today()
        delta = timedelta(days=1)
        # SQL回傳型態：<class 'datetime.date'>
        last_comment = read(user_id, "last_comment", cursor)
        # 今天第一次發言，重設發言次數
        if now - last_comment >= delta:
            reset(message, now, cursor)
        # 變更今天發言狀態
        reward(message, cursor)

    @staticmethod
    async def count(message):
        try:

            connection, cursor = link_sql()

            raw_content = message.content
            # 每月更新的數數
            # emoji 數數(把emoji轉換成binary)
            elements = raw_content.split()
            unique_elements = set(elements)
            if len(unique_elements) > 2:
                await message.add_reaction("❔")
                return

            # 轉換元素為0和1
            element_map = {element: idx for idx, element in enumerate(unique_elements)}
            transformed_elements = [str(element_map[element]) for element in elements]

            # 將轉換後的元素拼接成字串
            raw_content = "".join(transformed_elements)

            # emoji 數數(把emoji轉換成binary)
            counting_base = 2

            # Allow both plain and monospace formatting
            based_number = re.sub("^`([^\n]+)`$", "\\1", raw_content)

            # If is valid 4-digit whitespace delimiter format
            # (with/without base), then strip whitespace characters.
            #
            # Test cases:
            # - "0"
            # - "0000"
            # - "000000"
            # - "00 0000"
            # - "0b0"
            # - "0b0000"
            # - "0b 0000"
            # - "0b0 0000"
            # - "0b 0 0000"
            # - "0 b 0000"
            # - "0 b 0 0000"
            if re.match(
                "^(0[bdox]|0[bdox] |0 [bdox] |)"
                + "([0-9A-Fa-f]{1,4})"
                + "(([0-9A-Fa-f]{4})*|( [0-9A-Fa-f]{4})*)$",
                based_number,
            ):
                based_number = based_number.replace(" ", "")
            # If is valid 3-digit comma delimiter format
            # (10-based, without base)
            elif counting_base == 10 and re.match(
                "^([0-9]{1,3}(,[0-9]{3})*)$", based_number
            ):
                based_number = based_number.replace(",", "")
            # 若based_number字串轉換至整數失敗，會直接跳到except
            decimal_number = int(based_number, counting_base)
            # 補數
            decimal_complement = ~decimal_number & ((1 << len(based_number)) - 1)
            cursor.execute("select seq from game")
            now_seq = cursor.fetchone()[0]
            cursor.execute("select lastid from game")
            latest_user = cursor.fetchone()[0]
            if message.author.id == latest_user:
                # 同人疊數數
                await message.add_reaction("🔄")
            elif decimal_number == now_seq + 1 or decimal_complement == now_seq + 1:
                # 數數成立
                cursor.execute("UPDATE game SET seq = seq+1")
                cursor.execute("UPDATE game SET lastid = %s", (message.author.id,))
                # add a check emoji to the message
                await message.add_reaction("✅")
                # 隨機產生 1~100 的數字。若模 11=10 ，九個數字符合，分布於 1~100 ，發生機率 9%。給予 5 點電電點
                rand = random.randint(1, 100)
                if rand % 11 == 10:
                    point = read(message.author.id, "point", cursor) + 5
                    write(message.author.id, "point", point, cursor)
                    # pylint: disable-next = line-too-long
                    print(
                        f"{message.author.id}, {message.author} Get 5 point by count reward {datetime.now()}"
                    )
                    await message.add_reaction("💸")
            else:
                # 不同人數數，但數字不對
                await message.add_reaction("❌")
                await message.add_reaction("❓")
        except (TypeError, ValueError):
            # 在decimal_number賦值因為不是數字（可能聊天或其他文字）產生錯誤產生問號emoji回應
            await message.add_reaction("❔")
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error: {exception}")

        end(connection, cursor)

    @staticmethod
    async def nice_color(message):
        # if message.content is three letter
        if len(message.content) != 3:
            # reply text
            await message.channel.send("請輸入三位 HEX 碼顏色")
            return

        try:
            connection, cursor = link_sql()
            cursor.execute("SELECT nicecolor FROM game")
            nice_color = cursor.fetchone()[0]
            # Convert to upper case before check
            hex_color = message.content.upper()

            cursor.execute("SELECT `nicecolorround` FROM game")
            guess_round = cursor.fetchone()[0] + 1
            if hex_color == nice_color:
                # Use embed to send message. Set embed color to hex_color
                nice_color = "".join([c * 2 for c in nice_color])  # 格式化成六位數
                embed = discord.Embed(
                    title=f"猜了 {guess_round}次後答對了！",
                    description=f"#{hex_color}\n恭喜 {message.author.mention} 獲得 2{stickers['zap']}",
                    color=discord.Colour(int(nice_color, 16)),
                )
                await message.channel.send(embed=embed)
                # Generate a new color by random three letter 0~F
                new_color = "".join(
                    [random.choice("0123456789ABCDEF") for _ in range(3)]
                )
                # 資料庫存 3 位色碼，重設回答次數
                cursor.execute(
                    f"UPDATE game SET nicecolor = '{new_color}', nicecolorround = 0"
                )
                # 格式化成六位數，配合 discord.Colour 輸出
                new_color = "".join([c * 2 for c in new_color])
                # Send new color to channel
                embed = discord.Embed(
                    title="已產生新題目",
                    description="請輸入三位數回答",
                    color=discord.Colour(int(new_color, 16)),
                )
                await message.channel.send(embed=embed)
                # 猜對的使用者加分
                point = read(message.author.id, "point", cursor) + 2
                write(message.author.id, "point", point, cursor)
                # Log
                # pylint: disable-next = line-too-long
                print(
                    f"{message.author.id},{message.author} Get 2 point by nice color reward {datetime.now()}"
                )
            else:
                cursor.execute("UPDATE game SET nicecolorround = nicecolorround + 1;")
                # https://pylint.readthedocs.io/en/latest/user_guide/messages/refactor/consider-using-generator.html
                # pylint: disable-next = line-too-long
                correct = 100 - (
                    sum(
                        (int(hex_color[i], 16) - int(nice_color[i], 16)) ** 2
                        for i in range(3)
                    )
                    ** 0.5
                    / 0.2598076211353316
                )
                hex_color = "".join([c * 2 for c in hex_color])  # 格式化成六位數
                embed = discord.Embed(
                    title=f"#{hex_color}\n{correct:.2f}%",
                    color=discord.Colour(int(hex_color, 16)),
                )
                await message.channel.send(embed=embed)
                nice_color = "".join([c * 2 for c in nice_color])  # 格式化成六位數
                embed = discord.Embed(
                    description=f"答案：左邊顏色\n總共回答次數：{guess_round}",
                    color=discord.Colour(int(nice_color, 16)),
                )
                await message.channel.send(embed=embed)
            # except:
            # await message.add_reaction("❔")
            # print error message
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error: {exception}")

        end(connection, cursor)


def setup(bot):
    bot.add_cog(Comment(bot))
