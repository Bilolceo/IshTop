"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Sparkles,
  Users,
  RefreshCw,
  Target,
  Check,
  Minus,
  Mail,
  ExternalLink,
  Briefcase,
} from "lucide-react";
import { applicationApi, getErrorMessage } from "@/lib/api";
import { useTranslation } from "@/hooks/useTranslation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { UserAvatar } from "@/components/ui/avatar";

type Candidate = {
  source: "applicant" | "sourced";
  application_id: string | null;
  user_id: string | null;
  full_name: string | null;
  email: string | null;
  avatar_url: string | null;
  status: string | null;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  resume_title: string | null;
};

type Response = {
  job: { id: string; title: string; requirements_count: number };
  candidates: Candidate[];
  pool: "applicants" | "all";
  total_evaluated: number;
};

const STATUS_TONE: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-300",
  reviewing: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300",
  shortlisted: "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300",
  interview: "bg-indigo-100 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300",
  accepted: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300",
  withdrawn: "bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300",
};

export default function JobTopCandidatesPage() {
  const params = useParams();
  const jobId = params!.id as string;
  const { locale } = useTranslation();
  const isRu = locale === "ru";
  const statusLabel: Record<string, string> = isRu
    ? {
        pending: "Ожидание",
        reviewing: "Проверка",
        shortlisted: "Шорт-лист",
        interview: "Интервью",
        accepted: "Принят",
        rejected: "Отклонен",
        withdrawn: "Отозвано",
      }
    : {
        pending: "Kutilmoqda",
        reviewing: "Ko'rib chiqilmoqda",
        shortlisted: "Saralangan",
        interview: "Intervyu",
        accepted: "Qabul qilindi",
        rejected: "Rad etildi",
        withdrawn: "Qaytarib olindi",
      };

  const [data, setData] = useState<Response | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [pool, setPool] = useState<"applicants" | "all">("applicants");
  const [error, setError] = useState<string | null>(null);

  const t = useMemo(
    () => (isRu ? {
      back: "Назад к вакансиям",
      title: "AI Топ Кандидаты",
      subtitle: "Ранжирование по соответствию навыков и опыта.",
      poolApplicants: "Только подавшие",
      poolAll: "Включить базу кандидатов",
      refresh: "Обновить",
      empty: "Подходящих кандидатов не найдено",
      total: (n: number) => `Оценено ${n} кандидатов`,
      matched: "Совпавшие навыки",
      missing: "Не хватает",
      view: "Открыть",
      applicant: "Подал заявку",
      sourced: "Источник: база",
      noStatus: "—",
    } : {
      back: "Vakansiyalarga qaytish",
      title: "AI Top Nomzodlar",
      subtitle: "Ko'nikma va tajriba mosligi bo'yicha ranjirovka.",
      poolApplicants: "Faqat ariza topshirganlar",
      poolAll: "Nomzodlar bazasini ham qo'shish",
      refresh: "Yangilash",
      empty: "Mos nomzodlar topilmadi",
      total: (n: number) => `${n} ta nomzod baholandi`,
      matched: "Mos ko'nikmalar",
      missing: "Yetishmaydi",
      view: "Ochish",
      applicant: "Ariza topshirgan",
      sourced: "Manba: baza",
      noStatus: "—",
    }),
    [isRu]
  );

  const load = async (silent = false) => {
    if (silent) setRefreshing(true); else setLoading(true);
    setError(null);
    try {
      const res = await applicationApi.topCandidatesForJob(jobId, { limit: 20, pool });
      setData((res.data as { data: Response }).data);
    } catch (e) {
      setError(getErrorMessage(e));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pool]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link href="/company/jobs" className="inline-flex items-center gap-1 text-sm text-surface-600 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white">
          <ArrowLeft className="h-4 w-4" />
          {t.back}
        </Link>
      </div>

      <section className="relative overflow-hidden rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900 sm:p-8">
        <div className="pointer-events-none absolute -right-16 -top-16 h-72 w-72 rounded-full bg-gradient-to-br from-purple-500/15 via-pink-500/10 to-transparent blur-3xl" />
        <div className="relative flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-semibold text-purple-700 dark:border-purple-500/30 dark:bg-purple-500/10 dark:text-purple-300">
              <Sparkles className="h-3.5 w-3.5" />
              {t.title}
            </div>
            <h1 className="mt-3 font-display text-3xl font-bold tracking-tight text-surface-900 dark:text-white">
              {data?.job?.title || t.title}
            </h1>
            <p className="mt-2 text-sm text-surface-600 dark:text-surface-400">{t.subtitle}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex rounded-lg border border-surface-200 p-1 dark:border-surface-700">
              <button
                onClick={() => setPool("applicants")}
                className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
                  pool === "applicants"
                    ? "bg-brand-600 text-white"
                    : "text-surface-600 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800"
                }`}
              >
                {t.poolApplicants}
              </button>
              <button
                onClick={() => setPool("all")}
                className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
                  pool === "all"
                    ? "bg-brand-600 text-white"
                    : "text-surface-600 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800"
                }`}
              >
                {t.poolAll}
              </button>
            </div>
            <Button variant="outline" onClick={() => void load(true)} disabled={refreshing}>
              <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
              {t.refresh}
            </Button>
          </div>
        </div>
      </section>

      {error && (
        <Card className="border-red-200 bg-red-50 dark:border-red-500/30 dark:bg-red-500/10">
          <CardContent className="p-3 text-sm text-red-800 dark:text-red-100">{error}</CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Users className="h-5 w-5 text-brand-500" />
            {t.title}
          </CardTitle>
          {data && (
            <span className="text-xs text-surface-500">{t.total(data.total_evaluated)}</span>
          )}
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-24 rounded-xl" />
              ))}
            </div>
          ) : !data || data.candidates.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-surface-200 py-12 text-center dark:border-surface-700">
              <Briefcase className="mx-auto h-8 w-8 text-surface-400" />
              <p className="mt-2 font-medium text-surface-900 dark:text-white">{t.empty}</p>
            </div>
          ) : (
            <ol className="space-y-3">
              {data.candidates.map((c, idx) => {
                const tone =
                  c.score >= 80
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300"
                    : c.score >= 60
                    ? "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300"
                    : "bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300";
                const statusBadge = c.status ? STATUS_TONE[c.status] || STATUS_TONE.pending : null;
                return (
                  <li
                    key={`${c.user_id}-${idx}`}
                    className="grid grid-cols-[auto_1fr_auto] items-start gap-4 rounded-2xl border border-surface-200 p-4 transition-colors hover:border-purple-300 dark:border-surface-700 dark:hover:border-purple-500/40"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-surface-100 text-xs font-bold text-surface-700 dark:bg-surface-700 dark:text-surface-200">
                        {idx + 1}
                      </span>
                      <UserAvatar name={c.full_name || c.email || "?"} imageUrl={c.avatar_url ?? undefined} size="md" />
                    </div>

                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="truncate font-semibold text-surface-900 dark:text-white">
                          {c.full_name || c.email}
                        </p>
                        {c.resume_title && (
                          <span className="text-xs text-surface-500">· {c.resume_title}</span>
                        )}
                        <span className={`rounded-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                          c.source === "applicant"
                            ? "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300"
                            : "bg-violet-100 text-violet-700 dark:bg-violet-500/20 dark:text-violet-300"
                        }`}>
                          {c.source === "applicant" ? t.applicant : t.sourced}
                        </span>
                        {statusBadge && (
                          <span className={`rounded-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${statusBadge}`}>
                            {c.status ? (statusLabel[c.status] || c.status) : t.noStatus}
                          </span>
                        )}
                      </div>
                      {c.email && (
                        <p className="mt-0.5 flex items-center gap-1 text-xs text-surface-500">
                          <Mail className="h-3 w-3" /> {c.email}
                        </p>
                      )}
                      {c.matched_skills.length > 0 && (
                        <div className="mt-2 flex flex-wrap items-center gap-1.5">
                          <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">{t.matched}:</span>
                          {c.matched_skills.slice(0, 6).map((s) => (
                            <span key={s} className="inline-flex items-center gap-1 rounded bg-emerald-50 px-1.5 py-0.5 text-[11px] text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">
                              <Check className="h-2.5 w-2.5" /> {s}
                            </span>
                          ))}
                        </div>
                      )}
                      {c.missing_skills.length > 0 && (
                        <div className="mt-1 flex flex-wrap items-center gap-1.5">
                          <span className="text-[11px] font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">{t.missing}:</span>
                          {c.missing_skills.slice(0, 4).map((s) => (
                            <span key={s} className="inline-flex items-center gap-1 rounded bg-amber-50 px-1.5 py-0.5 text-[11px] text-amber-700 dark:bg-amber-500/10 dark:text-amber-300">
                              <Minus className="h-2.5 w-2.5" /> {s}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col items-end gap-2">
                      <div className={`flex flex-col items-end rounded-lg px-3 py-1.5 ${tone}`}>
                        <span className="text-xl font-bold leading-none">{c.score.toFixed(0)}%</span>
                        <span className="mt-0.5 text-[9px] font-semibold uppercase tracking-wider opacity-80">
                          <Target className="inline h-2.5 w-2.5" /> match
                        </span>
                      </div>
                      {c.application_id && (
                        <Link href={`/company/applicants/${c.application_id}`}>
                          <Button size="sm" variant="outline">
                            <ExternalLink className="mr-1 h-3.5 w-3.5" />
                            {t.view}
                          </Button>
                        </Link>
                      )}
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
