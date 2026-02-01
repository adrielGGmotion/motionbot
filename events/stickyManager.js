const fs = require('fs');
const path = require('path');

const STORAGE_PATH = path.join(__dirname, '../settings/stickyMessages.json');
const locks = new Set();

function readData() {
    try {
        if (!fs.existsSync(STORAGE_PATH)) {
            return {};
        }
        const data = fs.readFileSync(STORAGE_PATH, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error reading sticky messages data:', error);
        return {};
    }
}

function writeData(data) {
    try {
        fs.writeFileSync(STORAGE_PATH, JSON.stringify(data, null, 2));
    } catch (error) {
        console.error('Error writing sticky messages data:', error);
    }
}

module.exports = {
    getSticky: (guildId, channelId) => {
        const data = readData();
        return data[guildId]?.[channelId];
    },
    getAllStickies: (guildId) => {
        const data = readData();
        return data[guildId] || {};
    },
    setSticky: (guildId, channelId, config) => {
        const data = readData();
        if (!data[guildId]) data[guildId] = {};
        data[guildId][channelId] = config;
        writeData(data);
    },
    removeStickyByChannel: (guildId, channelId) => {
        const data = readData();
        if (data[guildId]) {
            delete data[guildId][channelId];
            writeData(data);
        }
    },
    removeStickyByName: (guildId, name) => {
        const data = readData();
        if (data[guildId]) {
            let found = false;
            for (const channelId in data[guildId]) {
                if (data[guildId][channelId].name === name) {
                    delete data[guildId][channelId];
                    found = true;
                    writeData(data);
                    return true;
                }
            }
        }
        return false;
    },
    updateLastMessageId: (guildId, channelId, messageId) => {
        const data = readData();
        if (data[guildId] && data[guildId][channelId]) {
            data[guildId][channelId].lastMessageId = messageId;
            writeData(data);
        }
    },
    isLocked: (channelId) => locks.has(channelId),
    lock: (channelId) => locks.add(channelId),
    unlock: (channelId) => locks.delete(channelId)
};
