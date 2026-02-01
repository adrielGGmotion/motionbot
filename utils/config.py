import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv('DISCORD_TOKEN')
    CLIENT_ID = os.getenv('CLIENT_ID')
    GUILD_ID = os.getenv('GUILD_ID') # Optional, for dev
    GSM_BASE_URL = os.getenv('GSM_BASE_URL')
    GSM_KEEP_ALIVE = os.getenv('GSM_KEEP_ALIVE', 'false').lower() == 'true'
    LAN_ACCESS = os.getenv('DASHBOARD_LAN_ACCESS', 'false').lower() == 'true'
    PORT = int(os.getenv('PORT', 3000))
