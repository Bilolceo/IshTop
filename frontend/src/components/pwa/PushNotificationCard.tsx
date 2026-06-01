"use client";

import { Bell, BellOff, Loader2 } from "lucide-react";
import { usePushNotifications } from "@/hooks/usePushNotifications";

export default function PushNotificationCard() {
  const { status, subscribed, busy, subscribe, unsubscribe } = usePushNotifications();

  if (status === "unsupported") {
    return (
      <div className="rounded-xl border border-surface-200 bg-surface-50 p-4 text-sm text-surface-500 dark:border-surface-700 dark:bg-surface-800/40">
        Brauzeringiz push-bildirishnomalarni qo&apos;llab-quvvatlamaydi.
      </div>
    );
  }

  return (
    <div className="flex items-start justify-between gap-3 rounded-xl border border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-800/40">
      <div className="flex items-start gap-3">
        <div className="grid h-9 w-9 flex-shrink-0 place-items-center rounded-lg bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400">
          {subscribed ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
        </div>
        <div>
          <p className="text-sm font-semibold text-surface-900 dark:text-white">
            Push bildirishnomalar
          </p>
          <p className="mt-0.5 text-xs text-surface-500">
            {subscribed
              ? "Yangi ish e'lonlari va ariza yangilanishlari haqida xabar olasiz."
              : "Yangi mos ishlar va ariza javoblari haqida tezda bilib turish."}
          </p>
        </div>
      </div>
      <button
        type="button"
        disabled={busy || status === "denied"}
        onClick={subscribed ? unsubscribe : subscribe}
        className="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-600 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-50"
      >
        {busy && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
        {status === "denied"
          ? "Bloklangan"
          : subscribed
            ? "O'chirish"
            : "Yoqish"}
      </button>
    </div>
  );
}
