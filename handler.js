const fs = require('fs');
const path = require('path');
const config = require('./settings/config');
const languageManager = require('./settings/languageManager');
const pc = require('picocolors');

/**
 * Loads events from the events directory
 * @param {import('discord.js').Client} client 
 */
function loadEvents(client) {
    const eventsPath = path.join(__dirname, 'events');
    const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));

    for (const file of eventFiles) {
        const filePath = path.join(eventsPath, file);
        const event = require(filePath);
        if (event.once) {
            client.once(event.name, (...args) => event.execute(...args));
        } else {
            client.on(event.name, (...args) => event.execute(...args));
        }
    }
    return eventFiles.length;
}

/**
 * Loads slash commands from the slashcommands directory recursively
 * @param {import('discord.js').Client} client 
 */
function loadCommands(client) {
    client.commands = new Map();
    const commandManager = require('./settings/commandManager');
    const commandsPath = path.join(__dirname, 'slashcommands');

    function readCommands(dir) {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);

            if (stat.isDirectory()) {
                readCommands(filePath);
            } else if (file.endsWith('.js')) {
                const command = require(filePath);
                if ('data' in command && 'execute' in command) {
                    const category = path.basename(dir);
                    command.category = category === 'slashcommands' ? 'General' : category;

                    // Only load into the bot's live commands if enabled
                    if (commandManager.isCommandEnabled(command.data.name)) {
                        client.commands.set(command.data.name, command);
                    }
                } else {
                    console.warn(pc.yellow(`[WARNING] The command at ${filePath} is missing target properties.`));
                }
            }
        }
    }

    readCommands(commandsPath);
    return client.commands.size;
}

const { REST, Routes } = require('discord.js');

/**
 * Deploys slash commands to Discord
 * @param {import('discord.js').Client} client 
 */
async function deployCommands(client) {
    const commands = [];
    for (const command of client.commands.values()) {
        commands.push(command.data.toJSON());
    }

    const rest = new REST({ version: '10' }).setToken(config.token);

    try {
        if (config.guildId) {
            await rest.put(
                Routes.applicationGuildCommands(config.clientId, config.guildId),
                { body: commands },
            );
        } else {
            await rest.put(
                Routes.applicationCommands(config.clientId),
                { body: commands },
            );
        }
        return true;
    } catch (error) {
        console.error(error);
        return false;
    }
}

module.exports = { loadEvents, loadCommands, deployCommands };
