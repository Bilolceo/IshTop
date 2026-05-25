/**
 * =============================================================================
 * STUDENT DASHBOARD - Overview Page
 * =============================================================================
 *
 * Features:
 * - Stats cards (Resumes, Applications, Interviews, Views)
 * - Recent activity feed
 * - Quick actions buttons
 * - Job recommendations
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  FileText,
  Send,
  Calendar,
  Eye,
  Sparkles,
  Briefcase,
  ArrowRight,
  ChevronRight,
  CheckCircle,
  AlertCircle,
  Target,
  Zap,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useTranslation } from "@/hooks/useTranslation";
import { useResume } from "@/hooks/useResume";
import { useApplications } from "@/hooks/useApplications";
import { useJobs } from "@/hooks/useJobs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { formatRelativeTime, formatSalaryRange } from "@/lib/utils";
import { jobApi, userApi } from "@/lib/api";
import type { Job } from "@/types/api";

// =============================================================================
// ANIMATION VARIANTS
// =============================================================================

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

type UpcomingInterviewCandidate = {
  id: string;
  status: string;
  interview_at?: string;
  interview_type?: string;
  meeting_link?: string;
  job?: {
    title?: string;
    company_name?: string;
    company?: { name?: string };
  };
};

type DashboardApplication = {
  id: string;
  status: string;
  applied_at?: string;
  interview_at?: string;
  interview_type?: string;
  meeting_link?: string;
  job?: {
    title?: string;
    company_name?: string;
    company?: { name?: string };
  };
};

function formatInterviewDateTime(dateValue: string, locale: "uz" | "ru") {
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) {
    return dateValue;
  }

  return new Intl.DateTimeFormat(locale === "ru" ? "ru-RU" : "uz-UZ", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatInterviewTypeLabel(interviewType: string | undefined, t: (key: string) => string) {
  if (!interviewType) {
    return t("dashboard.interview.formatNotSet");
  }

  const normalized = interviewType.trim().toLowerCase();
  if (normalized === "video") return t("dashboard.interview.videoInterview");
  if (normalized === "phone") return t("dashboard.interview.phoneInterview");
  if (normalized === "in-person" || normalized === "in person") return t("dashboard.interview.inPersonInterview");

  return interviewType;
}

function getUpcomingInterview(applications: UpcomingInterviewCandidate[]) {
  const now = Date.now();

  return applications
    .filter((app) => app.status === "interview" && app.interview_at)
    .map((app) => ({
      ...app,
      interviewTimestamp: new Date(app.interview_at as string).getTime(),
    }))
    .filter((app) => !Number.isNaN(app.interviewTimestamp) && app.interviewTimestamp >= now)
    .sort((a, b) => a.interviewTimestamp - b.interviewTimestamp)[0] || null;
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function StudentDashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { t, locale } = useTranslation();

  const { resumes, isLoading: resumesLoading, fetchResumes } = useResume();
  const { stats: appStats, applications, isLoading: appsLoading, fetchMyApplications } = useApplications();
  const { jobs, isLoading: jobsLoading, fetchJobs } = useJobs();
  const [summaryCounts, setSummaryCounts] = useState<{ resumes: number; applications: number } | null>(null);

  type Recommendation = {
    job: Job;
    match_score: number;
    skill_matches: string[];
    missing_skills: string[];
  };
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [recsLoading, setRecsLoading] = useState(true);
  const [needsResume, setNeedsResume] = useState(false);

  useEffect(() => {
    fetchResumes();
    fetchMyApplications();
    fetchJobs({}, 1);
  }, [fetchJobs, fetchMyApplications, fetchResumes]);

  useEffect(() => {
    let ignore = false;
    setRecsLoading(true);
    jobApi
      .recommended({ limit: 3 })
      .then((res) => {
        if (ignore) return;
        const payload = (res.data ?? {}) as {
          matches?: Recommendation[];
          message?: string;
        };
        const matches = Array.isArray(payload.matches) ? payload.matches : [];
        setRecommendations(matches);
        setNeedsResume(matches.length === 0 && /resume/i.test(payload.message ?? ""));
      })
      .catch(() => {
        if (!ignore) setRecommendations([]);
      })
      .finally(() => {
        if (!ignore) setRecsLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [user?.id]);

  useEffect(() => {
    const loadSummaryCounts = async () => {
      try {
        const response = await userApi.getProfile();
        const payload = response.data?.data ?? response.data ?? {};
        const resumesCount = typeof payload.resume_count === "number" ? payload.resume_count : 0;
        const applicationsCount = typeof payload.application_count === "number" ? payload.application_count : 0;
        setSummaryCounts({ resumes: resumesCount, applications: applicationsCount });
      } catch {
        setSummaryCounts(null);
      }
    };

    if (!user?.id) return;
    loadSummaryCounts();
  }, [user?.id]);

  const isLoading = resumesLoading || appsLoading;

  // Compute profile completion based on real user data
  const profileCompletion = (() => {
    let score = 20; // base
    if (user?.full_name) score += 20;
    if (user?.email) score += 20;
    if (user?.phone) score += 15;
    if (user?.bio) score += 15;
    if (user?.location) score += 10;
    return score;
  })();

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return t("dashboard.greeting.morning");
    if (hour < 18) return t("dashboard.greeting.afternoon");
    return t("dashboard.greeting.evening");
  };

  const stats = [
    {
      title: t("dashboard.stats.totalResumes"),
      value: isLoading ? "—" : (summaryCounts?.resumes ?? resumes.length),
      icon: FileText,
      color: "from-purple-500 to-indigo-600",
      bgColor: "bg-purple-100 dark:bg-purple-500/20",
      iconColor: "text-purple-600",
      change:
        (summaryCounts?.resumes ?? resumes.length) > 0
          ? t("dashboard.stats.resumeCount", { count: summaryCounts?.resumes ?? resumes.length })
          : t("dashboard.stats.thisWeek"),
      changeType: "positive",
    },
    {
      title: t("dashboard.stats.applicationsSent"),
      value: isLoading ? "—" : (summaryCounts?.applications ?? appStats.total),
      icon: Send,
      color: "from-cyan-500 to-blue-600",
      bgColor: "bg-cyan-100 dark:bg-cyan-500/20",
      iconColor: "text-cyan-600",
      change:
        appStats.pending > 0
          ? t("dashboard.stats.pendingCount", { count: appStats.pending })
          : t("dashboard.stats.noApplications"),
      changeType: "positive",
    },
    {
      title: t("dashboard.stats.interviewsScheduled"),
      value: isLoading ? "—" : appStats.interview,
      icon: Calendar,
      color: "from-green-500 to-emerald-600",
      bgColor: "bg-green-100 dark:bg-green-500/20",
      iconColor: "text-green-600",
      change: appStats.interview > 0 ? t("dashboard.stats.interviewCount", { count: appStats.interview }) : t("dashboard.stats.noInterviews"),
      changeType: "neutral",
    },
    {
      title: t("dashboard.stats.profileViews"),
      value: isLoading ? "—" : appStats.reviewing,
      icon: Eye,
      color: "from-amber-500 to-orange-600",
      bgColor: "bg-amber-100 dark:bg-amber-500/20",
      iconColor: "text-amber-600",
      change: appStats.accepted > 0 ? t("dashboard.stats.acceptedCount", { count: appStats.accepted }) : t("dashboard.stats.underReview"),
      changeType: "positive",
    },
  ];

  // Build recent activity from real applications
  const applicationsForDisplay = applications as DashboardApplication[];

  const recentActivity = applicationsForDisplay.slice(0, 5).map((app) => ({
    id: app.id,
    type: "application",
    title: `${app.job?.title || t("dashboard.jobs.jobFallback")} - ${app.job?.company?.name || app.job?.company_name || t("common.company")}`,
    time: app.applied_at ? formatRelativeTime(app.applied_at, locale) : "",
    icon: app.status === "interview" ? Calendar : app.status === "accepted" ? CheckCircle : Send,
    color: app.status === "interview"
      ? "bg-green-100 text-green-600 dark:bg-green-500/20"
      : app.status === "accepted"
      ? "bg-cyan-100 text-cyan-600 dark:bg-cyan-500/20"
      : "bg-blue-100 text-blue-600 dark:bg-blue-500/20",
  }));

  const upcomingInterview = getUpcomingInterview(applicationsForDisplay as UpcomingInterviewCandidate[]);
  const upcomingInterviewCompanyName =
    upcomingInterview?.job?.company?.name ||
    upcomingInterview?.job?.company_name ||
    t("common.company");

  const quickActions = [
    {
      title: t("dashboard.quickActions.createAIResume"),
      description: t("dashboard.quickActions.createAIResumeDesc"),
      icon: Sparkles,
      href: "/student/resumes/create-ai",
      color: "from-purple-500 to-indigo-600",
      primary: true,
      badge: t("dashboard.quickActions.aiPowered"),
    },
    {
      title: t("dashboard.quickActions.browseJobs"),
      description: t("dashboard.quickActions.browseJobsDesc"),
      icon: Briefcase,
      href: "/student/jobs",
      color: "from-cyan-500 to-blue-600",
    },
    {
      title: t("dashboard.quickActions.autoApply"),
      description: t("dashboard.quickActions.autoApplyDesc"),
      icon: Zap,
      href: "/student/applications/auto-apply",
      color: "from-amber-500 to-orange-600",
    },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-surface-900 dark:text-white sm:text-3xl">
            {greeting()}, {user?.full_name?.split(" ")[0] || t("common.student")}!
          </h1>
          <p className="mt-1 text-surface-500">
            {t("dashboard.subtitle")}
          </p>
        </div>
        <Link href="/student/resumes/create-ai">
          <Button className="bg-gradient-to-r from-purple-500 to-indigo-600 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40">
            <Sparkles className="mr-2 h-4 w-4" />
            {t("dashboard.sidebar.createAIResume")}
          </Button>
        </Link>
      </motion.div>

      {/* Profile Completion Banner */}
      {profileCompletion < 100 && (
        <motion.div variants={itemVariants}>
          <Card className="border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 dark:border-amber-500/30 dark:from-amber-900/20 dark:to-orange-900/20">
            <CardContent className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-500/20">
                  <AlertCircle className="h-6 w-6 text-amber-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-surface-900 dark:text-white">{t("dashboard.profile.complete")}</h3>
                  <p className="text-sm text-surface-500">
                    {t("dashboard.profile.completeText")}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-32">
                  <div className="mb-1 flex justify-between text-xs">
                    <span>{profileCompletion}%</span>
                  </div>
                  <Progress value={profileCompletion} className="h-2" />
                </div>
                <Link href="/student/settings">
                  <Button variant="outline" size="sm">
                    {t("dashboard.sidebar.profileSettings")}
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="relative overflow-hidden hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-surface-500">{stat.title}</p>
                    <p className="mt-2 text-3xl font-bold text-surface-900 dark:text-white">
                      {stat.value}
                    </p>
                    <p className={`mt-1 text-xs ${
                      stat.changeType === "positive" ? "text-green-600" : "text-surface-500"
                    }`}>
                      {stat.change}
                    </p>
                  </div>
                  <div className={`rounded-xl p-3 ${stat.bgColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.iconColor}`} />
                  </div>
                </div>
                {/* Decorative gradient */}
                <div className={`absolute -right-8 -top-8 h-24 w-24 rounded-full bg-gradient-to-br ${stat.color} opacity-10`} />
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants}>
        <h2 className="mb-4 font-display text-lg font-semibold text-surface-900 dark:text-white">
          {t("dashboard.quickActions.title")}
        </h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {quickActions.map((action) => (
            <Link key={action.title} href={action.href}>
              <motion.div
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                className={`group relative overflow-hidden rounded-2xl p-6 text-white shadow-lg transition-shadow hover:shadow-xl ${
                  action.primary
                    ? "bg-gradient-to-br from-purple-500 to-indigo-600"
                    : "bg-gradient-to-br " + action.color
                }`}
              >
                {/* Animated background */}
                <div className="absolute inset-0 bg-[url('data:image/svg+xml,...')] opacity-10" />
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-white/10"
                />
                
                <div className="relative">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-white/20">
                    <action.icon className="h-6 w-6" />
                  </div>
                  <h3 className="font-display text-lg font-semibold">{action.title}</h3>
                  <p className="mt-1 text-sm text-white/80">{action.description}</p>
                  <ArrowRight className="mt-4 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </div>

                {action.badge && (
                  <div className="absolute right-4 top-4">
                    <span className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2 py-0.5 text-xs font-medium">
                      <Sparkles className="h-3 w-3" />
                      {action.badge}
                    </span>
                  </div>
                )}
              </motion.div>
            </Link>
          ))}
        </div>
      </motion.div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Recent Activity */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg">{t("dashboard.recentActivity.title")}</CardTitle>
              <Link href="/student/applications" className="text-sm text-purple-600 hover:underline">
                {t("dashboard.recentActivity.viewAll")}
              </Link>
            </CardHeader>
            <CardContent>
              {appsLoading ? (
                <div className="space-y-3">
                  {[1,2,3].map(i => <Skeleton key={i} className="h-12 w-full" />)}
                </div>
              ) : recentActivity.length === 0 ? (
                <p className="py-6 text-center text-sm text-surface-500">
                  {t("dashboard.recentActivity.empty")}
                </p>
              ) : (
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-4"
                    >
                      <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full ${activity.color}`}>
                        <activity.icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-surface-900 dark:text-white truncate">
                          {activity.title}
                        </p>
                        <p className="text-xs text-surface-500">{activity.time}</p>
                      </div>
                      <ChevronRight className="h-5 w-5 text-surface-400" />
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Job Recommendations */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <Target className="h-5 w-5 text-purple-600" />
                {t("dashboard.recommended.title")}
              </CardTitle>
              <Link href="/student/jobs" className="text-sm text-purple-600 hover:underline">
                {t("dashboard.recommended.browseAll")}
              </Link>
            </CardHeader>
            <CardContent>
              {recsLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-24 w-full rounded-xl" />
                  ))}
                </div>
              ) : needsResume ? (
                <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-purple-200 bg-purple-50/40 py-8 text-center dark:border-purple-500/30 dark:bg-purple-500/5">
                  <Sparkles className="h-7 w-7 text-purple-500" />
                  <p className="text-sm text-surface-600 dark:text-surface-300">
                    {t("dashboard.recommended.noResume")}
                  </p>
                  <Link href="/student/resumes/create-ai">
                    <Button size="sm">{t("dashboard.recommended.createResumeCTA")}</Button>
                  </Link>
                </div>
              ) : recommendations.length === 0 ? (
                <p className="py-6 text-center text-sm text-surface-500">
                  {t("dashboard.recommended.empty")}
                </p>
              ) : (
                <div className="space-y-4">
                  {recommendations.map((rec, index) => {
                    const score = Math.round(rec.match_score);
                    const tone =
                      score >= 80
                        ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300"
                        : score >= 60
                        ? "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300"
                        : "bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300";
                    const job = rec.job;
                    return (
                      <Link key={job.id} href={`/student/jobs/${job.id}`}>
                        <motion.div
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="group rounded-xl border border-surface-200 p-4 transition-all hover:border-purple-200 hover:shadow-md dark:border-surface-700 dark:hover:border-purple-500/30 cursor-pointer"
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0 flex-1">
                              <h4 className="truncate font-semibold text-surface-900 dark:text-white group-hover:text-purple-600">
                                {job.title}
                              </h4>
                              <p className="truncate text-sm text-surface-500">
                                {job.company?.name || t("common.company")} • {job.location}
                              </p>
                              {(job.salary_min || job.salary_max) && (
                                <p className="mt-1 text-sm font-medium text-green-600">
                                  {formatSalaryRange(job.salary_min, job.salary_max, locale, job.salary_currency || "USD")}
                                </p>
                              )}
                            </div>
                            <div className={`flex flex-col items-end shrink-0 rounded-lg px-2.5 py-1.5 ${tone}`}>
                              <span className="text-base font-bold leading-none">{score}%</span>
                              <span className="mt-0.5 text-[10px] font-semibold uppercase tracking-wider opacity-80">
                                {t("dashboard.recommended.matchLabel")}
                              </span>
                            </div>
                          </div>
                          {rec.skill_matches.length > 0 && (
                            <div className="mt-3">
                              <p className="text-[11px] font-semibold uppercase tracking-wider text-surface-500">
                                {t("dashboard.recommended.matchedSkills")}
                              </p>
                              <div className="mt-1.5 flex flex-wrap gap-1">
                                {rec.skill_matches.slice(0, 4).map((skill: string) => (
                                  <Badge
                                    key={skill}
                                    variant="secondary"
                                    className="bg-emerald-50 text-emerald-700 text-xs dark:bg-emerald-500/10 dark:text-emerald-300"
                                  >
                                    {skill}
                                  </Badge>
                                ))}
                                {rec.skill_matches.length > 4 && (
                                  <span className="text-xs text-surface-500">
                                    +{rec.skill_matches.length - 4}
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                        </motion.div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Upcoming Interviews */}
      <motion.div variants={itemVariants}>
        <Card className="border-green-200 bg-gradient-to-r from-green-50 to-emerald-50 dark:border-green-500/30 dark:from-green-900/20 dark:to-emerald-900/20">
          <CardContent className="p-6">
            {appsLoading ? (
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-4">
                  <div className="h-14 w-14 rounded-2xl bg-green-100/80 dark:bg-green-500/20" />
                  <div className="space-y-2">
                    <div className="h-5 w-44 rounded bg-green-100/80 dark:bg-green-500/20" />
                    <div className="h-4 w-64 rounded bg-green-100/70 dark:bg-green-500/10" />
                    <div className="h-4 w-56 rounded bg-green-100/70 dark:bg-green-500/10" />
                  </div>
                </div>
                <div className="flex gap-2">
                  <div className="h-10 w-28 rounded-lg bg-green-100/80 dark:bg-green-500/20" />
                  <div className="h-10 w-32 rounded-lg bg-green-100/80 dark:bg-green-500/20" />
                </div>
              </div>
            ) : upcomingInterview ? (
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-green-100 dark:bg-green-500/20">
                    <Calendar className="h-7 w-7 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-display text-lg font-semibold text-surface-900 dark:text-white">
                      {t("dashboard.interview.title")}
                    </h3>
                    <p className="text-surface-600 dark:text-surface-300">
                      <strong>{upcomingInterview.job?.title || t("dashboard.interview.title")}</strong>{" "}
                      {t("dashboard.recentActivity.at")} {upcomingInterviewCompanyName}
                    </p>
                    <p className="text-sm text-surface-500">
                      {formatInterviewDateTime(upcomingInterview.interview_at as string, locale)}
                    </p>
                    <div className="mt-3 flex flex-wrap items-center gap-3">
                      <Badge variant="secondary" className="bg-white/80 text-surface-700 dark:bg-surface-700 dark:text-surface-200">
                        {formatInterviewTypeLabel(upcomingInterview.interview_type, t)}
                      </Badge>
                      {upcomingInterview.meeting_link ? (
                        <Button asChild variant="outline" size="sm" className="h-8 rounded-full border-green-200 bg-white/80 px-3 text-green-700 hover:bg-green-50 dark:border-green-500/30 dark:bg-surface-800 dark:text-green-300 dark:hover:bg-surface-700">
                          <a
                            href={upcomingInterview.meeting_link}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {t("dashboard.interview.meetingLink")}
                          </a>
                        </Button>
                      ) : (
                        <span className="text-sm text-surface-500">
                          {t("dashboard.interview.noMeetingLink")}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => router.push("/student/applications")}>
                    {t("dashboard.interview.reschedule")}
                  </Button>
                  <Button className="bg-green-600 hover:bg-green-700" onClick={() => router.push("/student/applications")}>
                    {t("dashboard.interview.joinMeeting")}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-3 rounded-2xl border border-dashed border-green-200 bg-white/60 p-5 text-center dark:border-green-500/30 dark:bg-surface-900/30">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-green-100 dark:bg-green-500/20">
                  <Calendar className="h-7 w-7 text-green-600" />
                </div>
                <div>
                  <h3 className="font-display text-lg font-semibold text-surface-900 dark:text-white">
                    {t("dashboard.interview.title")}
                  </h3>
                  <p className="mt-1 text-sm text-surface-500">
                    {t("dashboard.interview.empty")}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
