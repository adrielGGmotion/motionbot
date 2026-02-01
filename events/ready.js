const pc = require('picocolors');

module.exports = {
    name: 'clientReady',
    once: true,
    execute(client) {
        process.stdout.write(pc.green('  ✔ ') + `Logged in as ${pc.bold(pc.yellow(client.user.tag))}\n\n`);
        console.log(pc.cyan('✦ Bot is ready and listening for interactions!'));
    },
};
