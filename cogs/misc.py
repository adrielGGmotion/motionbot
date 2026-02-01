import discord
from discord import app_commands
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="error-test", description="Test error handling")
    async def error_test(self, interaction: discord.Interaction):
        # Intentionally raise an error to test the global handler
        raise Exception("This is a test error.")

async def setup(bot):
    await bot.add_cog(Misc(bot))
