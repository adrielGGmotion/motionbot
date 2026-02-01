const { MessageFlags } = require('discord.js');
const stats = require('../index').stats;
const logger = require('../logger');

module.exports = {
    name: 'interactionCreate',
    async execute(interaction) {
        if (!interaction.isChatInputCommand()) return;

        const command = interaction.client.commands.get(interaction.commandName);

        if (!command) {
            console.error(`No command matching ${interaction.commandName} was found.`);
            return;
        }

        try {
            stats.commandsRan++;
            await command.execute(interaction);
        } catch (error) {
            const logPath = logger.logError(error, interaction.commandName);

            // Try to inform the user, but catch any errors in doing so to prevent bot crash
            try {
                const errorContent = {
                    content: `There was an error while executing this command!\nLogs have been saved to \`${logPath}\``,
                    flags: [MessageFlags.Ephemeral]
                };

                if (interaction.replied || interaction.deferred) {
                    await interaction.followUp(errorContent);
                } else {
                    await interaction.reply(errorContent);
                }
            } catch (innerError) {
                console.error('[Failed to send error message to user]:', innerError);
            }
        }
    },
};
