import discord
from discord.ext import commands
from utils.sticky_manager import StickyManager
from utils.theme_manager import ThemeManager
from utils.language_manager import LanguageManager
import logging

logger = logging.getLogger("motionbot")

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Events Cog Loaded. Bot is ready: {self.bot.user}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # Sticky Message Logic
        sticky_config = StickyManager.get_sticky(message.guild.id, message.channel.id)
        if sticky_config:
            if StickyManager.is_locked(message.channel.id):
                return
            
            StickyManager.lock(message.channel.id)
            try:
                # Delete old message
                last_id = sticky_config.get('lastMessageId')
                if last_id:
                    try:
                        old_msg = await message.channel.fetch_message(last_id)
                        await old_msg.delete()
                    except discord.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                # Send new sticky
                theme = ThemeManager.get_theme()
                color = int(theme['primary'].replace('#', ''), 16)
                
                embed = discord.Embed(description=sticky_config['content'], color=color)
                new_msg = await message.channel.send(embed=embed)
                
                StickyManager.update_last_message_id(message.guild.id, message.channel.id, new_msg.id)
            
            except Exception as e:
                logger.error(f"Error in sticky message logic: {e}")
            finally:
                StickyManager.unlock(message.channel.id)

    # Global Error Handler for App Commands
    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_app_command_error

    def cog_unload(self):
        self.bot.tree.on_error = self._old_tree_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        from utils.logger import log_error
        
        # Log error in legacy style
        command_name = interaction.command.name if interaction.command else "unknown"
        log_path = log_error(error, command_name)
        
        logger.error(f"Command error in {command_name}: {error}")
        
        # Notify User
        try:
            msg = LanguageManager.t('error_prefix') if 'error_prefix' in LanguageManager._cache.get(LanguageManager._current_lang, {}) else "There was an error while executing this command!"
            msg = f"{msg}\nLogs have been saved to `{log_path}`"
            
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except:
            pass

async def setup(bot):
    await bot.add_cog(Events(bot))
