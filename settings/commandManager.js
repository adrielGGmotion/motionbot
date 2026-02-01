const fs = require('fs');
const path = require('path');

const configPath = path.join(__dirname, 'commands_config.json');

/**
 * Gets the current status of all commands
 * @returns {Object}
 */
function getCommandsConfig() {
    if (!fs.existsSync(configPath)) {
        return {};
    }
    try {
        return JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (e) {
        console.error('Error reading commands_config.json:', e);
        return {};
    }
}

/**
 * Saves the status of a command
 * @param {string} commandName 
 * @param {boolean} enabled 
 */
function setCommandStatus(commandName, enabled) {
    const config = getCommandsConfig();
    config[commandName] = enabled;
    fs.writeFileSync(configPath, JSON.stringify(config, null, 4));
}

/**
 * Checks if a command is enabled
 * @param {string} commandName 
 * @returns {boolean}
 */
function isCommandEnabled(commandName) {
    const config = getCommandsConfig();
    // Default to true if not specified
    return config[commandName] !== false;
}

module.exports = {
    getCommandsConfig,
    setCommandStatus,
    isCommandEnabled
};
