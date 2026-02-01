const fs = require('fs');
const path = require('path');

const themeFilePath = path.join(__dirname, 'theme.json');

function getTheme() {
    try {
        if (!fs.existsSync(themeFilePath)) {
            const defaultTheme = {
                primary: '#0099ff',
                accent: '#7289da',
                error: '#ff0000'
            };
            fs.writeFileSync(themeFilePath, JSON.stringify(defaultTheme, null, 4));
            return defaultTheme;
        }
        const data = fs.readFileSync(themeFilePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error reading theme settings:', error);
        return {
            primary: '#0099ff',
            accent: '#7289da',
            error: '#ff0000'
        };
    }
}

function setTheme(theme) {
    try {
        fs.writeFileSync(themeFilePath, JSON.stringify(theme, null, 4));
        return true;
    } catch (error) {
        console.error('Error saving theme settings:', error);
        return false;
    }
}

module.exports = { getTheme, setTheme };
