import asyncio
import os
import aiohttp
from quart import Quart, jsonify, request, send_from_directory, Response
from utils.config import Config
from utils.theme_manager import ThemeManager
from utils.language_manager import LanguageManager
from utils.command_manager import CommandManager
import time

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
app = Quart(__name__, static_folder=WEB_DIR, static_url_path='')
bot_instance = None

@app.route('/')
async def index():
    return await send_from_directory(WEB_DIR, 'index.html')

@app.route('/style.css')
async def style():
    return await send_from_directory(WEB_DIR, 'style.css')

@app.route('/api/stats')
async def api_stats():
    if not bot_instance:
        return jsonify({"error": "Bot not initialized"}), 500
    
    return jsonify({
        "uptime": time.time() - bot_instance.stats.start_time,
        "commandsRan": bot_instance.stats.commands_ran,
        "botName": bot_instance.user.name if bot_instance.user else "MotionBot",
        "botTag": str(bot_instance.user) if bot_instance.user else "MotionBot#0000",
        "status": "Online" if bot_instance.is_ready() else "Initializing",
        "guilds": len(bot_instance.guilds)
    })

@app.route('/api/avatar')
async def api_avatar():
    if not bot_instance or not bot_instance.user:
        return "Bot not ready", 404
        
    asset = bot_instance.user.display_avatar.with_format("png").with_size(128)
    data = await asset.read()
    return Response(data, mimetype='image/png')

@app.route('/api/developer')
async def api_developer():
    # Cache logic could be added here, simplified for now
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://github.com/adrielGGmotion.png') as resp:
                if resp.status == 200:
                    data = await resp.read()
                    return Response(data, mimetype='image/png')
    except:
        pass
    return "Error", 500

@app.route('/api/theme', methods=['GET', 'POST'])
async def api_theme():
    if request.method == 'POST':
        data = await request.get_json()
        if ThemeManager.set_theme(data):
            return jsonify({"success": True})
        return jsonify({"success": False}), 500
    
    return jsonify(ThemeManager.get_theme())

@app.route('/api/guilds')
async def api_guilds():
    if not bot_instance:
        return jsonify([])
    
    guild_list = []
    for g in bot_instance.guilds:
        icon_url = g.icon.url if g.icon else None
        guild_list.append({
            "id": str(g.id),
            "name": g.name,
            "icon": icon_url
        })
    return jsonify(guild_list)

@app.route('/api/commands')
async def api_commands():
    guild_id = request.args.get('guildId')
    
    # List commands from bot's tree or cogs
    # For now, we will construct a list from the running bot
    command_list = []
    
    # Regular commands
    for cmd in bot_instance.commands:
        command_list.append({
            "name": cmd.name,
            "description": cmd.brief or cmd.help or "No description",
            "category": cmd.cog_name or "General",
            "enabled": CommandManager.is_command_enabled(cmd.name, guild_id)
        })
        
    # App commands (Slash)
    # Note: accessing internals of app commands might be different
    # We will assume Hybrid commands or tree commands
    # This part might need refinement once we have cogs loaded and synced
    
    return jsonify(command_list)

@app.route('/api/commands/toggle', methods=['POST'])
async def api_commands_toggle():
    data = await request.get_json()
    name = data.get('name')
    enabled = data.get('enabled')
    guild_id = data.get('guildId')
    
    CommandManager.set_command_status(name, enabled, guild_id)
    
    # Ideally trigger a sync or reload here?
    # Command enabling/disabling via checks is instant if we use the manager in the check check
    
    return jsonify({"success": True})

@app.route('/api/language', methods=['GET', 'POST'])
async def api_language():
    if request.method == 'POST':
        data = await request.get_json()
        lang = data.get('language')
        if LanguageManager.set_language(lang):
             return jsonify({"success": True})
        return jsonify({"success": False}), 500

    return jsonify({
        "current": LanguageManager.get_language(),
        "available": LanguageManager.get_available_languages()
    })

@app.route('/api/config/gsm')
async def api_config_gsm():
    return jsonify({
        "url": Config.GSM_BASE_URL,
        "keepAlive": Config.GSM_KEEP_ALIVE
    })

@app.route('/api/config/env', methods=['POST'])
async def api_config_env():
    data = await request.get_json() # Expects { KEY: VALUE }
    env_path = os.path.join(os.getcwd(), '.env')
    
    try:
        new_lines = []
        keys_updated = set()
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, _ = line.split('=', 1)
                    if key in data:
                        new_lines.append(f"{key}={data[key]}")
                        keys_updated.add(key)
                        # Optional: Update os.environ if needed immediately
                        os.environ[key] = str(data[key])
                        continue
                new_lines.append(line)
        
        # Add new keys
        for key, value in data.items():
            if key not in keys_updated:
                new_lines.append(f"{key}={value}")
                os.environ[key] = str(value)
        
        with open(env_path, 'w') as f:
            f.write('\n'.join(new_lines) + '\n')
            
        # If GSM_KEEP_ALIVE or GSM_BASE_URL changed, reload KeepAliveManager
        if 'GSM_KEEP_ALIVE' in data or 'GSM_BASE_URL' in data:
            # We need to update Config class too since it's used by others
            from utils.keep_alive_manager import KeepAliveManager
            if 'GSM_BASE_URL' in data: Config.GSM_BASE_URL = data['GSM_BASE_URL']
            if 'GSM_KEEP_ALIVE' in data: Config.GSM_KEEP_ALIVE = str(data['GSM_KEEP_ALIVE']).lower() == 'true'
            await KeepAliveManager.reload()

        return jsonify({"success": True})
    except Exception as e:
        print(f"Failed to update .env: {e}")
        return jsonify({"success": False}), 500

# TODO: /api/config/env implementation (skipping for safety/complexity unless requested)

async def run_web_server(bot):
    global bot_instance
    bot_instance = bot
    port = Config.PORT
    host = '0.0.0.0' if Config.LAN_ACCESS else '127.0.0.1'
    
    # Suppress excessive logging from hypercorn/quart if needed
    await app.run_task(host=host, port=port)
