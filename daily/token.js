// Secrets from the user's environment: process env first, then the user's saved env var in the
// registry (Task Scheduler processes can miss a variable set after the scheduler service started).
const { execFileSync } = require('child_process');

function userEnv(name) {
  if (process.env[name]) return process.env[name].trim();
  try {
    const out = execFileSync('reg', ['query', 'HKCU\\Environment', '/v', name], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
    const m = out.match(new RegExp(`${name}\\s+REG_\\w+\\s+(\\S+)`));
    return m ? m[1] : '';
  } catch (_) {
    return '';
  }
}

module.exports = function telegramToken() { return userEnv('TELEGRAM_BOT_TOKEN'); };
module.exports.userEnv = userEnv;
