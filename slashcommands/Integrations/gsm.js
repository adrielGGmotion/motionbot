const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, StringSelectMenuBuilder, StringSelectMenuOptionBuilder, ComponentType } = require('discord.js');
const pc = require('picocolors');
const themeManager = require('../../settings/themeManager');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('gsm')
        .setDescription('GSMArena Integration')
        .addSubcommand(subcommand =>
            subcommand
                .setName('search')
                .setDescription('Search for a device')
                .addStringOption(option =>
                    option.setName('query')
                        .setDescription('Device name to search for')
                        .setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('specs')
                .setDescription('Get specifications for a device')
                .addStringOption(option =>
                    option.setName('device_id')
                        .setDescription('The ID of the device (from search)')
                        .setRequired(true))),

    async execute(interaction) {
        const baseUrl = process.env.GSM_BASE_URL;

        if (!baseUrl) {
            return interaction.reply({
                content: '🚫 **GSMArena API URL is not configured.**\nPlease configure it in the dashboard under "Integrations".',
                ephemeral: true
            });
        }

        const subcommand = interaction.options.getSubcommand();

        if (subcommand === 'search') {
            await handleSearch(interaction, baseUrl);
        } else if (subcommand === 'specs') {
            await handleSpecs(interaction, baseUrl);
        }
    }
};

async function handleSearch(interaction, baseUrl) {
    const query = interaction.options.getString('query');
    await interaction.deferReply();

    try {
        const response = await fetch(`${baseUrl}/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

        const data = await response.json();

        // Assuming API returns an array of devices or { data: [...] }
        const devices = Array.isArray(data) ? data : (data.data || []);

        if (devices.length === 0) {
            return interaction.editReply(`❌ No devices found for "**${query}**"`);
        }

        const embed = new EmbedBuilder()
            .setTitle(`📱 Search Results for "${query}"`)
            .setColor(themeManager.getTheme().primary)
            .setFooter({ text: 'GSMArena Integration', iconURL: 'https://www.gsmarena.com/assets/img/logo-3.png' }); // Using generic logo or bot avatar

        // Show top 5 results
        const topDevices = devices.slice(0, 5);
        let description = "";

        topDevices.forEach((device, index) => {
            // Adjust property names based on actual API
            const name = device.name || device.title || 'Unknown Device';
            const id = device.id || device.slug || 'unknown';
            description += `**${index + 1}.** ${name} (\`${id}\`)\n`;
        });

        if (devices.length > 5) {
            description += `\n*...and ${devices.length - 5} more.*`;
        }

        description += `\nUse \`/gsm specs <device_id>\` to see details.`;

        embed.setDescription(description);

        // Optional: Add basic image of first result if available
        if (topDevices[0].img || topDevices[0].image) {
            embed.setThumbnail(topDevices[0].img || topDevices[0].image);
        }

        await interaction.editReply({ embeds: [embed] });

    } catch (error) {
        console.error(pc.red(`[GSM] Search failed: ${error.message}`));
        await interaction.editReply('❌ Failed to fetch data from GSMArena API.');
    }
}

// ... (previous imports)

async function handleSpecs(interaction, baseUrl) {
    const deviceId = interaction.options.getString('device_id');
    await interaction.deferReply();

    try {
        const response = await fetch(`${baseUrl}/device/${deviceId}`);
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

        const device = await response.json();
        if (device.error) {
            return interaction.editReply(`❌ Device not found: ${device.error}`);
        }

        // --- Helpers ---
        const buildHomeEmbed = () => {
            const embed = new EmbedBuilder()
                .setTitle(device.name || device.title || 'Device Specs')
                .setColor(themeManager.getTheme().accent)
                .setThumbnail(device.img || device.image)
                .setTimestamp();

            if (device.quick_spec || device.quickSpec) {
                const q = device.quick_spec || device.quickSpec;
                if (Array.isArray(q)) {
                    q.forEach(s => embed.addFields({ name: s.name, value: s.value, inline: true }));
                }
            } else {
                embed.setDescription('No quick specifications available.');
            }
            return embed;
        };

        const buildCategoryEmbed = (categoryName) => {
            const embed = new EmbedBuilder()
                .setTitle(`${device.name} - ${categoryName}`)
                .setColor(themeManager.getTheme().accent)
                .setThumbnail(device.img || device.image)
                .setTimestamp();

            const dSpec = device.detail_spec || device.detailSpec || [];
            const category = dSpec.find(c => c.category === categoryName);

            if (category) {
                let desc = "";
                category.specifications.forEach(s => {
                    desc += `**${s.name}**: ${s.value}\n`;
                });
                embed.setDescription(desc.substring(0, 4096));
            } else {
                embed.setDescription('No data available for this category.');
            }
            return embed;
        };

        // --- Components ---
        const dSpec = device.detail_spec || device.detailSpec || [];
        const categories = dSpec.map(c => c.category);
        const rows = [];

        if (categories.length > 0) {
            const selectMenu = new StringSelectMenuBuilder()
                .setCustomId('gsm_cat_select')
                .setPlaceholder('Select Specification Category')
                .addOptions(
                    categories.slice(0, 25).map(cat =>
                        new StringSelectMenuOptionBuilder()
                            .setLabel(cat)
                            .setValue(cat)
                            .setDescription(`View details for ${cat}`)
                    )
                );
            rows.push(new ActionRowBuilder().addComponents(selectMenu));
        }

        const homeBtn = new ButtonBuilder()
            .setCustomId('gsm_home_btn')
            .setLabel('Overview')
            .setStyle(ButtonStyle.Secondary)
            .setEmoji('🏠');

        rows.push(new ActionRowBuilder().addComponents(homeBtn));

        // --- Reply & Collector ---
        const message = await interaction.editReply({
            embeds: [buildHomeEmbed()],
            components: rows
        });

        const collector = message.createMessageComponentCollector({
            time: 300000 // 5m
        });

        collector.on('collect', async i => {
            if (i.user.id !== interaction.user.id) {
                return i.reply({ content: 'Only the command user can control this.', ephemeral: true });
            }

            try {
                if (i.isStringSelectMenu()) {
                    await i.update({ embeds: [buildCategoryEmbed(i.values[0])] });
                } else if (i.customId === 'gsm_home_btn') {
                    await i.update({ embeds: [buildHomeEmbed()] });
                }
            } catch (err) {
                console.error("Interaction update failed", err);
            }
        });

        collector.on('end', () => {
            interaction.editReply({ components: [] }).catch(() => { });
        });

    } catch (error) {
        console.error(pc.red(`[GSM] Specs failed: ${error.message}`));
        await interaction.editReply('❌ Failed to fetch device details.');
    }
}
