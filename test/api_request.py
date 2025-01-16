# Standard imports
import json
import os

# Third-party imports
from dotenv import load_dotenv
import requests

load_dotenv(f"{os.getcwd()}/.env", verbose=True, override=True)
guild_id = os.getenv("GUILD_ID")
api_key = os.getenv("DISCORD_TOKEN")
headers = {
    "Authorization": f"Bot {api_key}",
    "Content-Type": "application/json",
}
url = f"https://discord.com/api/v10/guilds/{guild_id}/members/898141506588770334"
response = requests.get(url, headers=headers, timeout=5)

formatted_json = json.dumps(response.json(), indent=4)
print(formatted_json)
