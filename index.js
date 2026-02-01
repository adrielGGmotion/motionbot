const { Client, GatewayIntentBits } = require('discord.js');
const figlet = require('figlet');
const pc = require('picocolors');
const config = require('./settings/config');
const languageManager = require('./settings/languageManager');
const keepAliveManager = require('./settings/keepAliveManager');
const { loadEvents, loadCommands, deployCommands } = require('./handler');

// Global Bot Stats
const stats = {
    commandsRan: 0,
    startTime: Date.now(),
};

module.exports = { stats };

async function init() {
    // 1. Splash Screen
    console.clear();
    console.log(
        pc.cyan(
            figlet.textSync('motionbot', {
                font: 'Slant',
                horizontalLayout: 'default',
                verticalLayout: 'default',
            })
        )
    );
    console.log(pc.dim(languageManager.t('startup_tagline')));

    // 2. Initialize Client
    console.log(pc.blue('➜ ') + languageManager.t('bot_initializing'));
    const client = new Client({
        intents: [
            GatewayIntentBits.Guilds,
            GatewayIntentBits.GuildMessages,
            GatewayIntentBits.MessageContent,
        ],
    });

    // 3. Load Modules
    try {
        console.log(pc.blue('➜ ') + languageManager.t('loading_modules'));

        const eventCount = loadEvents(client);
        console.log(pc.green('  ✔ ') + languageManager.t('loaded_events', { count: pc.bold(eventCount) }));

        const commandCount = loadCommands(client);
        console.log(pc.green('  ✔ ') + languageManager.t('loaded_commands', { count: pc.bold(commandCount) }));

        // 4. Deploy Commands
        console.log(pc.blue('➜ ') + languageManager.t('deploying_commands'));
        const success = await deployCommands(client);
        if (success) {
            console.log(pc.green('  ✔ ') + languageManager.t('commands_deployed'));
        } else {
            console.log(pc.red('  ✖ ') + languageManager.t('commands_deploy_failed'));
        }

        // 5a. Init Keep Alive
        keepAliveManager.init();

        // 5. Configuration Check
        if (!config.token || config.token === 'YOUR_TOKEN_HERE') {
            console.log('\n' + pc.red(`✖ ${languageManager.t('error_prefix')}`) + pc.bold(languageManager.t('token_missing')));
            console.log(pc.red('  ') + languageManager.t('update_env'));
            process.exit(1);
        }

        // 5. Start Dashboard
        const { startDashboard } = require('./web/dashboard');
        startDashboard(client, stats);

        // 6. Login
        console.log('\n' + pc.magenta('✦ ') + languageManager.t('attempting_login'));
        await client.login(config.token);

    } catch (error) {
        console.error('\n' + pc.red(`✘ ${languageManager.t('critical_error')}`));
        console.error(pc.red(`  ${error.message}`));
        if (error.code === 'TokenInvalid') {
            console.log(pc.yellow(`\n  ${languageManager.t('check_token')}`));
        }
        process.exit(1);
    }
}

init();
