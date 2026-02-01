import discord
import os
import asyncio
import logging
import time
import pyfiglet
from colorama import Fore, Style, init
from discord.ext import commands
from utils.config import Config
from utils.language_manager import LanguageManager
from utils.keep_alive_manager import KeepAliveManager
from web.app import run_web_server

# Setup Logging
def setup_logging():
    logger = logging.getLogger("motionbot")
    logger.setLevel(logging.INFO)
    
    # File handler for all logs
    fh = logging.FileHandler("bot.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(fh)
    
    # Console handler for CRITICAL only (to avoid mess)
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    logger.addHandler(ch)
    
    # Silence third-party loggers
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("hypercorn").setLevel(logging.WARNING)
    
    return logger

logger = setup_logging()

class Stats:
    commands_ran = 0
    start_time = time.time()

class MotionBot(commands.Bot):
    def __init__(self):
        self.stats = Stats()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        init(autoreset=True) # Initialize colorama
        # 1. Splash Screen
        print("\033[H\033[J", end="") # Clear terminal
        banner = pyfiglet.figlet_format('motionbot', font='slant')
        print(Fore.CYAN + banner)
        print(Style.DIM + LanguageManager.t('startup_tagline'))
        
        print(Fore.BLUE + '➜ ' + LanguageManager.t('bot_initializing'))
        print(Fore.BLUE + '➜ ' + LanguageManager.t('loading_modules'))

        # Load Cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                except Exception as e:
                    logger.error(f'Failed to load extension {filename}: {e}')
        
        # Global Tree Check for Command Toggles
        async def global_check(interaction: discord.Interaction) -> bool:
            from utils.command_manager import CommandManager
            if not interaction.command:
                return True
            
            root_command = interaction.command.root_parent or interaction.command
            if not CommandManager.is_command_enabled(root_command.name, interaction.guild_id):
                await interaction.response.send_message(
                    LanguageManager.t('command_disabled') if 'command_disabled' in LanguageManager._cache.get(LanguageManager._current_lang, {}) else "This command is disabled.",
                    ephemeral=True
                )
                return False
            return True

        self.tree.interaction_check = global_check

        # Start GSMArena Keep-Alive
        await KeepAliveManager.start()
        
        # Start Web Dashboard
        self.loop.create_task(run_web_server(self))
        # Silence hypercorn access logs if possible through config, but here just a note

    async def on_ready(self):
        print(Fore.GREEN + '  ✔ ' + LanguageManager.t('loaded_events', count=Style.BRIGHT + str(len(self.cogs)))) 
        print(Fore.GREEN + '  ✔ ' + LanguageManager.t('commands_deployed'))
        
        print('\n' + Fore.MAGENTA + '✦ ' + LanguageManager.t('attempting_login'))
        # logger.info(f'Logged in as {self.user} (ID: {self.user.id})') # Already in bot.log
        await self.tree.sync()
        print(Fore.CYAN + '  ℹ ' + Style.BRIGHT + 'System: ' + Style.NORMAL + "Dashboard running at " + Fore.BLUE + f"http://localhost:{Config.PORT}")

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        self.stats.commands_ran += 1

def main():
    if not Config.TOKEN:
        logger.error("Token not found in .env")
        return
    
    bot = MotionBot()
    bot.run(Config.TOKEN)

if __name__ == "__main__":
    main()
