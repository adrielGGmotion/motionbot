import discord
from discord import app_commands
from discord.ext import commands
from utils.language_manager import LanguageManager
from utils.theme_manager import ThemeManager

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wipe", description="Deletes all messages from this channel (up to 14 days old)")
    @app_commands.default_permissions(administrator=True)
    async def wipe(self, interaction: discord.Interaction):
        # Check bot permissions
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
             await interaction.response.send_message(LanguageManager.t('wipe_no_perms'), ephemeral=True)
             return

        # Confirmation
        view = WipeConfirmView(interaction)
        theme = ThemeManager.get_theme()
        embed = discord.Embed(
            title=LanguageManager.t('wipe_confirm_title'),
            description=LanguageManager.t('wipe_confirm_desc'),
            color=int(theme['error'].replace('#', ''), 16)
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class WipeConfirmView(discord.ui.View):
    def __init__(self, original_interaction):
        super().__init__(timeout=30)
        self.original_interaction = original_interaction

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.original_interaction.user.id

    @discord.ui.button(label="Confirm Wipe", style=discord.ButtonStyle.danger) # Label from LanguageManager ideally
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=LanguageManager.t('wipe_in_progress'), embed=None, view=None)
        
        try:
            deleted = await interaction.channel.purge(limit=100) # Bulk delete limit
            count = len(deleted)
            
            theme = ThemeManager.get_theme()
            success_embed = discord.Embed(
                description=LanguageManager.t('wipe_success', count=count),
                color=int(theme['primary'].replace('#', ''), 16)
            )
            
            # Send success message (not ephemeral, then delete)
            msg = await interaction.channel.send(embed=success_embed)
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
                
        except Exception as e:
            await interaction.followup.send(LanguageManager.t('wipe_error'), ephemeral=True)
            print(f"Wipe error: {e}")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=LanguageManager.t('wipe_cancelled'), embed=None, view=None)

import asyncio

async def setup(bot):
    await bot.add_cog(Moderation(bot))
