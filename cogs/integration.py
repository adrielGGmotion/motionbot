import discord
from discord import app_commands
from discord.ext import commands
from utils.config import Config
from utils.theme_manager import ThemeManager
import aiohttp
import urllib.parse

class Integration(commands.GroupCog, name="gsm"):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = Config.GSM_BASE_URL

    @app_commands.command(name="search", description="Search for a device")
    @app_commands.describe(query="Device name to search for")
    async def search(self, interaction: discord.Interaction, query: str):
        if not self.base_url:
            await interaction.response.send_message("GSMArena API URL is not configured.", ephemeral=True)
            return

        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/search?q={urllib.parse.quote(query)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(f"API Error: {resp.status}")
                        return
                    
                    data = await resp.json()
                    devices = data if isinstance(data, list) else data.get('data', [])

                    if not devices:
                        await interaction.followup.send(f"No devices found for **{query}**")
                        return

                    theme = ThemeManager.get_theme()
                    embed = discord.Embed(
                        title=f"Search Results for \"{query}\"",
                        color=int(theme['primary'].replace('#', ''), 16)
                    )
                    embed.set_footer(text="GSMArena Integration", icon_url="https://www.gsmarena.com/assets/img/logo-3.png")

                    description = ""
                    for i, device in enumerate(devices[:5]):
                        name = device.get('name') or device.get('title') or 'Unknown'
                        did = device.get('id') or device.get('slug') or 'unknown'
                        description += f"**{i+1}.** {name} (`{did}`)\n"
                    
                    if len(devices) > 5:
                        description += f"\n*...and {len(devices)-5} more.*"
                    
                    description += "\nUse `/gsm specs <device_id>` to see details."
                    embed.description = description
                    
                    if devices[0].get('img') or devices[0].get('image'):
                        embed.set_thumbnail(url=devices[0].get('img') or devices[0].get('image'))

                    await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send("Failed to fetch data.")
            print(f"GSM Search Error: {e}")

    @app_commands.command(name="specs", description="Get specifications for a device")
    @app_commands.describe(device_id="The ID of the device")
    async def specs(self, interaction: discord.Interaction, device_id: str):
        if not self.base_url:
             await interaction.response.send_message("GSMArena API URL is not configured.", ephemeral=True)
             return

        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/device/{device_id}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(f"API Error: {resp.status}")
                        return
                    
                    device = await resp.json()
                    if device.get('error'):
                         await interaction.followup.send(f"Device not found: {device.get('error')}")
                         return

                    view = SpecsView(device)
                    await interaction.followup.send(embed=view.build_home_embed(), view=view)
        except Exception as e:
            await interaction.followup.send("Failed to fetch details.")
            print(f"GSM Specs Error: {e}")

class SpecsView(discord.ui.View):
    def __init__(self, device):
        super().__init__(timeout=300)
        self.device = device
        self.theme = ThemeManager.get_theme()
        
        # Setup specific commands if categories exist
        specs = device.get('detail_spec') or device.get('detailSpec') or []
        categories = [c.get('category') for c in specs if c.get('category')]
        
        if categories:
            self.add_item(CategorySelect(categories[:25])) # Discord limit 25

    def build_home_embed(self):
        embed = discord.Embed(
            title=self.device.get('name') or self.device.get('title') or "Specs",
            color=int(self.theme['accent'].replace('#', ''), 16)
        )
        embed.set_thumbnail(url=self.device.get('img') or self.device.get('image'))
        
        quick = self.device.get('quick_spec') or self.device.get('quickSpec')
        if quick and isinstance(quick, list):
            for q in quick:
                embed.add_field(name=q.get('name', 'Info'), value=q.get('value', 'N/A'), inline=True)
        else:
            embed.description = "No quick specs available."
            
        return embed

    def build_category_embed(self, category_name):
        embed = discord.Embed(
            title=f"{self.device.get('name')} - {category_name}",
            color=int(self.theme['accent'].replace('#', ''), 16)
        )
        embed.set_thumbnail(url=self.device.get('img') or self.device.get('image'))
        
        specs = self.device.get('detail_spec') or self.device.get('detailSpec') or []
        cat_data = next((c for c in specs if c.get('category') == category_name), None)
        
        if cat_data:
            desc = ""
            for s in cat_data.get('specifications', []):
                desc += f"**{s.get('name')}**: {s.get('value')}\n"
            embed.description = desc[:4096]
        else:
            embed.description = "No data."
            
        return embed

    @discord.ui.button(label="Overview", style=discord.ButtonStyle.secondary, emoji="🏠")
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.build_home_embed())

class CategorySelect(discord.ui.Select):
    def __init__(self, categories):
        options = [discord.SelectOption(label=c, description=f"View {c}") for c in categories]
        super().__init__(placeholder="Select Specification Category", options=options, custom_id="gsm_cat_select")

    async def callback(self, interaction: discord.Interaction):
        view: SpecsView = self.view
        embed = view.build_category_embed(self.values[0])
        await interaction.response.edit_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Integration(bot))
