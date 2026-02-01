import discord
import os
import asyncio
import logging
from discord.ext import commands
from utils.config import Config
from utils.language_manager import LanguageManager
from utils.keep_alive_manager import KeepAliveManager
from web.app import run_web_server

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("motionbot")

class MotionBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Load Cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f'Loaded extension: {filename}')
        
        # Start GSMArena Keep-Alive
        await KeepAliveManager.start()
        
        # Start Web Dashboard
        self.loop.create_task(run_web_server(self))
        logger.info("Web Dashboard Task Started")

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.tree.sync()
        logger.info('Slash commands synced')

def main():
    if not Config.TOKEN:
        logger.error("Token not found in .env")
        return
    
    bot = MotionBot()
    bot.run(Config.TOKEN)

if __name__ == "__main__":
    main()
