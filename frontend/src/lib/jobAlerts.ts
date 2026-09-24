/**
 * Links into the bot's "yangi ish chiqsa xabar ber" alerts.
 *
 * Alerts live in Telegram, keyed by the chat, so nobody has to sign up or link
 * an account to get one. The site only has to open the bot on the right
 * screen: the one-tap soha/shahar picker, or straight to a subscription when
 * the page already knows the city.
 */

import { APPLY_BOT } from "@/lib/jobApply";

// Must match the city ids in backend app/core/job_categories.py (CITIES).
// The bot re-validates, and an unknown id just opens the picker.
const BOT_CITY_IDS = new Set([
  "remote", "toshkent", "samarqand", "fargona", "qoqon", "namangan", "andijon",
  "buxoro", "navoiy", "qarshi", "termiz", "urganch", "jizzax", "guliston", "nukus",
]);

export function jobAlertBotLink(opts: { city?: string } = {}): string {
  const city = (opts.city || "").trim().toLowerCase();
  const start = BOT_CITY_IDS.has(city) ? `alert_t_${city}` : "alerts";
  return `https://t.me/${APPLY_BOT}?start=${start}`;
}
