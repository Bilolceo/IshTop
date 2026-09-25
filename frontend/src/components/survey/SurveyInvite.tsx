"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ClipboardList, X } from "lucide-react";

import { surveyApi } from "@/lib/api";
import { STUDENT_SURVEY_KEY } from "@/lib/surveys";
import { useTranslation } from "@/hooks/useTranslation";

const DISMISS_KEY = `survey-dismissed:${STUDENT_SURVEY_KEY}`;

/** Dashboard nudge to take the 2-minute survey; gone once answered or dismissed. */
export function SurveyInvite() {
  const { locale } = useTranslation();
  const t = (uz: string, ru: string) => (locale === "ru" ? ru : uz);
  const [show, setShow] = useState(false);

  useEffect(() => {
    try {
      if (localStorage.getItem(DISMISS_KEY)) return;
    } catch {
      /* storage blocked — still ask */
    }
    let alive = true;
    surveyApi
      .status(STUDENT_SURVEY_KEY)
      .then((r) => alive && setShow(!r.data.data.answered))
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, []);

  if (!show) return null;

  const dismiss = () => {
    setShow(false);
    try {
      localStorage.setItem(DISMISS_KEY, "1");
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="relative flex items-center gap-4 rounded-2xl border border-primary-200 bg-primary-50 p-4 pr-10 dark:border-primary-500/30 dark:bg-primary-500/10">
      <ClipboardList className="h-8 w-8 shrink-0 text-primary-600" />
      <div className="min-w-0 flex-1">
        <p className="font-semibold text-surface-900 dark:text-white">
          {t("2 daqiqalik so'rovnoma", "Опрос на 2 минуты")}
        </p>
        <p className="text-sm text-surface-600 dark:text-surface-300">
          {t(
            "Ish qidirishda nima qiyin? Javobingiz bilan IshTop'ni yaxshilaymiz.",
            "Что сложно в поиске работы? По вашим ответам мы улучшим IshTop.",
          )}
        </p>
      </div>
      <Link
        href="/sorovnoma?src=dashboard"
        className="shrink-0 rounded-xl bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
      >
        {t("Boshlash", "Начать")}
      </Link>
      <button
        type="button"
        onClick={dismiss}
        aria-label={t("Yopish", "Закрыть")}
        className="absolute right-2 top-2 rounded p-1 text-surface-400 hover:text-surface-600"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
