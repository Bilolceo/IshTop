"use client";

import { useCallback, useEffect, useState } from "react";
import { Copy, RefreshCw } from "lucide-react";

import {
  getErrorMessage,
  surveyApi,
  type SurveySummary,
  type TractionMetrics,
} from "@/lib/api";
import { STUDENT_SURVEY, STUDENT_SURVEY_KEY } from "@/lib/surveys";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTranslation } from "@/hooks/useTranslation";

const STEP_LABEL: Record<string, { uz: string; ru: string }> = {
  signed_up: { uz: "Ro'yxatdan o'tdi", ru: "Зарегистрировались" },
  resume: { uz: "Rezyume yaratdi", ru: "Создали резюме" },
  applied: { uz: "Ariza topshirdi", ru: "Откликнулись" },
  employer_responded: { uz: "Ish beruvchi javob berdi", ru: "Работодатель ответил" },
  hired: { uz: "Ishga olindi", ru: "Наняты" },
};

function Stat({ label, value, sub }: { label: string; value: number | string; sub?: string }) {
  return (
    <div className="rounded-xl border border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
      <p className="text-xs text-surface-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-surface-900 dark:text-white">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-surface-500">{sub}</p>}
    </div>
  );
}

function Bars({ data }: { data: { week: string; value: number }[] }) {
  const top = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="flex h-32 items-end gap-1">
      {data.map((d) => (
        <div key={d.week} className="group flex flex-1 flex-col items-center justify-end" title={`${d.week}: ${d.value}`}>
          <span className="mb-1 text-[10px] text-surface-500">{d.value || ""}</span>
          <div
            className="w-full rounded-t bg-primary-500/80"
            style={{ height: `${(d.value / top) * 100}%`, minHeight: d.value ? 2 : 0 }}
          />
          <span className="mt-1 text-[9px] text-surface-400">{d.week.slice(5)}</span>
        </div>
      ))}
    </div>
  );
}

export default function AdminMetricsPage() {
  const { locale } = useTranslation();
  const lang = locale === "ru" ? "ru" : "uz";
  const t = (uz: string, ru: string) => (lang === "ru" ? ru : uz);

  const [m, setM] = useState<TractionMetrics | null>(null);
  const [s, setS] = useState<SurveySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [tr, sv] = await Promise.all([
        surveyApi.traction(12),
        surveyApi.summary(STUDENT_SURVEY_KEY),
      ]);
      setM(tr.data.data);
      setS(sv.data.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const surveyUrl =
    typeof window !== "undefined" ? `${window.location.origin}/sorovnoma` : "/sorovnoma";

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(`${surveyUrl}?src=telegram`);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard blocked — the link is visible to copy by hand */
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
            {t("Traction va so'rovnoma", "Traction и опрос")}
          </h1>
          <p className="text-sm text-surface-500">
            {t(
              "Test, demo va xodim akkauntlari hisobga olinmaydi — bu raqamlarni tashqariga aytish mumkin.",
              "Тестовые, демо и служебные аккаунты исключены — эти цифры можно показывать наружу.",
            )}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void load()} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          {t("Yangilash", "Обновить")}
        </Button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading && !m ? (
        <div className="grid gap-3 sm:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      ) : m ? (
        <>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Stat label={t("Talabalar", "Студенты")} value={m.students.total} />
            <Stat label={t("Faol (7 kun)", "Активны (7 дн.)")} value={m.students.active_7d} sub={`30 ${t("kun", "дн.")}: ${m.students.active_30d}`} />
            <Stat label={t("Arizalar", "Отклики")} value={m.applications.total} />
            <Stat label={t("Ish beruvchilar", "Работодатели")} value={m.employers.companies} />
            <Stat
              label={t("Faol vakansiyalar", "Активные вакансии")}
              value={m.employers.live_jobs}
              sub={`${t("kompaniyalardan", "от компаний")}: ${m.employers.live_jobs_posted_by_companies}`}
            />
            <Stat label={t("Telegram bog'langan", "Привязан Telegram")} value={m.students.telegram_linked} />
            <Stat
              label={t("Ish alertlari", "Подписки на вакансии")}
              value={m.engagement.job_alerts_active}
              sub={`${m.engagement.job_alert_chats} ${t("chat", "чатов")}`}
            />
            <Stat label={t("So'rovnoma javoblari", "Ответы на опрос")} value={m.engagement.survey_responses} />
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t("Voronka", "Воронка")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {m.funnel.map((f) => (
                <div key={f.step} className="grid grid-cols-[10rem_1fr_5rem] items-center gap-3 text-sm">
                  <span className="text-surface-600 dark:text-surface-300">{STEP_LABEL[f.step]?.[lang] ?? f.step}</span>
                  <div className="h-3 rounded-full bg-surface-100 dark:bg-surface-800">
                    <div className="h-3 rounded-full bg-primary-500" style={{ width: `${Math.min(100, f.pct)}%` }} />
                  </div>
                  <span className="text-right font-medium">
                    {f.value} <span className="text-xs text-surface-500">({f.pct}%)</span>
                  </span>
                </div>
              ))}
              <p className="pt-2 text-xs text-surface-500">
                {t(
                  "Oxirgi ikki qator — arizalarga nisbatan foiz; qolganlari — talabalarga nisbatan.",
                  "Последние две строки — процент от откликов; остальные — от студентов.",
                )}
              </p>
            </CardContent>
          </Card>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t("Haftalik ro'yxatdan o'tish", "Регистрации по неделям")}</CardTitle>
              </CardHeader>
              <CardContent>
                <Bars data={m.weekly.signups} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t("Haftalik arizalar", "Отклики по неделям")}</CardTitle>
              </CardHeader>
              <CardContent>
                <Bars data={m.weekly.applications} />
              </CardContent>
            </Card>
          </div>
        </>
      ) : null}

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
          <CardTitle className="text-base">
            {t("Talabalar so'rovnomasi", "Опрос студентов")}
            {s && <span className="ml-2 text-sm font-normal text-surface-500">{s.total} {t("javob", "ответов")}</span>}
          </CardTitle>
          <div className="flex items-center gap-2 text-sm">
            <code className="rounded bg-surface-100 px-2 py-1 text-xs dark:bg-surface-800">{surveyUrl}?src=…</code>
            <Button variant="outline" size="sm" onClick={copyLink}>
              <Copy className="mr-1 h-3.5 w-3.5" />
              {copied ? t("Nusxalandi", "Скопировано") : t("Havola", "Ссылка")}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {s && s.total > 0 && (
            <p className="text-xs text-surface-500">
              {t("Tizimga kirganlar", "Вошедших")}: {s.signed_in} · {t("Turli IP", "Разных IP")}: {s.distinct_ips} ·{" "}
              {t("Manbalar", "Источники")}:{" "}
              {Object.entries(s.sources)
                .map(([k, v]) => `${k} ${v}`)
                .join(", ")}
            </p>
          )}
          {s?.total === 0 && (
            <p className="text-sm text-surface-500">
              {t(
                "Hali javob yo'q. Havolani universitet chatlariga ?src=<chat-nomi> bilan tarqating — qaysi chat ko'proq javob berganini ko'rasiz.",
                "Ответов пока нет. Распространите ссылку в университетских чатах с ?src=<название-чата> — увидите, какой чат ответил больше.",
              )}
            </p>
          )}
          {s &&
            s.total > 0 &&
            s.questions.map((q) => {
              const def = STUDENT_SURVEY.find((d) => d.id === q.id);
              if (!def) return null;
              return (
                <div key={q.id}>
                  <p className="text-sm font-semibold text-surface-900 dark:text-white">
                    {def.title[lang]} <span className="font-normal text-surface-500">({q.answered})</span>
                  </p>
                  {q.kind === "text" ? (
                    <ul className="mt-2 max-h-64 space-y-1 overflow-auto text-sm text-surface-700 dark:text-surface-300">
                      {(q.texts ?? []).map((txt, i) => (
                        <li key={i} className="rounded bg-surface-50 px-3 py-1.5 dark:bg-surface-800">
                          {txt}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="mt-2 space-y-1">
                      {[...(q.options ?? [])]
                        .sort((a, b) => b.count - a.count)
                        .map((o) => (
                          <div key={o.id} className="grid grid-cols-[minmax(0,14rem)_1fr_5rem] items-center gap-3 text-sm">
                            <span className="truncate text-surface-600 dark:text-surface-300">
                              {def.options?.find((d) => d.id === o.id)?.label[lang] ?? o.id}
                            </span>
                            <div className="h-2.5 rounded-full bg-surface-100 dark:bg-surface-800">
                              <div className="h-2.5 rounded-full bg-emerald-500" style={{ width: `${o.pct}%` }} />
                            </div>
                            <span className="text-right">
                              {o.count} <span className="text-xs text-surface-500">({o.pct}%)</span>
                            </span>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              );
            })}
        </CardContent>
      </Card>
    </div>
  );
}
