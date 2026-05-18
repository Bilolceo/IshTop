"use client";

import { motion } from "framer-motion";
import {
  MapPin,
  DollarSign,
  Clock,
  Bookmark,
  BookmarkCheck,
  Zap,
  Target,
} from "lucide-react";
import { useTranslation } from "@/hooks/useTranslation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatRelativeTime, formatSalaryRange, cn } from "@/lib/utils";
import type { Job } from "@/types/api";

export function JobCard({
  job,
  isSelected,
  isSaved,
  onSelect,
  onToggleSave,
  onQuickApply,
}: {
  job: Job & { matchScore?: number };
  isSelected: boolean;
  isSaved: boolean;
  onSelect: () => void;
  onToggleSave: () => void;
  onQuickApply: () => void;
}) {
  const { locale } = useTranslation();
  const isRu = locale === "ru";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      onClick={onSelect}
      className={cn(
        "relative cursor-pointer rounded-2xl border p-4 transition-all",
        "hover:-translate-y-0.5 hover:bg-surface-50 dark:hover:bg-surface-800/90",
        isSelected
          ? "border-purple-400 bg-purple-50/70 shadow-lg ring-1 ring-purple-300 dark:bg-purple-900/20 dark:ring-purple-500/40"
          : "border-surface-200 bg-white hover:border-surface-300 hover:shadow-md dark:border-surface-700 dark:bg-surface-900 dark:hover:border-surface-600",
      )}
    >
      {/* Bookmark — top right absolute */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onToggleSave();
        }}
        title={
          isSaved
            ? isRu
              ? "Снять из сохранённых"
              : "Saqlanganlardan olib tashlash"
            : isRu
              ? "Сохранить вакансию"
              : "Ishni saqlash"
        }
        aria-label={
          isSaved
            ? isRu
              ? "Снять из сохранённых"
              : "Saqlanganlardan olib tashlash"
            : isRu
              ? "Сохранить вакансию"
              : "Ishni saqlash"
        }
        className={cn(
          "absolute right-3 top-3 rounded-lg p-1.5 transition-colors",
          isSaved
            ? "bg-purple-100 text-purple-600"
            : "text-surface-400 hover:bg-surface-100 hover:text-surface-600",
        )}
      >
        {isSaved ? (
          <BookmarkCheck className="h-4 w-4" />
        ) : (
          <Bookmark className="h-4 w-4" />
        )}
      </button>

      {/* Header row: logo + title + company */}
      <div className="flex gap-3 pr-8">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-purple-100 to-indigo-100 text-base font-bold text-purple-700 dark:from-purple-900/50 dark:to-indigo-900/50 dark:text-purple-300">
          {job.company?.name?.charAt(0) || "C"}
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-[17px] font-semibold leading-tight text-surface-900 dark:text-white">
            {job.title}
          </h3>
          <p className="mt-0.5 text-sm text-surface-500 dark:text-surface-400">
            {job.company?.name}
          </p>
        </div>
      </div>

      {/* Meta row: location, salary, time, match */}
      <div className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-surface-500">
        <span className="flex items-center gap-1">
          <MapPin className="h-3 w-3" />
          {job.location}
        </span>
        <span className="flex items-center gap-1">
          <DollarSign className="h-3 w-3" />
          {formatSalaryRange(job.salary_min, job.salary_max) ||
            (isRu ? "Зарплата не указана" : "Maosh ko'rsatilmagan")}
        </span>
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {formatRelativeTime(job.created_at, isRu ? "ru" : "uz")}
        </span>
        {job.matchScore ? (
          <Badge
            variant={
              job.matchScore >= 80
                ? "success"
                : job.matchScore >= 60
                  ? "warning"
                  : "secondary"
            }
            className="gap-1 ml-auto"
          >
            <Target className="h-3 w-3" />
            {job.matchScore}% {isRu ? "mos" : "mos"}
          </Badge>
        ) : null}
      </div>

      {/* Skills */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {job.requirements.skills?.slice(0, 4).map((skill) => (
          <Badge key={skill} variant="secondary" className="rounded-full text-xs">
            {skill}
          </Badge>
        ))}
        {(job.requirements.skills?.length || 0) > 4 && (
          <Badge variant="secondary" className="rounded-full text-xs">
            +{(job.requirements.skills?.length || 0) - 4}
          </Badge>
        )}
      </div>

      {/* CTA row */}
      <div className="mt-4 flex justify-end">
        <Button
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onQuickApply();
          }}
          className="rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 px-4 text-xs shadow-sm shadow-purple-500/30"
        >
          <Zap className="mr-1 h-3 w-3" />
          {isRu ? "Быстрый отклик" : "Tezkor ariza"}
        </Button>
      </div>
    </motion.div>
  );
}
