import discord
import time
from discord import app_commands
from discord.ext import commands
from utils.theme_manager import ThemeManager

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays information about the bot and commands.")
    async def help_command(self, interaction: discord.Interaction):
        theme = ThemeManager.get_theme()
        
        # Calculate categories
        categories = {}
        # Iterate over app commands (Slash)
        # Note: bot.tree.get_commands() returns top level commands.
        for cmd in self.bot.tree.get_commands():
            # If command in a GroupCog or just grouped, we might need to drill down?
            # Cog association is not always directly on the generic AppCommand object in tree list
            # But normally we can infer it or we group manually.
            # actually discord.app_commands.Command has `binding` which might be the cog?
            # A simpler way: Iterate Cogs.
             pass
        
        # Better approach: Iterate Cogs and their app_commands
        for name, cog in self.bot.cogs.items():
            # Get commands from the cog
            # Note: cog.get_app_commands() returns commands registered in that cog
            cmds = cog.get_app_commands()
            if cmds:
                 categories[name] = cmds
        
        # Also catch commands not in cogs (if any)
        # ... logic skipped for simplicity as all mine are in cogs

        uptime_seconds = time.time() - self.bot.start_time if hasattr(self.bot, 'start_time') else 0
        days, rem = divmod(uptime_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

        home_embed = discord.Embed(
            title=f"{self.bot.user.name} Help Interface",
            description="**A powerful Discord utility bot.**", # Hardcoded description from package.json equivalent
            color=int(theme['primary'].replace('#', ''), 16)
        )
        if self.bot.user.avatar:
            home_embed.set_thumbnail(url=self.bot.user.avatar.url)
            
        home_embed.add_field(name="<:bot:1467345982269423637> Bot Name", value=self.bot.user.name, inline=True)
        home_embed.add_field(name="<:idk:1467345975256547374> Version", value="2.0.0 (Python)", inline=True)
        verified_lib = "discord.py" 
        home_embed.add_field(name="<:code:1467345977475334307> Library", value=verified_lib, inline=True)
        # Count total commands
        total_cmds = sum(len(c) for c in categories.values())
        home_embed.add_field(name="<:search:1467345985687523478> Commands", value=str(total_cmds), inline=True)
        home_embed.add_field(name="<:home:1467345984039162050> Servers", value=str(len(self.bot.guilds)), inline=True)
        home_embed.add_field(name="<:clock:1467345980604153927> Uptime", value=uptime_str, inline=True)
        
        home_embed.set_footer(text="Select a category below to navigate", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        view = HelpView(self.bot, categories, home_embed, theme)
        await interaction.response.send_message(embed=home_embed, view=view, ephemeral=True)

class HelpView(discord.ui.View):
    def __init__(self, bot, categories, home_embed, theme):
        super().__init__(timeout=300)
        self.bot = bot
        self.categories = categories
        self.home_embed = home_embed
        self.theme = theme
        
        self.add_item(HelpSelect(categories))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Allow anyone or restrict? Legacy used `ephemeral` so only user sees it anyway.
        return True

class HelpSelect(discord.ui.Select):
    def __init__(self, categories):
        options = [
            discord.SelectOption(label="Home", description="Return to the main bot information page", value="home", emoji="<:home:1467345984039162050>".split(':')[2].replace('>','')) # Try to parse or just use unicode if failing? Legacy implies custom emojis
        ]
        
        # Note: Emoji ID passing in SelectOption requires generic unicode or name:id
        # discord.py handles custom emojis in SelectOption using `emoji` kwarg which can be str or PartialEmoji
        # The string "<:home:1467345984039162050>" might not work directly as `emoji` arg if not parsed
        # I will use a safe fallback for now or try to use discord.PartialEmoji.from_str
        
        from discord import PartialEmoji
        
        def safe_emoji(e_str):
            try:
                return PartialEmoji.from_str(e_str)
            except:
                return None

        # Home
        home_emoji = safe_emoji("<:home:1467345984039162050>")
        options = [
            discord.SelectOption(label="Home", description="Return to the main bot information page", value="home", emoji=home_emoji)
        ]

        sorted_cats = sorted(categories.keys())
        cat_emoji = safe_emoji("<:files:1467345973318520955>")
        
        for cat in sorted_cats:
            options.append(
                discord.SelectOption(label=f"{cat} Commands", description=f"View commands in the {cat} category", value=f"cat_{cat}", emoji=cat_emoji)
            )

        creator_emoji = safe_emoji("<:code:1467345977475334307>")
        options.append(
            discord.SelectOption(label="Creator Info", description="Information about the developer", value="creator", emoji=creator_emoji)
        )

        super().__init__(placeholder="Select a category or page", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        view: HelpView = self.view
        val = self.values[0]
        
        if val == "home":
             await interaction.response.edit_message(embed=view.home_embed)
        
        elif val == "creator":
            embed = discord.Embed(title="<:code:1467345977475334307> Creator Information", color=int(view.theme.get('accent', view.theme['primary']).replace('#', ''), 16))
            embed.description = "This bot is maintained and developed by **Adriel**."
            embed.add_field(name="GitHub", value="[AdrielGGmotion](https://github.com/adrielGGmotion)", inline=True)
            embed.add_field(name="Project Repository", value="[motionbot](https://github.com/adrielGGmotion/motionbot)", inline=True)
            embed.add_field(name="Language", value="Python (discord.py)", inline=True)
            embed.set_thumbnail(url="https://github.com/adrielGGmotion.png")
            await interaction.response.edit_message(embed=embed)
            
        elif val.startswith("cat_"):
            cat_name = val.replace("cat_", "")
            cmds = view.categories.get(cat_name, [])
            
            embed = discord.Embed(
                title=f"<:files:1467345973318520955> {cat_name} Commands",
                color=int(view.theme['primary'].replace('#', ''), 16)
            )
            if view.bot.user.avatar:
                embed.set_thumbnail(url=view.bot.user.avatar.url)
                
            if cmds:
                desc = ""
                for cmd in cmds:
                    # cmd is AppCommand or Group
                    if isinstance(cmd, app_commands.Group):
                         # If group, maybe list subcommands?
                         # For now just list group name
                         desc += f"**/ {cmd.name}**\n{cmd.description}\n\n"
                    else:
                         desc += f"**/ {cmd.name}**\n{cmd.description}\n\n"
                embed.description = desc
            else:
                embed.description = "No commands found."
                
            await interaction.response.edit_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
