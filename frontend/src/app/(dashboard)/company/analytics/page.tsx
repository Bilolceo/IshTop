"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Eye,
  Send,
  ClipboardCheck,
  Star,
  Calendar,
  Trophy,
  TrendingUp,
  Users,
  Briefcase,
  RefreshCw,
} from "lucide-react";
import { useTranslation } from "@/hooks/useTranslation";
import { applicationApi, getErrorMessage } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

type Funnel = {
  totals: {
    total_jobs: number;
    active_jobs: number;
    total_applications: number;
    total_views: number;
    avg_match_score: number | null;
  };
  funnel: {
    views: number;
    applications: number;
    reviewing: number;
    shortlisted: number;
    interview: number;
    accepted: number;
    rejected: number;
  };
  conversion_rates: {
    view_to_apply: number;
    apply_to_review: number;
    review_to_interview: number;
    interview_to_hire: number;
  };
  by_status: Array<{ status: string; count: number }>;
  top_jobs: Array<{
    id: string;
    title: string;
    status: string;
    views: number;
    applications: number;
    interview_count: number;
    accepted_count: number;
  }>;
  recent_activity: {
    applications_in_window: number;
    hires_in_window: number;
    window_days: number;
  };
};

const FUNNEL_STAGES: Array<{
  key: keyof Funnel["funnel"];
  icon: typeof Eye;
  color: string;
}> = [
  { key: "views", icon: Eye, color: "from-cyan-500 to-blue-500" },
  { key: "applications", icon: Send, color: "from-blue-500 to-indigo-500" },
  { key: "reviewing", icon: ClipboardCheck, color: "from-indigo-500 to-purple-500" },
  { key: "interview", icon: Calendar, color: "from-purple-500 to-pink-500" },
  { key: "accepted", icon: Trophy, color: "from-emerald-500 to-teal-500" },
];

export default function CompanyAnalyticsPage() {
  const { locale } = useTranslation();
  const isRu = locale === "ru";
  const jobStatusLabel: Record<string, string> = isRu
    ? { active: "Активная", draft: "Черновик", paused: "Приостановлена", closed: "Закрыта" }
    : { active: "Faol", draft: "Qoralama", paused: "To'xtatilgan", closed: "Yopilgan" };
  const [data, setData] = useState<Funnel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [days, setDays] = useState<7 | 30 | 90>(30);

  const load = async (silent = false) => {
    if (silent) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const res = await applicationApi.hiringFunnel({ days });
      const payload = (res.data as { data?: Funnel })?.data ?? (res.data as Funnel);
      setData(payload);
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
  }, [days]);

  const t = {
    title: isRu ? "Аналитика найма" : "Yollash tahlili",
    subtitle: isRu
      ? "Воронка кандидатов, конверсия и эффективность вакансий."
      : "Nomzodlar voronkasi, konversiya va vakansiya samaradorligi.",
    refresh: isRu ? "Обновить" : "Yangilash",
    last7: isRu ? "7 дней" : "7 kun",
    last30: isRu ? "30 дней" : "30 kun",
    last90: isRu ? "90 дней" : "90 kun",
    totalJobs: isRu ? "Всего вакансий" : "Jami vakansiyalar",
    activeJobs: isRu ? "активны" : "faol",
    totalApps: isRu ? "Всего откликов" : "Jami arizalar",
    totalViews: isRu ? "Просмотры" : "Ko'rishlar",
    avgMatch: isRu ? "Средний % совпадения" : "O'rtacha moslik %",
    funnelTitle: isRu ? "Воронка найма" : "Yollash voronkasi",
    funnelSubtitle: isRu
      ? "Каждый этап показывает совокупное число кандидатов, дошедших до него."
      : "Har bir bosqich shu bosqichga yetib kelgan nomzodlar sonini ko'rsatadi.",
    stages: {
      views: isRu ? "Просмотры" : "Ko'rishlar",
      applications: isRu ? "Отклики" : "Arizalar",
      reviewing: isRu ? "На рассмотрении" : "Ko'rib chiqilmoqda",
      shortlisted: isRu ? "Шорт-лист" : "Saralangan",
      interview: isRu ? "Интервью" : "Intervyu",
      accepted: isRu ? "Принято" : "Qabul qilindi",
      rejected: isRu ? "Отклонено" : "Rad etildi",
    } as Record<keyof Funnel["funnel"], string>,
    conversion: isRu ? "Конверсии" : "Konversiyalar",
    viewToApply: isRu ? "Просмотр → отклик" : "Ko'rish → ariza",
    applyToReview: isRu ? "Отклик → рассмотрение" : "Ariza → ko'rib chiqish",
    reviewToInterview: isRu ? "Рассмотрение → интервью" : "Ko'rib chiqish → intervyu",
    interviewToHire: isRu ? "Интервью → найм" : "Intervyu → yollash",
    topJobs: isRu ? "Топ вакансий" : "Eng yaxshi vakansiyalar",
    topJobsSubtitle: isRu ? "Сортировка по числу откликов" : "Arizalar soni bo'yicha saralangan",
    job: isRu ? "Вакансия" : "Vakansiya",
    apps: isRu ? "Отклики" : "Arizalar",
    interviews: isRu ? "Интервью" : "Intervyu",
    hires: isRu ? "Наймы" : "Yollangan",
    activity: isRu ? "Активность за период" : "Davr ichida faollik",
    appsInWindow: isRu ? "Откликов" : "Arizalar",
    hiresInWindow: isRu ? "Наймов" : "Yollanganlar",
    noData: isRu ? "Пока нет данных. Опубликуйте вакансию." : "Ma'lumot yo'q. Vakansiya joylang.",
    error: isRu ? "Ошибка загрузки" : "Yuklashda xato",
  };

  if (error) {
    return (
      <main className="space-y-4">
        <h1 className="font-display text-2xl font-bold text-surface-900 dark:text-white">{t.title}</h1>
        <Card className="border-red-200 bg-red-50 dark:border-red-500/30 dark:bg-red-500/10">
          <CardContent className="p-4 text-sm text-red-800 dark:text-red-100">{t.error}: {error}</CardContent>
        </Card>
        <Button variant="outline" onClick={() => void load()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          {t.refresh}
        </Button>
      </main>
    );
  }

  const maxFunnelValue = data
    ? Math.max(data.funnel.views, data.funnel.applications, 1)
    : 1;

  return (
    <main className="space-y-6">
      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900 sm:p-8">
        <div className="pointer-events-none absolute -right-16 -top-16 h-72 w-72 rounded-full bg-gradient-to-br from-brand-500/15 via-cyan-500/10 to-transparent blur-3xl" aria-hidden />
        <div className="relative flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/10 dark:text-brand-300">
              <TrendingUp className="h-3.5 w-3.5" />
              {t.title}
            </div>
            <h1 className="mt-3 font-display text-3xl font-bold tracking-tight text-surface-900 dark:text-white sm:text-4xl">
              {t.title}
            </h1>
            <p className="mt-2 text-sm text-surface-600 dark:text-surface-400">{t.subtitle}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex rounded-lg border border-surface-200 p-1 dark:border-surface-700">
              {([7, 30, 90] as const).map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
                    days === d
                      ? "bg-brand-600 text-white"
                      : "text-surface-600 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800"
                  }`}
                >
                  {d === 7 ? t.last7 : d === 30 ? t.last30 : t.last90}
                </button>
              ))}
            </div>
            <Button variant="outline" onClick={() => void load(true)} disabled={refreshing}>
              <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
              {t.refresh}
            </Button>
          </div>
        </div>
      </section>

      {/* KPI Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-2xl" />
          ))
        ) : data ? (
          <>
            <KPICard
              icon={Briefcase}
              label={t.totalJobs}
              value={data.totals.total_jobs}
              note={`${data.totals.active_jobs} ${t.activeJobs}`}
              color="from-blue-500 to-cyan-500"
            />
            <KPICard
              icon={Send}
              label={t.totalApps}
              value={data.totals.total_applications}
              note={`${data.recent_activity.applications_in_window} / ${data.recent_activity.window_days}d`}
              color="from-indigo-500 to-purple-500"
            />
            <KPICard
              icon={Eye}
              label={t.totalViews}
              value={data.totals.total_views}
              color="from-emerald-500 to-teal-500"
            />
            <KPICard
              icon={Star}
              label={t.avgMatch}
              value={data.totals.avg_match_score !== null ? `${data.totals.avg_match_score}%` : "—"}
              color="from-amber-500 to-orange-500"
            />
          </>
        ) : null}
      </div>

      {/* Funnel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="h-5 w-5 text-brand-500" />
            {t.funnelTitle}
          </CardTitle>
          <p className="text-sm text-surface-500 dark:text-surface-400">{t.funnelSubtitle}</p>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 rounded-lg" />
              ))}
            </div>
          ) : data ? (
            <div className="space-y-2">
              {FUNNEL_STAGES.map((stage) => {
                const value = data.funnel[stage.key];
                const widthPct = Math.max((value / maxFunnelValue) * 100, 4);
                const Icon = stage.icon;
                return (
                  <div key={stage.key} className="flex items-center gap-3">
                    <div className="flex w-36 flex-shrink-0 items-center gap-2 text-sm font-medium text-surface-700 dark:text-surface-300">
                      <Icon className="h-4 w-4 text-surface-500" />
                      {t.stages[stage.key]}
                    </div>
                    <div className="relative flex-1">
                      <div
                        className={`h-9 rounded-lg bg-gradient-to-r ${stage.color} shadow-sm transition-all`}
                        style={{ width: `${widthPct}%` }}
                      />
                      <div className="absolute inset-y-0 left-3 flex items-center text-sm font-semibold text-white">
                        {value.toLocaleString()}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : null}

          {data && (
            <div className="mt-6 grid gap-3 border-t border-surface-200 pt-4 dark:border-surface-700 sm:grid-cols-2 lg:grid-cols-4">
              <ConversionStat label={t.viewToApply} value={data.conversion_rates.view_to_apply} />
              <ConversionStat label={t.applyToReview} value={data.conversion_rates.apply_to_review} />
              <ConversionStat label={t.reviewToInterview} value={data.conversion_rates.review_to_interview} />
              <ConversionStat label={t.interviewToHire} value={data.conversion_rates.interview_to_hire} tone="emerald" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Top Jobs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Trophy className="h-5 w-5 text-amber-500" />
            {t.topJobs}
          </CardTitle>
          <p className="text-sm text-surface-500 dark:text-surface-400">{t.topJobsSubtitle}</p>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-14 rounded-lg" />
              ))}
            </div>
          ) : data && data.top_jobs.length > 0 ? (
            <div className="overflow-hidden rounded-xl border border-surface-200 dark:border-surface-700">
              <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-3 border-b border-surface-200 bg-surface-50/80 px-4 py-2.5 text-[11px] font-bold uppercase tracking-wider text-surface-500 dark:border-surface-700 dark:bg-surface-900/60 dark:text-surface-400">
                <span>{t.job}</span>
                <span className="text-right">{t.totalViews}</span>
                <span className="text-right">{t.apps}</span>
                <span className="text-right">{t.interviews}</span>
                <span className="text-right">{t.hires}</span>
              </div>
              <div className="divide-y divide-surface-200 dark:divide-surface-700">
                {data.top_jobs.map((job) => (
                  <Link
                    key={job.id}
                    href={`/company/jobs/${job.id}/edit`}
                    className="grid grid-cols-[1fr_auto_auto_auto_auto] items-center gap-3 px-4 py-3 text-sm transition-colors hover:bg-surface-50 dark:hover:bg-surface-900/40"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-medium text-surface-900 dark:text-white">{job.title}</p>
                      <Badge variant={job.status === "active" ? "success" : "secondary"} className="mt-0.5">
                        {jobStatusLabel[job.status] || job.status}
                      </Badge>
                    </div>
                    <span className="text-right text-surface-600 dark:text-surface-300">{job.views}</span>
                    <span className="text-right font-semibold text-surface-900 dark:text-white">
                      {job.applications}
                    </span>
                    <span className="text-right text-purple-600 dark:text-purple-400">
                      {job.interview_count}
                    </span>
                    <span className="text-right font-semibold text-emerald-600 dark:text-emerald-400">
                      {job.accepted_count}
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-surface-200 py-10 text-center dark:border-surface-700">
              <Users className="h-8 w-8 text-surface-400" />
              <p className="text-sm text-surface-500">{t.noData}</p>
              <Link href="/company/jobs/new">
                <Button size="sm">{isRu ? "Создать вакансию" : "Vakansiya yaratish"}</Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </main>
  );
}

function KPICard({
  icon: Icon,
  label,
  value,
  note,
  color,
}: {
  icon: typeof Eye;
  label: string;
  value: number | string;
  note?: string;
  color: string;
}) {
  return (
    <Card className="group relative overflow-hidden transition-all hover:-translate-y-0.5 hover:shadow-lg">
      <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${color}`} />
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-surface-500">{label}</p>
            <p className="mt-2 font-display text-3xl font-bold text-surface-900 dark:text-white">{value}</p>
            {note && <p className="mt-1 text-xs text-surface-500">{note}</p>}
          </div>
          <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${color} text-white`}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ConversionStat({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone?: "emerald";
}) {
  const valueColor =
    tone === "emerald"
      ? "text-emerald-600 dark:text-emerald-400"
      : "text-surface-900 dark:text-white";
  return (
    <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-900/40">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-surface-500">{label}</p>
      <p className={`mt-1 font-display text-2xl font-bold ${valueColor}`}>{value}%</p>
    </div>
  );
}
