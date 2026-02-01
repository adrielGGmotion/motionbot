require('dotenv').config();

const config = {
    token: process.env.DISCORD_TOKEN,
    prefix: process.env.PREFIX || '^',
    clientId: process.env.CLIENT_ID,
    guildId: process.env.GUILD_ID,
    lanAccess: process.env.DASHBOARD_LAN_ACCESS === 'true',
};

// Simple validation
const missing = Object.entries(config)
    .filter(([key, value]) => !value && key !== 'guildId') // guildId is often optional for global commands but good to have
    .map(([key]) => key);

if (missing.length > 0) {
    console.error(`Missing configuration for: ${missing.join(', ')}`);
    // Note: We don't exit here so the index.js can handle it gracefully with visuals
}

module.exports = config;
