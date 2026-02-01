const { EmbedBuilder, Events } = require('discord.js');
const stickyManager = require('../events/stickyManager');
const themeManager = require('../settings/themeManager');

module.exports = {
    name: Events.MessageCreate,
    async execute(message) {
        if (!message.guild || message.author.bot) return;

        const guildId = message.guild.id;
        const channelId = message.channel.id;
        const stickyConfig = stickyManager.getSticky(guildId, channelId);

        if (!stickyConfig) return;

        // If already processing a sticky message for this channel, skip
        if (stickyManager.isLocked(channelId)) return;

        // Lock the channel
        stickyManager.lock(channelId);

        try {
            // Try to delete the old sticky message
            if (stickyConfig.lastMessageId) {
                try {
                    const oldMessage = await message.channel.messages.fetch(stickyConfig.lastMessageId).catch(() => null);
                    if (oldMessage && oldMessage.deletable) await oldMessage.delete();
                } catch (e) {
                    // Ignore error
                }
            }

            const theme = themeManager.getTheme();

            // Send new sticky message
            const newSticky = await message.channel.send({
                embeds: [new EmbedBuilder().setDescription(stickyConfig.content).setColor(theme.primary)]
            });

            // Update the lastMessageId in storage
            stickyManager.updateLastMessageId(guildId, channelId, newSticky.id);

        } catch (error) {
            console.error(`Error handling sticky message in ${channelId}:`, error);
        } finally {
            // Unlock the channel
            stickyManager.unlock(channelId);
        }
    },
};
