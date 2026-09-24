"use client";

/**
 * "Yangi ish chiqsa xabar ber" — opens the bot's alerts. Dismissible per
 * placement, since a permanent banner above a list someone visits daily is
 * noise once they have seen it.
 */

import { useEffect, useState } from "react";
import { BellRing, X, ArrowRight } from "lucide-react";
import { jobAlertBotLink } from "@/lib/jobAlerts";

export function JobAlertCta({
  ru = false,
  city,
  storageKey,
}: {
  ru?: boolean;
  city?: string;
  /** When set, the card can be closed and stays closed on this device. */
  storageKey?: string;
}) {
  const [show, setShow] = useState(!storageKey);

  useEffect(() => {
    if (!storageKey) return;
    try {
      setShow(window.localStorage.getItem(storageKey) !== "1");
    } catch {
      setShow(true);
    }
  }, [storageKey]);

  const dismiss = () => {
    try {
      if (storageKey) window.localStorage.setItem(storageKey, "1");
    } catch {
      /* ignore */
    }
    setShow(false);
  };

  if (!show) return null;

  return (
    <div className="relative overflow-hidden rounded-2xl border border-amber-200/70 bg-gradient-to-r from-amber-50 via-orange-50 to-white p-4 dark:border-amber-500/20 dark:from-amber-500/10 dark:via-orange-500/5 dark:to-surface-900 sm:p-5">
      {storageKey && (
        <button
          type="button"
          onClick={dismiss}
          aria-label={ru ? "Закрыть" : "Yopish"}
          className="absolute right-3 top-3 rounded-lg p-1 text-amber-700/70 transition hover:bg-white/60 dark:text-white/50"
        >
          <X className="h-4 w-4" />
        </button>
      )}

      <div className="flex flex-col items-start gap-3 pr-6 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-white text-amber-600 shadow-[0_4px_12px_-4px_rgba(217,119,6,0.45)] dark:bg-amber-500/15 dark:text-amber-300">
            <BellRing className="h-5 w-5" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-surface-900 dark:text-white">
              {ru ? "Новая вакансия — узнайте первым" : "Yangi ish chiqsa — birinchi bo'lib biling"}
            </p>
            <p className="text-xs text-surface-600 dark:text-white/70">
              {ru
                ? "Выберите сферу или город — пришлём подходящую вакансию в Telegram сразу, как она появится. Бесплатно, ночью не беспокоим."
                : "Soha yoki shaharni tanlang — mos vakansiya chiqishi bilan Telegram'da xabar beramiz. Bepul, kechasi bezovta qilmaymiz."}
            </p>
          </div>
        </div>

        <a
          href={jobAlertBotLink({ city })}
          target="_blank"
          rel="noopener noreferrer"
          className="group inline-flex w-full shrink-0 items-center justify-center gap-1.5 rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-600 sm:w-auto"
        >
          {ru ? "Включить уведомления" : "Xabarnomani yoqish"}
          <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" aria-hidden />
        </a>
      </div>
    </div>
  );
}

export default JobAlertCta;
