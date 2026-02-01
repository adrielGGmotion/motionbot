import json
import os

STORAGE_PATH = 'stickyMessages.json'
locks = set()

class StickyManager:
    @staticmethod
    def read_data():
        if not os.path.exists(STORAGE_PATH):
            return {}
        try:
            with open(STORAGE_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading sticky data: {e}")
            return {}

    @staticmethod
    def write_data(data):
        try:
            with open(STORAGE_PATH, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error writing sticky data: {e}")

    @classmethod
    def get_sticky(cls, guild_id, channel_id):
        data = cls.read_data()
        return data.get(str(guild_id), {}).get(str(channel_id))

    @classmethod
    def set_sticky(cls, guild_id, channel_id, config):
        data = cls.read_data()
        g_id = str(guild_id)
        if g_id not in data:
            data[g_id] = {}
        data[g_id][str(channel_id)] = config
        cls.write_data(data)

    @classmethod
    def remove_sticky(cls, guild_id, channel_id):
        data = cls.read_data()
        g_id = str(guild_id)
        if g_id in data and str(channel_id) in data[g_id]:
            del data[g_id][str(channel_id)]
            cls.write_data(data)

    @classmethod
    def update_last_message_id(cls, guild_id, channel_id, message_id):
        data = cls.read_data()
        g_id = str(guild_id)
        c_id = str(channel_id)
        if g_id in data and c_id in data[g_id]:
            data[g_id][c_id]['lastMessageId'] = message_id
            cls.write_data(data)

    @staticmethod
    def is_locked(channel_id):
        return channel_id in locks

    @staticmethod
    def lock(channel_id):
        locks.add(channel_id)

    @staticmethod
    def unlock(channel_id):
        if channel_id in locks:
            locks.remove(channel_id)
