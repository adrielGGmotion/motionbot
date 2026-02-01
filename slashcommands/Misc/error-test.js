const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('error-test')
        .setDescription('Intentionally throws an error to test the logger.'),
    async execute(interaction) {
        throw new Error('This is a test error to verify the command error handling and logging system.');
    },
};
