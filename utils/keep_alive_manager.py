import asyncio
import aiohttp
import logging
from utils.config import Config

logger = logging.getLogger("motionbot")

class KeepAliveManager:
    _task = None

    @classmethod
    async def start(cls):
        if cls._task:
            return

        enabled = Config.GSM_KEEP_ALIVE
        url = Config.GSM_BASE_URL

        if enabled and url:
            logger.info(f"GSMArena Keep-Alive enabled. Pinging every 15s to {url}")
            cls._task = asyncio.create_task(cls._run(url))
        else:
            logger.info("GSMArena Keep-Alive disabled.")

    @classmethod
    async def stop(cls):
        if cls._task:
            cls._task.cancel()
            try:
                await cls._task
            except asyncio.CancelledError:
                pass
            cls._task = None

    @classmethod
    async def reload(cls):
        await cls.stop()
        await cls.start()

    @classmethod
    async def _run(cls, url):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        # Success is silent to avoid log spam
                        pass
            except Exception as e:
                logger.warning(f"[KeepAlive] Ping failed to {url}: {e}")
            
            await asyncio.sleep(15)
