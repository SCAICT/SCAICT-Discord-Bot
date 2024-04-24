# Standard imports
from datetime import datetime
from datetime import date
from datetime import timedelta
import json
import os
# Third-party imports
import discord
from discord.ext import commands
# Local imports
from cog.core.sql import read
from cog.core.sql import write
from cog.core.sql import user_id_exists
from cog.core.sql import end # 用來結束和SQL資料庫的會話
from cog.core.sql import link_sql

import random
def insert_user(user_id, table, cursor): # 初始化（新增）傳入該ID的資料表
    cursor.execute(f"INSERT INTO {table} (uid) VALUE({user_id})") # 其他屬性在新增時MySQL會給預設值

def get_channels(): # 要特殊用途頻道的列表，這裡會用來判斷是否在簽到頻道簽到，否則不予受理
    # os.chdir("./")
    with open(f"{os.getcwd()}/DataBase/server.config.json", "r", encoding = "utf-8") as file:
        return json.load(file)["SCAICT-alpha"]["channel"]
with open(f"{os.getcwd()}/DataBase/server.config.json", "r") as file:
    stickers=json.load(file)["SCAICT-alpha"]["stickers"]
def reset(message, now,CURSOR):
    userId=message.author.id
    write(userId,"today_comments",0,CURSOR)#歸零發言次數
    write(userId,"last_comment",str(now),CURSOR)
    write(userId,"times",2,CURSOR,TABLE="CommentPoints")#初始化達標後能獲得的電電點
    write(userId,"next_reward",1,CURSOR,TABLE="CommentPoints")
def reward(message,CURSOR):
    #讀USER資料表的東西
    userId=message.author.id
    nickName=message.author
    today_comments=read(userId,"today_comments",CURSOR)
    point=read(userId,"point",CURSOR)
    #讀CommentPoints 資料表裡面的東西，這個表格紀錄有關發言次數非線性加分的資料
    next_reward=read(userId,"next_reward",CURSOR,TABLE="CommentPoints")
    times=read(userId,"times",CURSOR,TABLE="CommentPoints")

    today_comments += 1

    if today_comments == next_reward:
        point += 2
        next_reward += times ** 2
        times += 1
        write(user_id, "point", point, cursor)
        write(user_id, "next_reward", next_reward, cursor, table = "CommentPoints")
        write(user_id, "times", times, cursor, table = "CommentPoints")

        # 紀錄log
        print(f"{user_id},{nickname} Get 2 point by comment {datetime.now()}")
    write(user_id, "today_comments", today_comments, cursor)
# 每月更新的數數

class Comment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sp_channel = get_channels() # 特殊用途的channel

    # 數數判定
    @commands.Cog.listener()
    async def on_message(self, message):
        user_id = message.author.id
        connection, cursor = link_sql() # SQL 會話

        if message.content.startswith("!set"):
            # 狀態指令
            arg = message.content.split(" ")
            await self.bot.change_presence(activity = discord.Streaming(
                name = "YouTube",
                url = f"{arg[2]}"
                # , details = f"{arg[1]}"
            ))
        if user_id != self.bot.user.id:
            # 機器人會想給自己記錄電電點，必須排除
            if message.channel.id == self.sp_channel["countChannel"]:
            # 數數回應
                await Comment.count(message)
            elif message.channel.id == self.spChannel["colorChannel"]:
            #猜色碼回應
                await comment.niceColor(message)
            return
        if message.channel.id not in self.sp_channel["exclude_point"]:
            # 列表中頻道不算發言次數
            Comment.today_comment(user_id, message, cursor)
        end(connection, cursor)

    @staticmethod
    def today_comment(user_id, message, cursor):
        # 新增該user的資料表
        if not user_id_exists(user_id, "USER", cursor): # 該 uesr id 不在USER資料表內，插入該筆使用者資料
            insert_user(user_id, "USER", cursor)
        if not user_id_exists(user_id, "CommentPoints", cursor):
            insert_user(user_id, "CommentPoints", cursor)
        now = date.today()
        delta = timedelta(days = 1)
        last_comment = read(user_id, "last_comment", cursor) # SQL回傳型態：<class 'datetime.date'>
        # 今天第一次發言，重設發言次數
        if now - last_comment >= delta:
            reset(message, now, cursor)
        # 變更今天發言狀態
        reward(message, cursor)

    @staticmethod
    async def count(message):
        connect, cursor = link_sql()
        try:
            bin_string = message.content
            #若bin_string轉換失敗，會直接跳到except
            decimal_number = int(bin_string, 2)
            connect, cursor = link_sql()
            cursor.execute("select seq from game")
            now_seq = cursor.fetchone()[0]
            cursor.execute("select lastID from game")
            latest_user = cursor.fetchone()[0]
            if message.author.id == latest_user:
                # 同人疊數數
                await message.add_reaction("🔄")
            elif decimal_number == now_seq + 1:
                # 數數成立
                cursor.execute("UPDATE game SET seq = seq+1")
                print(message.author.id)
                cursor.execute(f"UPDATE game SET lastID = {message.author.id}")
                # add a check emoji to the message
                await message.add_reaction("✅")
            else:
                # 不同人數數，但數字不對
                await message.add_reaction("❌")
                await message.add_reaction("❓")
        except (TypeError, ValueError):
            # 在decimal_number賦值因為不是數字（可能聊天或其他文字）產生錯誤產生問號emoji回應
            await message.add_reaction("❔")
        end(CONNECT,CURSOR)
    
    @staticmethod
    async def niceColor(message):
        CONNECT,CURSOR=linkSQL()
        # try:
                # if message.content is three letter
        if len(message.content) != 3:
            # reply text
            await message.channel.send("請輸入三位 HEX 碼顏色")
            return
        # to upper case before check
        CONNECT,CURSOR=linkSQL()
        CURSOR.execute("select niceColor from game")
        niceColor=CURSOR.fetchone()[0]
        niceColor = ''.join([c*2 for c in niceColor])#格式化成六位數
        hexColor = message.content.upper()
        hexColor = ''.join([c*2 for c in hexColor])#格式化成六位數
        
        CURSOR.execute("select `niceColorRound` from game")
        round=CURSOR.fetchone()[0]
        if(hexColor == niceColor):
            # use embled to send message. Set embled color to hexColor
            embed = discord.Embed(title=f"猜了 {round}次後答對了!", description=f"#{hexColor}\n恭喜 {message.author.mention} 獲得 2{stickers['logo']}", color=discord.Colour(int(niceColor,16)))
            await message.channel.send(embed=embed)
            # set count to 0
            CURSOR.execute("UPDATE game SET niceColorRound = 0")
            # generate a new color by random three letter 0~F
            #資料庫內一定要先設定一個初值題目，沒有題目永遠不會答對產生新題目
            newColor = ''.join([random.choice('0123456789ABCDEF') for _ in range(3)])
            CURSOR.execute(f"UPDATE game SET niceColor = '{newColor}'")
            # send new color to channel
            embed = discord.Embed(title=f"新題目已生成", description=f"請輸入三位數回答", color=discord.Colour(int(newColor,16)))
            await message.channel.send(embed=embed)
            #猜對的用戶加分
            point=read(message.author.id,"point",CURSOR)+2
            write(message.author.id,"point",point,CURSOR)
        else:
            CURSOR.execute("UPDATE game SET niceColorRound = niceColorRound+1;")
            # 計算顏色有多相近。計算三個數字分別與答案相差多少的平均值除以16*100%
            diff = sum([abs(int(hexColor[i], 16) - int(niceColor[i], 16)) for i in range(3)]) / 48 * 100
            # reply with embled. background color is hexColor
            embed = discord.Embed(title=f"#{hexColor}\n{diff:.2f}%", color=discord.Colour(int(hexColor, 16)))
            await message.channel.send(embed=embed)
            embed = discord.Embed(description=f"答案:左邊顏色\n總共回答次數:{round}", color=discord.Colour(int(niceColor,16)))
            await message.channel.send(embed=embed)
        # except:
        #     await message.add_reaction("❔")
            # print error message
            
        end(CONNECT,CURSOR)
        

def setup(bot):
    bot.add_cog(Comment(bot))
