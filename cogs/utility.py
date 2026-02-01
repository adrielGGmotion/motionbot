import discord
from discord import app_commands
from discord.ext import commands
from utils.language_manager import LanguageManager
from utils.command_manager import CommandManager

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check if command is enabled for this guild
        if not CommandManager.is_command_enabled(interaction.command.name, interaction.guild_id):
            await interaction.response.send_message("This command is disabled in this server.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="ping", description="Check if the bot is responsive")
    async def ping(self, interaction: discord.Interaction):
        # We can implement dynamic descriptions using locale later if needed
        # For now, using the key from LanguageManager for the reply
        await interaction.response.send_message(LanguageManager.t('pong_reply'))

async def setup(bot):
    await bot.add_cog(Utility(bot))
