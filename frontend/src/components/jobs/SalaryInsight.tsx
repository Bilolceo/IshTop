"use client";

/**
 * "Maosh tahlili" — where this listing's pay sits against what the same kasb
 * (or soha) pays across the live listings.
 *
 * On a listing that hides its pay this is the most useful block on the page:
 * the candidate still learns what the job usually pays, and walks into the
 * call knowing what to ask for.
 */

import Link from "next/link";
import { BarChart3, ArrowRight } from "lucide-react";
import type { SalaryInsight as Insight } from "@/types/api";
import { diffVerdict, groupLabel, mln, mlnRange } from "@/lib/salary";
import { cn } from "@/lib/utils";

export function SalaryInsight({ insight, isRu }: { insight: Insight; isRu: boolean }) {
  const label = groupLabel(insight, isRu);
  const verdict = diffVerdict(insight.diff_pct, isRu, insight.job_is_floor);

  // Scale the bar to the group's full spread, widened to fit this listing.
  const lo = Math.min(insight.min, insight.job_value ?? insight.min);
  const hi = Math.max(insight.max, insight.job_value ?? insight.max);
  const span = Math.max(hi - lo, 1);
  const pos = (v: number) => `${Math.min(100, Math.max(0, ((v - lo) / span) * 100))}%`;

  const basis =
    insight.kind === "role"
      ? isRu
        ? `по профессии «${label}»`
        : `«${label}» kasbi bo'yicha`
      : isRu
        ? `в сфере «${label}»`
        : `«${label}» sohasida`;

  return (
    <div className="rounded-2xl border border-surface-200 bg-white p-5 dark:border-surface-700 dark:bg-surface-900">
      <h2 className="flex items-center gap-2 text-sm font-bold text-surface-900 dark:text-white">
        <BarChart3 className="h-4 w-4 text-emerald-500" />
        {isRu ? "Анализ зарплаты" : "Maosh tahlili"}
      </h2>

      <p className="mt-3 text-sm text-surface-600 dark:text-surface-300">
        {isRu ? "Обычно платят " : "Odatda to'lanadi "}
        {basis}:
      </p>
      <p className="mt-1 text-2xl font-bold text-surface-900 dark:text-white">
        {mln(insight.median, isRu)} <span className="text-base font-semibold text-surface-500">{isRu ? "сум" : "so'm"}</span>
      </p>
      <p className="text-xs text-surface-500">
        {isRu ? "большинство: " : "ko'pchiligi: "}
        {mlnRange(insight.p25, insight.p75, isRu)}
      </p>

      {/* The middle half of the market as a band, the median as a tick and
          this listing as a dot. */}
      <div className="relative mt-5 h-2 rounded-full bg-surface-100 dark:bg-surface-800" aria-hidden>
        <div
          className="absolute inset-y-0 rounded-full bg-emerald-200 dark:bg-emerald-500/30"
          style={{ left: pos(insight.p25), width: `calc(${pos(insight.p75)} - ${pos(insight.p25)})` }}
        />
        <div
          className="absolute -top-1 h-4 w-0.5 rounded bg-emerald-600 dark:bg-emerald-400"
          style={{ left: pos(insight.median) }}
        />
        {insight.job_value !== null && (
          <div
            className={cn(
              "absolute -top-1.5 h-5 w-5 -translate-x-1/2 rounded-full border-2 border-white shadow dark:border-surface-900",
              verdict?.tone === "up" ? "bg-emerald-500" : verdict?.tone === "down" ? "bg-amber-500" : "bg-brand-500",
            )}
            style={{ left: pos(insight.job_value) }}
          />
        )}
      </div>
      <div className="mt-2 flex justify-between text-[11px] text-surface-400">
        <span>{mln(lo, isRu)}</span>
        <span>{mln(hi, isRu)}</span>
      </div>

      {insight.job_value !== null && !verdict ? (
        /* A pay figure but no verdict: compared against a whole soha (which
           mixes kasbs), or a floor that does not clear the median. */
        <p className="mt-3 rounded-xl bg-surface-50 px-3 py-2 text-sm text-surface-700 dark:bg-surface-800 dark:text-surface-200">
          {isRu ? "Эта вакансия: " : "Bu vakansiya: "}
          {insight.job_is_floor ? (isRu ? "от " : "") : ""}
          {mln(insight.job_value, isRu)}
          {insight.job_is_floor && !isRu ? " dan" : ""}
          {insight.kind === "category" &&
            (isRu
              ? " — в сфере разные профессии, поэтому точного сравнения нет."
              : " — sohada turli kasblar bor, shuning uchun aniq solishtirmaymiz.")}
        </p>
      ) : insight.job_value !== null && verdict ? (
        <p
          className={cn(
            "mt-3 rounded-xl px-3 py-2 text-sm font-medium",
            verdict.tone === "up" && "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300",
            verdict.tone === "down" && "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300",
            verdict.tone === "flat" && "bg-surface-50 text-surface-700 dark:bg-surface-800 dark:text-surface-200",
          )}
        >
          {isRu ? "Эта вакансия: " : "Bu vakansiya: "}
          {insight.job_is_floor ? (isRu ? "от " : "") : ""}
          {mln(insight.job_value, isRu)}
          {insight.job_is_floor && !isRu ? " dan" : ""} — {verdict.text}
        </p>
      ) : (
        <p className="mt-3 rounded-xl bg-surface-50 px-3 py-2 text-sm text-surface-700 dark:bg-surface-800 dark:text-surface-200">
          {isRu
            ? `Работодатель не указал зарплату. Ориентируйтесь на ${mlnRange(insight.p25, insight.p75, true)} сум и уточните при звонке.`
            : `Ish beruvchi maoshni ko'rsatmagan. ${mlnRange(insight.p25, insight.p75)} so'm atrofini mo'ljal qiling va qo'ng'iroqda aniqlashtiring.`}
        </p>
      )}

      <p className="mt-3 text-[11px] leading-relaxed text-surface-400">
        {isRu
          ? `По ${insight.count} активным вакансиям на IshTop с указанной зарплатой.`
          : `IshTop'dagi maosh ko'rsatilgan ${insight.count} ta faol vakansiya asosida.`}
      </p>
      <Link
        href="/maosh"
        className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
      >
        {isRu ? "Все зарплаты по профессиям" : "Barcha kasblar bo'yicha maoshlar"}
        <ArrowRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}

export default SalaryInsight;
