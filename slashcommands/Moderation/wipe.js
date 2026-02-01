const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, PermissionFlagsBits, MessageFlags } = require('discord.js');
const themeManager = require('../../settings/themeManager');
const languageManager = require('../../settings/languageManager');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('wipe')
        .setDescription('Deletes all messages from this channel (up to 14 days old)')
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),

    async execute(interaction) {
        const theme = themeManager.getTheme();
        const channel = interaction.channel;

        // Check if bot has permissions
        const botPermissions = channel.permissionsFor(interaction.guild.members.me);
        if (!botPermissions.has(PermissionFlagsBits.ManageMessages) && !botPermissions.has(PermissionFlagsBits.Administrator)) {
            return interaction.reply({
                content: languageManager.t('wipe_no_perms'),
                ephemeral: true
            });
        }

        const confirmEmbed = new EmbedBuilder()
            .setTitle(languageManager.t('wipe_confirm_title'))
            .setDescription(languageManager.t('wipe_confirm_desc'))
            .setColor(theme.error || '#ff0000');

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('confirm_wipe')
                    .setLabel(languageManager.t('wipe_confirm_label'))
                    .setStyle(ButtonStyle.Danger),
                new ButtonBuilder()
                    .setCustomId('cancel_wipe')
                    .setLabel(languageManager.t('wipe_cancel_label'))
                    .setStyle(ButtonStyle.Secondary),
            );

        const response = await interaction.reply({
            embeds: [confirmEmbed],
            components: [row],
            flags: [MessageFlags.Ephemeral]
        });

        const collectorFilter = i => i.user.id === interaction.user.id;

        try {
            const confirmation = await response.awaitMessageComponent({ filter: collectorFilter, time: 30000 });

            if (confirmation.customId === 'confirm_wipe') {
                // Initial update to show work in progress
                await confirmation.update({ content: languageManager.t('wipe_in_progress'), embeds: [], components: [] });

                let totalDeleted = 0;
                try {
                    // Discord bulkDelete limit is 100.
                    const deleted = await channel.bulkDelete(100, true);
                    totalDeleted = deleted.size;
                } catch (error) {
                    console.error('Error wiping channel:', error);
                    // Since we already used confirmation.update, we must followUp or editReply
                    return interaction.followUp({ content: languageManager.t('wipe_error'), flags: [MessageFlags.Ephemeral] });
                }

                const successEmbed = new EmbedBuilder()
                    .setDescription(languageManager.t('wipe_success', { count: totalDeleted }))
                    .setColor(theme.primary || '#00ff00');

                const successMsg = await interaction.followUp({ embeds: [successEmbed], fetchReply: true, ephemeral: false });

                setTimeout(async () => {
                    try {
                        await successMsg.delete();
                    } catch (e) {
                        // Ignore if message already deleted or not found
                    }
                }, 5000);

            } else if (confirmation.customId === 'cancel_wipe') {
                await confirmation.update({ content: languageManager.t('wipe_cancelled'), embeds: [], components: [] });
            }
        } catch (e) {
            // Only update if it was a timeout (confirmation will be undefined/rejected)
            if (e.code === 'InteractionCollectorError' || !interaction.replied) {
                await interaction.editReply({ content: languageManager.t('wipe_timeout'), embeds: [], components: [] });
            } else {
                console.error('Wipe command error:', e);
            }
        }
    },
};
