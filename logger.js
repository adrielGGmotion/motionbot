const fs = require('fs');
const path = require('path');

/**
 * Logs an error to a file formatted by date and hour.
 * @param {Error} error The error object.
 * @param {string} commandName The name of the command that failed.
 * @returns {string} The path to the log file.
 */
function logError(error, commandName) {
    const now = new Date();
    const dateDir = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    const hourFile = `${String(now.getHours()).padStart(2, '0')}-00.log`;

    const logsDir = path.join(__dirname, 'logs', dateDir);
    const logFilePath = path.join(logsDir, hourFile);

    // Create directories if they don't exist
    if (!fs.existsSync(logsDir)) {
        fs.mkdirSync(logsDir, { recursive: true });
    }

    const timestamp = now.toISOString();
    const logEntry = `
[${timestamp}] COMMAND: ${commandName}
MESSAGE: ${error.message}
STACK: ${error.stack}
--------------------------------------------------------------------------------
`;

    fs.appendFileSync(logFilePath, logEntry, 'utf8');

    // Return the relative path for the user
    return path.join('logs', dateDir, hourFile);
}

module.exports = {
    logError
};
