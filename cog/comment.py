import discord
from discord.ext import commands
import json
from datetime import datetime
from datetime import date
from datetime import timedelta
import os
from cog.core.SQL import read
from cog.core.SQL import write
from cog.core.SQL import isExist
from cog.core.SQL import end    #用來結束和SQL資料庫的會話
from cog.core.SQL import linkSQL
import random
def insertUser(userId,TABLE,CURSOR):#初始化(創建)傳入該ID的表格
    CURSOR.execute(f"INSERT INTO {TABLE} (uid) VALUE({userId})")#其他屬性在創造時MYSQL會給預設值
def getChannels():#要特殊用途頻道的列表，這裡會用來判斷是否在簽到頻簽到，否則不予授理
    #os.chdir("./")
    with open(f"{os.getcwd()}/DataBase/server.config.json", "r") as file:
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

    today_comments+=1
    
    if today_comments==next_reward:
        point+=2
        next_reward+=times**2
        times+=1
        write(userId,"point",point,CURSOR)
        write(userId,"next_reward",next_reward,CURSOR,TABLE="CommentPoints")
        write(userId,"times",times,CURSOR,TABLE="CommentPoints")

        #紀錄log
        print(f"{userId},{nickName} Get 2 point by comment {datetime.now()}")
    write(userId,"today_comments",today_comments,CURSOR)
#每月更新的數數

class comment(commands.Cog):

    def __init__(self, bot):
        self.bot=bot
        self.spChannel=getChannels()#特殊用途的channel
        
    #數數判定
    @commands.Cog.listener()
    async def on_message(self, message):
        userId=message.author.id
        CONNECTION,CURSOR=linkSQL()#SQL 會話
        
        if message.content.startswith("!set"):
            #狀態指令
            arg=message.content.split(" ")
            await self.bot.change_presence(activity=discord.Streaming(name="YouTube", url=f"{arg[2]}"))#,details=f"{arg[1]}"
        if userId != self.bot.user.id:
            #機器人會想給自己記錄電電點，必須排除
            if message.channel.id == self.spChannel["countChannel"]:
            #數數回應
                await comment.count(message)
            elif message.channel.id == self.spChannel["colorChannel"]:
            #猜色碼回應
                await comment.niceColor(message)
            return
        if message.channel.id not in self.spChannel["exclude_point"]:
            #列表中頻道不算發言次數
            comment.todayComment(userId,message,CURSOR)
        end(CONNECTION,CURSOR)
        
    @staticmethod
    def todayComment(userId,message,CURSOR):
        #創建該user的資料表
        if not(isExist(userId,"USER",CURSOR)):#該 uesr id 不在USER表格內，插入該筆用戶資料
            insertUser(userId,"USER",CURSOR)
        if not(isExist(userId,"CommentPoints",CURSOR)):
            insertUser(userId,"CommentPoints",CURSOR)
        now = date.today()
        delta = timedelta(days=1)
        last_comment  = read(userId, 'last_comment',CURSOR)#SQL回傳型態:<class 'datetime.date'>
        #今天第一次發言，重置發言次數
        if(now-last_comment >= delta):
            reset(message, now,CURSOR)
        #更改今天發言狀態
        reward(message,CURSOR)
        
    @staticmethod
    async def count(message):
        CONNECT,CURSOR=linkSQL()
        try:
            bin_string = message.content
            #若bin_string轉換失敗，會直接跳到except
            decimal_number = int(bin_string, 2)
            CONNECT,CURSOR=linkSQL()
            CURSOR.execute("select seq from game")
            nowSeq=CURSOR.fetchone()[0]
            CURSOR.execute("select lastID from game")
            latestUser=CURSOR.fetchone()[0]
            if  message.author.id == latestUser:
                #同人疊數數
                await message.add_reaction("🔄")
            elif decimal_number == nowSeq+1:
                #數數成立
                CURSOR.execute("UPDATE game SET seq = seq+1")
                print(message.author.id)
                CURSOR.execute(f"UPDATE game SET lastID = {message.author.id}")
                # add a check emoji to the message
                await message.add_reaction("✅")
            else:
                #不同人數數，但數字不對
                await message.add_reaction("❌")
        except:
            #在decimal_number賦值因為不是數字(可能聊天或其他文字)產生錯誤產生問號emoji回應
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
    bot.add_cog(comment(bot))
