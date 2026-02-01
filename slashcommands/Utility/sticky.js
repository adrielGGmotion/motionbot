const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ChannelType, PermissionFlagsBits } = require('discord.js');
const stickyManager = require('../../events/stickyManager');
const themeManager = require('../../settings/themeManager');
const languageManager = require('../../settings/languageManager');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('sticky')
        .setDescription(languageManager.t('sticky_desc_main'))
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages)
        .addSubcommand(subcommand =>
            subcommand
                .setName('create')
                .setDescription(languageManager.t('sticky_desc_create'))
                .addStringOption(option =>
                    option.setName(languageManager.t('sticky_name_label')).setDescription(languageManager.t('sticky_name_desc')).setRequired(true))
                .addChannelOption(option =>
                    option.setName(languageManager.t('sticky_channel_label')).setDescription(languageManager.t('sticky_channel_desc')).addChannelTypes(ChannelType.GuildText).setRequired(true))
                .addStringOption(option =>
                    option.setName(languageManager.t('sticky_message_label')).setDescription(languageManager.t('sticky_message_desc')).setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('delete')
                .setDescription(languageManager.t('sticky_desc_delete'))
                .addStringOption(option =>
                    option.setName(languageManager.t('sticky_name_label')).setDescription(languageManager.t('sticky_name_desc')).setRequired(true))),

    async execute(interaction) {
        const subcommand = interaction.options.getSubcommand();
        const guildId = interaction.guildId;
        const theme = themeManager.getTheme();

        if (subcommand === 'create') {
            const name = interaction.options.getString(languageManager.t('sticky_name_label'));
            const channel = interaction.options.getChannel(languageManager.t('sticky_channel_label'));
            const messageContent = interaction.options.getString(languageManager.t('sticky_message_label'));

            // Delete old sticky message if it exists in this channel
            const existingSticky = stickyManager.getSticky(guildId, channel.id);
            if (existingSticky && existingSticky.lastMessageId) {
                try {
                    const oldMsg = await channel.messages.fetch(existingSticky.lastMessageId).catch(() => null);
                    if (oldMsg && oldMsg.deletable) await oldMsg.delete();
                } catch (e) { /* ignore */ }
            }

            // Send the first sticky message
            const sentMessage = await channel.send({
                embeds: [new EmbedBuilder().setDescription(messageContent).setColor(theme.primary)]
            });

            stickyManager.setSticky(guildId, channel.id, {
                name: name,
                content: messageContent,
                lastMessageId: sentMessage.id
            });

            await interaction.reply({
                content: languageManager.t('sticky_created', { name: name, channel: channel.toString() }),
                ephemeral: true
            });

        } else if (subcommand === 'delete') {
            const name = interaction.options.getString(languageManager.t('sticky_name_label'));
            const stickies = stickyManager.getAllStickies(guildId);

            let channelId = null;
            let stickyConfig = null;
            for (const id in stickies) {
                if (stickies[id].name === name) {
                    channelId = id;
                    stickyConfig = stickies[id];
                    break;
                }
            }

            if (!channelId) {
                return interaction.reply({
                    content: languageManager.t('sticky_not_found', { name: name }),
                    ephemeral: true
                });
            }

            const confirmEmbed = new EmbedBuilder()
                .setTitle(languageManager.t('wipe_confirm_title')) // Reuse some generic titles if appropriate or add new once
                .setDescription(languageManager.t('wipe_confirm_desc')) // This is specific to wipe, let's just use it for now or keep it hardcoded if I didn't add it to en.json
                .setColor(theme.error);

            // Actually, let's use specific sticky strings
            confirmEmbed.setTitle(languageManager.t('sticky_confirm_delete_title'));
            confirmEmbed.setDescription(languageManager.t('sticky_confirm_delete_desc', { name: name, channel: `<#${channelId}>` }));

            const row = new ActionRowBuilder()
                .addComponents(
                    new ButtonBuilder()
                        .setCustomId('confirm_delete_sticky')
                        .setLabel(languageManager.t('wipe_confirm_label'))
                        .setStyle(ButtonStyle.Danger),
                    new ButtonBuilder()
                        .setCustomId('cancel_delete_sticky')
                        .setLabel(languageManager.t('wipe_cancel_label'))
                        .setStyle(ButtonStyle.Secondary),
                );

            const response = await interaction.reply({
                embeds: [confirmEmbed],
                components: [row],
                ephemeral: true
            });

            const collectorFilter = i => i.user.id === interaction.user.id;

            try {
                const confirmation = await response.awaitMessageComponent({ filter: collectorFilter, time: 60000 });

                if (confirmation.customId === 'confirm_delete_sticky') {
                    // Try to delete the actual message first
                    try {
                        const channel = await interaction.guild.channels.fetch(channelId);
                        const lastMsg = await channel.messages.fetch(stickyConfig.lastMessageId);
                        if (lastMsg) await lastMsg.delete();
                    } catch (e) {
                        // Ignore if message not found
                    }

                    stickyManager.removeStickyByName(guildId, name);
                    await confirmation.update({
                        content: languageManager.t('sticky_deleted', { name: name }),
                        embeds: [],
                        components: []
                    });
                } else if (confirmation.customId === 'cancel_delete_sticky') {
                    await confirmation.update({ content: languageManager.t('wipe_cancelled'), embeds: [], components: [] });
                }
            } catch (e) {
                await interaction.editReply({ content: languageManager.t('wipe_timeout'), embeds: [], components: [] });
            }
        }
    },
};
