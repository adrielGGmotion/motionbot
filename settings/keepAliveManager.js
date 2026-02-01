const pc = require('picocolors');

let intervalId = null;

function init() {
    startKeepAlive();
}

function startKeepAlive() {
    // Clear existing interval if any (e.g., if re-initialized)
    if (intervalId) clearInterval(intervalId);

    const enabled = process.env.GSM_KEEP_ALIVE === 'true';
    const url = process.env.GSM_BASE_URL;

    if (enabled && url) {
        console.log(pc.cyan('ℹ ') + 'GSMArena Keep-Alive enabled. Pinging every 15s.');

        // Initial ping
        ping(url);

        intervalId = setInterval(() => {
            ping(url);
        }, 15000); // 15 seconds
    } else {
        if (intervalId) {
            console.log(pc.gray('ℹ GSMArena Keep-Alive disabled.'));
            intervalId = null;
        }
    }
}

async function ping(url) {
    try {
        await fetch(url);
        // We don't log success to avoid spamming the console
    } catch (err) {
        console.error(pc.yellow(`[KeepAlive] Ping failed to ${url}: ${err.message}`));
    }
}

// Allow reloading config at runtime
function reload() {
    startKeepAlive();
}

module.exports = { init, reload };
