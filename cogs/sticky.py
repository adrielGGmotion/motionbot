import discord
from discord import app_commands
from discord.ext import commands
from utils.sticky_manager import StickyManager
from utils.language_manager import LanguageManager
from utils.theme_manager import ThemeManager

class Sticky(commands.GroupCog, name="sticky"):
    def __init__(self, bot):
        self.bot = bot
        # Using generic fallback description if translation fails, though LanguageManager handles it
        self.description = "Manage sticky messages"

    @app_commands.command(name="create", description="Create a sticky message in a channel")
    @app_commands.describe(
        name="The unique name for this sticky message",
        channel="The channel where the sticky message will appear",
        message="The content of the sticky message"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def create(self, interaction: discord.Interaction, name: str, channel: discord.TextChannel, message: str):
        # Delete old sticky if exists (handled by manager logic? No, manager logic is for persistence)
        # We need to manually remove the old message from Discord if we can find it
        
        # Check if already exists for this channel to clean up old msg
        existing = StickyManager.get_sticky(interaction.guild_id, channel.id)
        if existing and 'lastMessageId' in existing:
            try:
                old_msg = await channel.fetch_message(existing['lastMessageId'])
                await old_msg.delete()
            except:
                pass

        # Send initial message
        theme = ThemeManager.get_theme()
        color = int(theme['primary'].replace('#', ''), 16)
        embed = discord.Embed(description=message, color=color)
        
        try:
            sent_msg = await channel.send(embed=embed)
            
            # Save to config
            StickyManager.set_sticky(interaction.guild_id, channel.id, {
                "name": name,
                "content": message,
                "lastMessageId": sent_msg.id
            })
            
            await interaction.response.send_message(
                LanguageManager.t('sticky_created', name=name, channel=channel.mention),
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to send messages in that channel.", ephemeral=True)

    @app_commands.command(name="delete", description="Delete a sticky message by name")
    @app_commands.describe(name="The name of the sticky message to delete")
    @app_commands.default_permissions(manage_messages=True)
    async def delete(self, interaction: discord.Interaction, name: str):
        # Find the sticky by name
        # StickyManager doesn't support search by name directly nicely, but we can iterate
        # We need to implement a search helper or do it here
        # StickyManager struct: {guild_id: {channel_id: {name: ...}}}
        
        # Re-implementing search logic similar to legacy
        target_channel_id = None
        target_config = None
        
        # This is a bit inefficient reading file every time but fine for now
        # Ideally we should extend StickyManager to return all guild stickies
        # Let's read raw data safely
        # Note: StickyManager methods are class methods
        
        # We need to expose a way to get all stickies for a guild in manager
        # I added `read_data` as static but maybe not public friendly.
        # Let's rely on reading it again via private access or better: 
        # I realized `StickyManager` implementation I wrote has `get_sticky` but not `get_all_stickies` for a guild publically?
        # Let's check `utils/sticky_manager.py` content I wrote.
        # I wrote `get_sticky(guild, channel)`. 
        # I should probably update `StickyManager` to include `get_all_guild_stickies` or similar.
        # OR just read the file here since I imported json/os in the manager but not here.
        # Actually I can just add `get_all` to `StickyManager` in a quick update or hack it.
        # Hack it for now: we know the structure.
        
        # Wait, I can just use `StickyManager.read_data()` if I made it static. I did.
        
        data = StickyManager.read_data()
        guild_data = data.get(str(interaction.guild_id), {})
        
        for cid, config in guild_data.items():
            if config.get('name') == name:
                target_channel_id = cid
                target_config = config
                break
        
        if not target_channel_id:
            await interaction.response.send_message(
                LanguageManager.t('sticky_not_found', name=name),
                ephemeral=True
            )
            return

        # Confirmation View
        view = ConfirmView(interaction.user.id, name, target_channel_id, target_config, interaction.guild)
        theme = ThemeManager.get_theme()
        embed = discord.Embed(
            title=LanguageManager.t('sticky_confirm_delete_title'),
            description=LanguageManager.t('sticky_confirm_delete_desc', name=name, channel=f"<#{target_channel_id}>"),
            color=int(theme['error'].replace('#', ''), 16)
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmView(discord.ui.View):
    def __init__(self, user_id, name, channel_id, config, guild):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.name = name
        self.channel_id = channel_id
        self.config = config
        self.guild = guild

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Delete message
        try:
            channel = await self.guild.fetch_channel(self.channel_id)
            if channel:
                msg = await channel.fetch_message(self.config['lastMessageId'])
                await msg.delete()
        except:
            pass # Message might be gone

        # Delete from DB
        StickyManager.remove_sticky(interaction.guild_id, self.channel_id)
        
        await interaction.response.edit_message(
            content=LanguageManager.t('sticky_deleted', name=self.name),
            embed=None, view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=LanguageManager.t('wipe_cancelled'), embed=None, view=None)

async def setup(bot):
    await bot.add_cog(Sticky(bot))
