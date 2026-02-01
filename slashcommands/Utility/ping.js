const { SlashCommandBuilder } = require('discord.js');
const languageManager = require('../../settings/languageManager');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('ping')
        .setDescription(languageManager.t('ping_desc')),
    async execute(interaction) {
        await interaction.reply(languageManager.t('pong_reply'));
    },
};
