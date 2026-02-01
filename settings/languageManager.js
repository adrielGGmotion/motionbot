const fs = require('fs');
const path = require('path');
const config = require('./config');

class LanguageManager {
    constructor() {
        this.languagesPath = path.join(__dirname, '..', 'languages');
        this.customPath = path.join(__dirname, '..', 'custom');
        this.settingsPath = path.join(__dirname, 'language.json');
        this.translations = {};
        this.customStrings = {};
        this.currentLanguage = this.loadSettings().language || config.language || 'en';

        this.loadTranslations();
        this.loadCustomStrings();
    }

    loadSettings() {
        try {
            if (fs.existsSync(this.settingsPath)) {
                return JSON.parse(fs.readFileSync(this.settingsPath, 'utf8'));
            }
        } catch (error) {
            console.error('Error reading language settings:', error);
        }
        return {};
    }

    saveSettings() {
        try {
            fs.writeFileSync(this.settingsPath, JSON.stringify({ language: this.currentLanguage }, null, 4));
        } catch (error) {
            console.error('Error saving language settings:', error);
        }
    }

    loadTranslations() {
        const langFile = path.join(this.languagesPath, `${this.currentLanguage}.json`);
        if (fs.existsSync(langFile)) {
            try {
                this.translations = JSON.parse(fs.readFileSync(langFile, 'utf8'));
            } catch (error) {
                console.error(`Error loading translation file ${langFile}:`, error);
                this.translations = {};
            }
        } else {
            // Fallback to English
            const fallbackFile = path.join(this.languagesPath, 'en.json');
            if (fs.existsSync(fallbackFile)) {
                try {
                    this.translations = JSON.parse(fs.readFileSync(fallbackFile, 'utf8'));
                } catch (error) {
                    console.error(`Error loading fallback translation file:`, error);
                }
            }
        }
    }

    loadCustomStrings() {
        const customFile = path.join(this.customPath, 'strings.json');
        if (fs.existsSync(customFile)) {
            try {
                this.customStrings = JSON.parse(fs.readFileSync(customFile, 'utf8'));
            } catch (error) {
                // If it fails to parse (e.g. invalid JSON), just ignore it
                this.customStrings = {};
            }
        }
    }

    setLanguage(lang) {
        this.currentLanguage = lang;
        this.saveSettings();
        this.loadTranslations();
        return true;
    }

    getLanguage() {
        return this.currentLanguage;
    }

    getAvailableLanguages() {
        try {
            if (!fs.existsSync(this.languagesPath)) return ['en'];
            return fs.readdirSync(this.languagesPath)
                .filter(file => file.endsWith('.json'))
                .map(file => file.replace('.json', ''));
        } catch (error) {
            console.error('Error listing languages:', error);
            return ['en'];
        }
    }

    t(key, placeholders = {}) {
        let text = this.customStrings[key] || this.translations[key] || key;

        if (typeof text !== 'string') return key;

        for (const [placeholder, value] of Object.entries(placeholders)) {
            text = text.replace(new RegExp(`{${placeholder}}`, 'g'), value);
        }

        return text;
    }
}

module.exports = new LanguageManager();
