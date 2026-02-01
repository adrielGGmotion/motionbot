import json
import os

CONFIG_PATH = 'commands_config.json'

class CommandManager:
    @staticmethod
    def get_config():
        if not os.path.exists(CONFIG_PATH):
            return {"global": {}, "guilds": {}}
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            return {"global": {}, "guilds": {}}

    @staticmethod
    def save_config(config):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)

    @classmethod
    def set_command_status(cls, command_name, enabled, guild_id=None):
        config = cls.get_config()
        
        if guild_id:
            if str(guild_id) not in config["guilds"]:
                config["guilds"][str(guild_id)] = {}
            config["guilds"][str(guild_id)][command_name] = enabled
        else:
            config["global"][command_name] = enabled
            
        cls.save_config(config)

    @classmethod
    def is_command_enabled(cls, command_name, guild_id=None):
        config = cls.get_config()
        
        # 1. Guild Specific
        if guild_id:
            guild_config = config.get("guilds", {}).get(str(guild_id), {})
            if command_name in guild_config:
                return guild_config[command_name]
        
        # 2. Global Setting
        if command_name in config.get("global", {}):
            return config["global"][command_name]
            
        # 3. Default True
        return True
