const express = require('express');
const path = require('path');
const pc = require('picocolors');

/**
 * Starts the minimalist dashboard server
 * @param {import('discord.js').Client} client 
 * @param {object} stats 
 */
function startDashboard(client, stats) {
    const app = express();
    const port = process.env.PORT || 3000;
    const themeManager = require('../settings/themeManager');
    const languageManager = require('../settings/languageManager');
    const config = require('../settings/config');

    app.use(express.json());
    app.use(express.static(path.join(__dirname)));

    const host = config.lanAccess ? '0.0.0.0' : 'localhost';

    app.get('/api/stats', (req, res) => {
        res.json({
            uptime: process.uptime(),
            commandsRan: stats.commandsRan,
            botName: client.user?.username || 'motionbot',
            botTag: client.user?.tag || 'motionbot#0000',
            status: client.isReady() ? 'Online' : 'Initializing',
            guilds: client.guilds.cache.size,
        });
    });

    let avatarCache = { buffer: null, timestamp: 0 };
    const CACHE_DURATION = 60 * 60 * 1000; // 1 hour

    app.get('/api/avatar', async (req, res) => {
        if (!client.user) return res.status(404).send('Not Found');
        const avatarUrl = client.user.displayAvatarURL({ extension: 'png', size: 128 });
        try {
            const response = await fetch(avatarUrl);
            const buffer = await response.arrayBuffer();
            res.set('Content-Type', 'image/png');
            res.send(Buffer.from(buffer));
        } catch (err) {
            console.error("Failed to proxy avatar", err);
            res.status(500).send('Error');
        }
    });

    app.get('/api/developer', async (req, res) => {
        const now = Date.now();
        if (avatarCache.buffer && (now - avatarCache.timestamp < CACHE_DURATION)) {
            res.set('Content-Type', 'image/png');
            return res.send(avatarCache.buffer);
        }

        try {
            const response = await fetch('https://github.com/adrielGGmotion.png');
            if (!response.ok) throw new Error('Failed to fetch from GitHub');
            const buffer = await response.arrayBuffer();

            avatarCache = { buffer: Buffer.from(buffer), timestamp: now };

            res.set('Content-Type', 'image/png');
            res.send(avatarCache.buffer);
        } catch (err) {
            console.error("Failed to fetch developer avatar", err);
            res.status(500).send('Error');
        }
    });

    app.get('/api/theme', (req, res) => {
        res.json(themeManager.getTheme());
    });

    app.post('/api/theme', (req, res) => {
        const { primary, accent, error } = req.body;
        if (themeManager.setTheme({ primary, accent, error })) {
            res.json({ success: true });
        } else {
            res.status(500).json({ success: false });
        }
    });

    app.get('/api/commands', (req, res) => {
        const commandManager = require('../settings/commandManager');
        const fs = require('fs');
        const path = require('path');
        const commandsPath = path.join(__dirname, '..', 'slashcommands');
        const commands = [];

        function scanCommands(dir) {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const filePath = path.join(dir, file);
                const stat = fs.statSync(filePath);
                if (stat.isDirectory()) {
                    scanCommands(filePath);
                } else if (file.endsWith('.js')) {
                    const cmd = require(filePath);
                    if ('data' in cmd) {
                        const category = path.basename(dir);
                        commands.push({
                            name: cmd.data.name,
                            description: cmd.data.description,
                            category: category === 'slashcommands' ? 'General' : category,
                            enabled: commandManager.isCommandEnabled(cmd.data.name)
                        });
                    }
                }
            }
        }

        scanCommands(commandsPath);
        res.json(commands);
    });

    app.post('/api/commands/toggle', async (req, res) => {
        const { name, enabled } = req.body;
        const commandManager = require('../settings/commandManager');
        const { loadCommands, deployCommands } = require('../handler');

        commandManager.setCommandStatus(name, enabled);

        // Refresh live commands
        loadCommands(client);

        // Deploy to Discord immediately
        const success = await deployCommands(client);

        res.json({ success });
    });

    app.get('/api/language', (req, res) => {
        res.json({
            current: languageManager.getLanguage(),
            available: languageManager.getAvailableLanguages()
        });
    });

    app.post('/api/language', (req, res) => {
        const { language } = req.body;
        if (languageManager.setLanguage(language)) {
            res.json({ success: true });
        } else {
            res.status(500).json({ success: false });
        }
    });

    app.get('/api/config/gsm', (req, res) => {
        const fs = require('fs');
        const envPath = path.join(__dirname, '..', '.env');
        let url = process.env.GSM_BASE_URL;
        let keepAlive = process.env.GSM_KEEP_ALIVE === 'true';

        // Try reading directly from file if not in process (though dotenv should have loaded it)
        if (fs.existsSync(envPath)) {
            const envContent = fs.readFileSync(envPath, 'utf8');

            if (!url) {
                const urlMatch = envContent.match(/^GSM_BASE_URL=(.*)$/m);
                if (urlMatch) url = urlMatch[1].trim();
            }

            // Always check file for boolean to be sure
            const keepAliveMatch = envContent.match(/^GSM_KEEP_ALIVE=(.*)$/m);
            if (keepAliveMatch) keepAlive = keepAliveMatch[1].trim() === 'true';
        }
        res.json({ url, keepAlive });
    });

    app.post('/api/config/env', (req, res) => {
        const fs = require('fs');
        const envPath = path.join(__dirname, '..', '.env');
        const updates = req.body; // Expects { KEY: VALUE }

        try {
            let envContent = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf8') : '';
            const lines = envContent.split('\n');
            const newLines = [];
            const keysUpdated = new Set();

            lines.forEach(line => {
                const match = line.match(/^([^=]+)=(.*)$/);
                if (match) {
                    const key = match[1];
                    if (updates.hasOwnProperty(key)) {
                        newLines.push(`${key}=${updates[key]}`);
                        keysUpdated.add(key);
                        // Update process.env runtime as well
                        process.env[key] = updates[key];
                    } else {
                        newLines.push(line);
                    }
                } else {
                    newLines.push(line);
                }
            });

            // Append new keys
            for (const [key, value] of Object.entries(updates)) {
                if (!keysUpdated.has(key)) {
                    newLines.push(`${key}=${value}`);
                    process.env[key] = value;
                }
            }

            fs.writeFileSync(envPath, newLines.join('\n'));

            // Reload Keep Alive Manager
            const keepAliveManager = require('../settings/keepAliveManager');
            keepAliveManager.reload();

            res.json({ success: true });
        } catch (err) {
            console.error("Failed to update .env", err);
            res.status(500).json({ success: false });
        }
    });

    app.listen(port, host, () => {
        let url = `http://localhost:${port}`;
        if (host === '0.0.0.0') {
            const nets = require('os').networkInterfaces();
            for (const name of Object.keys(nets)) {
                for (const net of nets[name]) {
                    if (net.family === 'IPv4' && !net.internal) {
                        url = `http://${net.address}:${port}`;
                        break;
                    }
                }
                if (url !== `http://localhost:${port}`) break;
            }
        }
        console.log(pc.blue('➜ ') + `Dashboard running at ${pc.cyan(url)}` + (host === '0.0.0.0' ? pc.dim(' (Network Access Enabled)') : ''));
    });
}

module.exports = { startDashboard };
