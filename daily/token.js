// Telegram bot token: process env first, then the user's saved env var in the registry
// (Task Scheduler processes can miss a variable set after the scheduler service started).
const { execFileSync } = require('child_process');

module.exports = function telegramToken() {
  if (process.env.TELEGRAM_BOT_TOKEN) return process.env.TELEGRAM_BOT_TOKEN.trim();
  try {
    const out = execFileSync('reg', ['query', 'HKCU\\Environment', '/v', 'TELEGRAM_BOT_TOKEN'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
    const m = out.match(/TELEGRAM_BOT_TOKEN\s+REG_\w+\s+(\S+)/);
    return m ? m[1] : '';
  } catch (_) {
    return '';
  }
};
