# Standard imports
import json
import os
import random
from urllib.parse import urlencode
import traceback

# Third-party imports
from flask import (
    Flask,
    redirect,
    request,
    session,
    url_for,
    render_template,
    send_from_directory,
    jsonify,
)
import requests
from dotenv import load_dotenv

# Local imports
from cog.core.sql import write
from cog.core.sql import read
from cog.core.sql import link_sql
from cog.core.sql import end
from cog.core.sql import user_id_exists
from cog.api.api import Apis
from cog.api.gift import Gift

app = Flask(__name__)
load_dotenv(f"{os.getcwd()}/.env", verbose=True, override=True)

app.secret_key = os.getenv("SECRET_KEY")
discord_client_id = os.getenv("DISCORD_CLIENT_ID")
discord_client_secret = os.getenv("DISCORD_CLIENT_SECRET")
discord_redirect_uri = os.getenv("DISCORD_REDIRECT_URI")
github_client_id = os.getenv("GITHUB_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
github_redirect_uri = os.getenv("GITHUB_REDIRECT_URI")
github_discord_redirect_uri = os.getenv("GITHUB_DISCORD_REDIRECT_URI")
discord_token = os.getenv("DISCORD_TOKEN")
send_gift_role = os.getenv("SEND_GIFT_ROLE")
guild_ID = os.getenv("GUILD_ID")
# 將字串轉換為列表
if send_gift_role:
    send_gift_role = [str(role_id) for role_id in send_gift_role.split(",")]
else:
    send_gift_role_list = []


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.route("/login")
def login():
    redirurl = request.args.get("redirurl")
    base_url = "https://discord.com/api/oauth2/authorize"
    params = {
        "client_id": discord_client_id,
        "redirect_uri": discord_redirect_uri,
        "response_type": "code",
        "scope": "identify email",
    }
    if redirurl:
        params["state"] = redirurl
    # 將參數進行 URL 編碼並組合成最終的 URL
    urlencoded = urlencode(params)
    return redirect(f"{base_url}?{urlencoded}")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("profile"))


@app.route("/api/mlist")
def listt():
    if not session:
        return jsonify({"result": "you must login", "status": 403})
    api_admin = session.get(
        "user"
    )  # <class 'werkzeug.local.LocalProxy'> {'avatar': 'https://cdn.discordapp.com/avatars/898141506588770334/a_c81acdd4a925993d053a6fe9ed990c14.png', 'id': '898141506588770334', 'name': 'iach526526'}
    api_admin_id = api_admin.get("id")
    headers = {"Authorization": f"Bot {discord_token}"}
    url = f"https://discord.com/api/v10/guilds/{guild_ID}/members/{api_admin_id}"
    response = requests.get(url, headers=headers, timeout=10)
    user_data = response.json()
    if response.status_code != 200:
        return (
            jsonify({"error": "Failed to fetch user information"}),
            response.status_code,
        )
    if send_gift_role not in user_data.get("roles", []):
        return jsonify(
            {"result": "You do not have permission to use this", "status": 403}
        )
    url = "https://discord.com/api/v10/guilds/959823904266944562/members"
    headers = {"Authorization": f"Bot {discord_token}"}
    params = {"limit": 1000}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    return response.json()


@app.route("/api/send/<int:target_user_id>")
# api/send/{recipient}?gift_type={電電點|抽獎券}count={count}
def send(target_user_id):
    if not session:
        return jsonify({"result": "you must login", "status": 403})
    try:
        api_admin = session.get(
            "user"
        )  # <class 'werkzeug.local.LocalProxy'> {'avatar': 'https://cdn.discordapp.com/avatars/898141506588770334/a_c81acdd4a925993d053a6fe9ed990c14.png', 'id': '898141506588770334', 'name': 'iach526526'}
        api_admin_id = api_admin.get("id")
        api_admin_name = api_admin.get("name")
        discord_api = Apis(discord_token, guild_ID)
        request_admin = discord_api.get_user(api_admin_id)
        gift_type = request.args.get("gift_type", "電電點")  # 預設為"電電點"
        gift_amount = request.args.get("count", 1)  # 預設數量為1
        if "error" in request_admin:
            # 如果有錯誤，返回錯誤訊息和詳細報錯
            return jsonify(
                {
                    "result": "Failed to fetch user information in admin id",
                    "status": 500,
                    "error_details": request_admin.get("details"),
                }
            )
        admin_roles = request_admin.get("roles", [])
        # 確保發起人有權限發送禮物
        if set(send_gift_role) & set(admin_roles) == set():
            return jsonify(
                {"result": "You do not have permission to use this", "status": 403}
            )
        if gift_type not in ["電電點", "抽獎券"]:
            return jsonify({"result": "Invalid gift type", "status": 400})
        try:
            gift_amount = int(gift_amount)  # 確保 count 是整數
        except ValueError:
            return jsonify({"result": "Invalid count value", "status": 400})
        # 確保目標用戶存在
        user_data = discord_api.get_user(target_user_id)
        if "error" in user_data:
            # 如果有錯誤，返回錯誤訊息和詳細信息
            return jsonify(
                {
                    "result": "Failed to fetch user information in target id (which is in url path)",
                    "status": 500,
                    "error_details": request_admin.get("details"),
                }
            )
        # 送禮物
        user_name = user_data["user"]["username"]
        try:
            new_gift = Gift(
                discord_token, guild_ID, target_user_id
            )  # create a new gift object
            if new_gift.dm_room is None:
                return jsonify(
                    {
                        "result": "Failed to create DM channel",
                        "status": 500,
                        "error": new_gift.error_msg,
                    }
                )
            message_id = new_gift.send_gift(gift_type, gift_amount)
            connect, cursor = link_sql()
            if not user_id_exists(target_user_id, "user", cursor):
                cursor.execute(
                    "INSERT INTO user (uid) VALUE(%s)", (target_user_id,)
                )  # 這裡要調用 api 去抓使用者名稱和 Mail
            cursor.execute(
                "INSERT into gift (btnID,type,count,recipient,received,sender) VALUE(%s,%s,%s,%s,%s,%s)",
                (
                    message_id,
                    gift_type,
                    gift_amount,
                    user_name,
                    True,
                    api_admin_name,
                ),
            )
            gift_type = "point" if gift_type == "電電點" else "ticket"
            query = f"update user set {gift_type}={gift_type}+%s where uid=%s"
            cursor.execute(query, (gift_amount, target_user_id))
            end(connect, cursor)

        except Exception as e:
            return jsonify(
                {
                    "result": "internal server error(SQL) when insert gift",
                    "status": 500,
                    "error": str(e),
                }
            )
        return jsonify({"result": "success", "status": 200})
    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {"result": "internal server error", "status": 500, "error": str(e)}
        )


@app.route("/callback")
def callback():
    code = request.args.get("code")
    redirurl = request.args.get("state")  # 使用 state 作為重定向的目標 URL
    data = {
        "client_id": discord_client_id,
        "client_secret": discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": discord_redirect_uri,
        "scope": "identify email",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # pylint: disable-next = missing-timeout
    response = requests.post(
        "https://discord.com/api/oauth2/token", data=data, headers=headers
    )
    access_token = response.json().get("access_token")
    if not access_token:
        return "Error: Access token not found", 400

    headers = {"Authorization": f"Bearer {access_token}"}
    # pylint: disable-next = missing-timeout
    user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
    user_data = user_response.json()

    # 儲存用戶資料到 session
    session["user"] = {
        "name": user_data.get("username"),
        "avatar": (
            f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
            if user_data.get("avatar")
            else None
        ),
        "id": user_data.get("id"),
    }

    # 將用戶資料寫入資料庫
    connection, cursor = link_sql()
    write(user_data["id"], "DCname", user_data["username"], cursor)
    write(
        user_data["id"], "DCmail", user_data.get("email", "No email provided"), cursor
    )
    end(connection, cursor)
    # 如果 redirurl 存在，將用戶資料作為查詢參數附加到 redirurl 並重定向
    if redirurl:  # and is_safe_url(redirurl):
        params = {
            "username": user_data["username"],
            "user_id": user_data["id"],
            "avatar": session["user"]["avatar"],
            "email": user_data.get("email", "No email provided"),
            "headers": headers,
        }
        urlencoded = urlencode(params)
        separator = "&" if "?" in redirurl else "?"
        return redirect(f"https://{redirurl}{separator}{urlencoded}")
    # 否則，重定向到 profile 頁面
    return redirect(url_for("profile"))


@app.route("/github/discord-callback")
def discord_callback():
    code = request.args.get("code")
    data = {
        "client_id": discord_client_id,
        "client_secret": discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": github_discord_redirect_uri,
        "scope": "identify",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # pylint: disable-next = missing-timeout
    response = requests.post(
        "https://discord.com/api/oauth2/token", data=data, headers=headers
    )
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    # pylint: disable-next = missing-timeout
    user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
    user_data = user_response.json()
    session["user"] = {
        "name": user_data["username"],
        "avatar": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        "id": user_data["id"],
    }
    return redirect(url_for("star_uwu"))


# make filter static in templates/static static
@app.route("/static/<path:filename>")
def staticfiles(path):
    return send_from_directory("static", path)


@app.route("/")
def profile():
    connection, cursor = link_sql()  # SQL 會話
    discord_user = session.get("user")
    if not discord_user:
        end(connection, cursor)
        return render_template("home.html")

    user_points = read(discord_user["id"], "point", cursor)
    user_tickets = read(discord_user["id"], "ticket", cursor)
    if user_id_exists(discord_user["id"], "user", cursor):  # 有找到這個使用者在表上
        end(connection, cursor)
        return render_template(
            "home.html",
            username=discord_user["name"],
            avatar=discord_user["avatar"],
            point=str(user_points),
            ticket=str(user_tickets),
        )

    end(connection, cursor)
    return render_template(
        "home.html",
        username=discord_user["name"],
        avatar=discord_user["avatar"],
        point="?",
        ticket="?",
    )


@app.route("/slot")
def slot():
    connection, cursor = link_sql()  # SQL 會話
    discord_user = session.get("user")
    if not discord_user:
        return render_template("slot.html")
    user_points = read(discord_user["id"], "point", cursor)
    user_tickets = read(discord_user["id"], "ticket", cursor)
    if user_id_exists(discord_user["id"], "user", cursor):  # 有找到這個使用者在資料表上
        end(connection, cursor)
        return render_template(
            "slot.html",
            username=discord_user["name"],
            avatar=discord_user["avatar"],
            point=str(user_points),
            ticket=str(user_tickets),
        )

    end(connection, cursor)
    return render_template(
        "slot.html",
        username=discord_user["name"],
        avatar=discord_user["avatar"],
        point="?",
        ticket="?",
    )


@app.route("/productList")
def product_list():
    # send pure JSON data
    with open(f"{os.getcwd()}/DataBase/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)
    return products


@app.route("/buyProduct", methods=["POST"])
def buy_product():
    # Receive POST request, get product id and check if logged in
    discord_user = session.get("user")
    if not discord_user:
        return "請重新登入"
    product_id = request.json.get("id")  # Convert product_id to a string
    if not product_id:
        return "無法讀取商品 ID"
    with open(f"{os.getcwd()}/DataBase/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)
    # Check in the json array products.products for the product with the id
    product = next((p for p in products["products"] if p["id"] == product_id), None)
    if not product:
        return "商品不存在"
    if product["stock"] < 1:
        return "商品已售完"
    # if pay is not "point"
    if product["pay"] != "point":
        return "此獎品無法使用電電點兌換"

    connection, cursor = link_sql()  # SQL 會話

    if not user_id_exists(discord_user["id"], "user", cursor):
        end(connection, cursor)
        return "使用者不存在"
    user_points = read(discord_user["id"], "point", cursor)
    if user_points < product["price"]:
        end(connection, cursor)
        return "電電點不足"
    user_points -= product["price"]

    write(discord_user["id"], "point", user_points, cursor)
    end(connection, cursor)
    product["stock"] -= 1
    with open(f"{os.getcwd()}/DataBase/products.json", "w", encoding="utf-8") as file:
        json.dump(products, file)
    return "購買成功！"


@app.route("/rollSlot", methods=["POST"])
def roll_slot() -> list:
    data = request.json
    num_draws = int(data.get("numDraws", 1))  # 預設為 1 次抽獎
    connection, cursor = link_sql()  # SQL 會話
    discord_user = session.get("user")
    if not discord_user:
        return "請重新登入"

    # # user = users.get(discord_user["id"])
    if not user_id_exists(discord_user["id"], "user", cursor):
        end(connection, cursor)
        return "使用者不存在"
    with open(f"{os.getcwd()}/DataBase/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)
    # Check in the json array products.products for the product with the id

    product = next((p for p in products["products"] if p["id"] == "slot"), None)
    # product 參考內容 {'name': '貓咪機', 'id': 'slot', 'description': '來抽獎吧', 'price': 1, 'image': 'https://cdn-icons-png.flaticon.com/128/1055/1055823.png', 'stock': 9999, 'category': '遊戲', 'pay': 'ticket', 'url': 'slot'}
    # 用來確認商品是否存在和價格用的
    # 讀使用者的抽獎券和電電點
    user_tickets = read(discord_user["id"], "ticket", cursor)
    user_points = read(discord_user["id"], "point", cursor)
    if user_tickets < product["price"] * num_draws:
        end(connection, cursor)
        easter_egg = (
            "這位好駭客，burp suite 是不能突破我的" if num_draws not in (1, 10) else ""
        )
        return "抽獎券不足\n" + easter_egg
    with open(f"{os.getcwd()}/DataBase/slot.json", "r", encoding="utf-8") as file:
        slot_json = json.load(file)
    for _ in range(num_draws):
        result = random.choices(
            population=slot_json["population"], weights=slot_json["weights"], k=1
        )[0]
        user_points += slot_json["get"][result]
        user_tickets -= product["price"]
    # 更新抽獎券和電電點
    if not discord_user:
        return "請重新登入"
    write(discord_user["id"], "ticket", user_tickets, cursor)
    write(discord_user["id"], "point", user_points, cursor)
    end(connection, cursor)
    easter_egg = (
        f"你是好駭客，破例讓你連抽 {num_draws} 次" if num_draws not in (1, 10) else ""
    )  # 給用 burp suite 偷改前端表單的人一點驚喜
    return [easter_egg + "抽獎成功", slot_json["get"][result], result]


# GitHub login


@app.route("/github/login")
def github_login():
    # Redirect to GitHub's OAuth login page
    # pylint: disable-next = line-too-long
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&scope=user%20repo&redirect_uri={github_redirect_uri}"
    return redirect(github_oauth_url)


@app.route("/github/callback")
def github_callback():
    # Exchange the authorization code for an access token
    code = request.args.get("code")
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": github_client_id,
        "client_secret": github_client_secret,
        "code": code,
    }
    # pylint: disable-next = missing-timeout
    response = requests.post(token_url, headers=headers, data=data)
    session["access_token"] = response.json()["access_token"]

    return redirect(url_for("star_uwu"))


@app.route("/star_uwu")
def star_uwu():
    def insert_user(user_id, table, cursor):  # 初始化（新增）傳入該ID的資料表
        cursor.execute(f"INSERT INTO {table} (uid) VALUE({user_id})")

    if "access_token" not in session:
        print("GitHub access token not found!")
        return redirect(url_for("github_login"))
    # if dc not login
    discord_user = session.get("user")
    if not discord_user:
        # pylint: disable-next = line-too-long
        return redirect(
            f"https://discord.com/api/oauth2/authorize?client_id={discord_client_id}&redirect_uri={github_discord_redirect_uri}&response_type=code&scope=identify+email"
        )
    # 記錄使用者GitHub
    user_url = "https://api.github.com/user"
    headers = {"Authorization": f"token {session['access_token']}"}
    # pylint: disable-next = missing-timeout
    user_response = requests.get(user_url, headers=headers)
    github_username = user_response.json()["login"]
    github_email = user_response.json()["email"]
    connection, cursor = link_sql()  # SQL 會話
    discord_user = session.get("user")
    write(discord_user["id"], "githubName", github_username, cursor)
    write(discord_user["id"], "githubMail", github_email, cursor)
    end(connection, cursor)

    repo_owner = "SCAICT"
    repo_name = "SCAICT-uwu"
    star_url = f"https://api.github.com/user/starred/{repo_owner}/{repo_name}"
    headers = {"Authorization": f"token {session['access_token']}"}
    # Sending a PUT request to star the repository
    # pylint: disable-next = missing-timeout
    response = requests.put(star_url, headers=headers)
    # Checking the response status and returning an appropriate message
    if response.ok:
        print(f"Successfully starred {repo_owner}/{repo_name}! {response}")
        connection, cursor = link_sql()  # SQL 會話
        if not user_id_exists(
            discord_user["id"], "user", cursor
        ):  # 該 user id 不在user表格內，插入該筆使用者資料
            insert_user(discord_user["id"], "user", cursor)
        # if already starred. loveuwu is 1
        if read(discord_user["id"], "loveuwu", cursor):
            end(connection, cursor)
            return render_template("already.html")
        write(discord_user["id"], "loveuwu", 1, cursor)
        user_points = read(discord_user["id"], "point", cursor)
        user_points += 20
        write(discord_user["id"], "point", user_points, cursor)
        end(connection, cursor)
        return render_template("star_success.html")

    return f"Failed to star {repo_owner}/{repo_name}."


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
