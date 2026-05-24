/**
 * =============================================================================
 * SMARTCAREER AI - Landing Page
 * =============================================================================
 *
 * Modern SaaS-style landing page with:
 * - Hero Section with gradient & animations
 * - Features Section (3 columns)
 * - How It Works (4 steps timeline)
 * - Pricing Section (3 tiers)
 * - Testimonials (carousel)
 * - CTA Footer
 */

"use client";

import { useMemo, useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion, useScroll, useTransform } from "framer-motion";
import {
  Sparkles,
  FileText,
  Briefcase,
  Zap,
  Target,
  Shield,
  ArrowRight,
  CheckCircle,
  Star,
  Users,
  TrendingUp,
  Bot,
  Play,
  ChevronLeft,
  ChevronRight,
  User,
  Search,
  Send,
  Award,
  Clock,
  Globe,
  Rocket,
  Check,
  X,
} from "lucide-react";
import { useTranslation } from "@/hooks/useTranslation";
import { LanguageSwitcher } from "@/components/ui/language-switcher";
import { ThemeToggle } from "@/components/ui/theme-toggle";

// =============================================================================
// ANIMATION VARIANTS
// =============================================================================

const fadeInUp = {
  initial: { opacity: 1, y: 0 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 },
};

const fadeIn = {
  initial: { opacity: 1 },
  animate: { opacity: 1 },
  transition: { duration: 0.5 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const scaleIn = {
  initial: { opacity: 1, scale: 1 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.5 },
};

// =============================================================================
// DATA
// =============================================================================

const features = [
  {
    icon: Bot,
    title: "AI Resume Builder",
    description:
      "Generate professional, ATS-optimized resumes in seconds with GPT-4 powered AI. Stand out from the crowd.",
    color: "from-purple-500 to-indigo-600",
    bgColor: "bg-purple-500/10",
    iconColor: "text-purple-500",
  },
  {
    icon: Target,
    title: "Smart Job Matching",
    description:
      "AI analyzes your skills and experience to find perfect job matches. No more endless scrolling.",
    color: "from-cyan-500 to-blue-600",
    bgColor: "bg-cyan-500/10",
    iconColor: "text-cyan-500",
  },
  {
    icon: Zap,
    title: "Auto Apply",
    description:
      "Apply to multiple matching jobs automatically with one click. Save hours of repetitive work.",
    color: "from-amber-500 to-orange-600",
    bgColor: "bg-amber-500/10",
    iconColor: "text-amber-500",
  },
];

const howItWorks = [
  {
    step: 1,
    icon: User,
    title: "Create Profile",
    description: "Sign up and enter your experience, skills, and career goals.",
  },
  {
    step: 2,
    icon: Sparkles,
    title: "Generate AI Resume",
    description: "Our AI creates a stunning, professional resume tailored to your industry.",
  },
  {
    step: 3,
    icon: Search,
    title: "Browse Jobs",
    description: "Explore AI-matched job opportunities that fit your profile perfectly.",
  },
  {
    step: 4,
    icon: Award,
    title: "Get Hired",
    description: "Apply with confidence and land your dream job faster than ever.",
  },
];

const pricingPlans = [
  {
    name: "Free",
    price: "0",
    description: "Perfect for getting started",
    features: [
      "1 AI-generated resume",
      "Basic job search",
      "5 job applications/month",
      "Email support",
    ],
    notIncluded: [
      "Unlimited AI generations",
      "Auto-apply feature",
      "Priority support",
      "Analytics dashboard",
    ],
    cta: "Start Free",
    popular: false,
  },
  {
    name: "Pro",
    price: "4",
    description: "For serious job seekers",
    features: [
      "Unlimited AI resumes",
      "Advanced job matching",
      "50 applications/month",
      "Auto-apply feature",
      "Cover letter generator",
      "Priority email support",
      "Analytics dashboard",
    ],
    notIncluded: ["Custom integrations"],
    cta: "Start Pro Trial",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For teams & organizations",
    features: [
      "Everything in Pro",
      "Unlimited applications",
      "Team management",
      "Custom integrations",
      "API access",
      "Dedicated support",
      "Custom branding",
      "SLA guarantee",
    ],
    notIncluded: [],
    cta: "Contact Sales",
    popular: false,
  },
];

type TestimonialItem = {
  name: string;
  role: string;
  company: string;
  image: string | null;
  quote: string;
  rating: number;
};

const testimonials: TestimonialItem[] = [
  {
    name: "Aziz Karimov",
    role: "Software Developer",
    company: "EPAM Systems",
    image: null,
    quote:
      "IshTop completely transformed my job search. The AI resume generator helped me create a professional resume that got me 5x more interviews!",
    rating: 5,
  },
  {
    name: "Dilnoza Rahimova",
    role: "Marketing Manager",
    company: "Uzum Market",
    image: null,
    quote:
      "The auto-apply feature saved me countless hours. I applied to 50 relevant jobs in one afternoon. Got my dream job within 2 weeks!",
    rating: 5,
  },
  {
    name: "Bobur Toshmatov",
    role: "Data Analyst",
    company: "Click.uz",
    image: null,
    quote:
      "As a fresh graduate, I didn't know how to write a proper resume. IshTop created a stunning resume that helped me land my first tech job.",
    rating: 5,
  },
  {
    name: "Malika Yusupova",
    role: "Product Manager",
    company: "Payme",
    image: null,
    quote:
      "The smart job matching is incredibly accurate. Every recommendation was relevant to my skills and experience. Highly recommend!",
    rating: 5,
  },
  {
    name: "Jahongir Aliyev",
    role: "UI/UX Designer",
    company: "Freelancer",
    image: null,
    quote:
      "Finally, a platform that understands the Uzbekistan job market! The AI suggestions for my portfolio and resume were spot-on.",
    rating: 5,
  },
];

const statsKeys = [
  { value: "50K+", labelKey: "landing.stats.resumes" },
  { value: "10K+", labelKey: "landing.stats.users" },
  { value: "95%", labelKey: "landing.stats.successRate" },
  { value: "500+", labelKey: "landing.stats.companies" },
];

type LandingPayload = {
  hero?: { title?: string; subtitle?: string; primaryCta?: string; secondaryCta?: string };
  stats?: Array<{ value: string; label: string }>;
  features?: Array<{ title: string; description: string }>;
  howItWorks?: Array<{ title: string; description: string }>;
  pricing?: Array<{
    name: string;
    price: string;
    description: string;
    cta: string;
    features: string[];
    notIncluded?: string[];
    popular?: boolean;
  }>;
  testimonials?: Array<{ name: string; role: string; company: string; quote: string; rating?: number; image?: string | null }>;
  cta?: { title?: string; subtitle?: string; button?: string };
  footer?: { description?: string };
};

// =============================================================================
// COMPONENTS
// =============================================================================

function TestimonialCard({
  testimonial,
  isActive,
}: {
  testimonial: TestimonialItem;
  isActive: boolean;
}) {
  return (
    <motion.div
      initial={false}
      animate={{ opacity: isActive ? 1 : 0.5, scale: isActive ? 1 : 0.95 }}
      transition={{ duration: 0.3 }}
      className={`relative overflow-hidden rounded-3xl border bg-white/95 p-8 shadow-2xl backdrop-blur transition-all dark:bg-surface-900/90 ${
        isActive ? "border-brand-400/60" : "border-surface-200 dark:border-surface-700"
      }`}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-violet-500 via-cyan-500 to-emerald-500" />
      {/* Quote */}
      <p className="mb-7 text-xl leading-relaxed text-surface-700 italic dark:text-surface-200">&ldquo;{testimonial.quote}&rdquo;</p>

      {/* Rating */}
      <div className="mb-6 flex gap-1.5">
        {[...Array(testimonial.rating)].map((_, i) => (
          <Star key={i} className="h-5 w-5 fill-amber-400 text-amber-400" />
        ))}
      </div>

      {/* Author */}
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-400 to-purple-600 text-lg font-bold text-white shadow-lg shadow-violet-500/20">
          {testimonial.name
            .split(" ")
            .map((n) => n[0])
            .join("")}
        </div>
        <div>
          <p className="text-lg font-semibold text-surface-900 dark:text-surface-100">{testimonial.name}</p>
          <p className="text-sm text-surface-600 dark:text-surface-300">
            {testimonial.role} at {testimonial.company}
          </p>
        </div>
      </div>
    </motion.div>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function LandingPageClient({ cmsPayload }: { cmsPayload?: LandingPayload | null }) {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const { scrollYProgress } = useScroll();
  const heroY = useTransform(scrollYProgress, [0, 0.5], [0, -100]);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);
  const { t, translations, locale } = useTranslation();
  const isRu = locale === "ru";
  const dynamicStats = useMemo(() => {
    if (cmsPayload?.stats && cmsPayload.stats.length > 0) {
      return cmsPayload.stats;
    }
    return statsKeys.map((item) => ({ value: item.value, label: t(item.labelKey) }));
  }, [cmsPayload?.stats, t]);
  const dynamicTestimonials = useMemo(() => {
    if (cmsPayload?.testimonials && cmsPayload.testimonials.length > 0) {
      return cmsPayload.testimonials.map((entry) => ({ ...entry, image: entry.image ?? null, rating: entry.rating ?? 5 }));
    }
    return testimonials;
  }, [cmsPayload?.testimonials]);
  const dynamicFeatures = useMemo(() => {
    if (cmsPayload?.features && cmsPayload.features.length >= 3) return cmsPayload.features;
    return [
      { title: t("landing.features.ai.title"), description: t("landing.features.ai.description") },
      { title: t("landing.features.matching.title"), description: t("landing.features.matching.description") },
      { title: t("landing.features.autoApply.title"), description: t("landing.features.autoApply.description") },
    ];
  }, [cmsPayload?.features, t]);
  const dynamicHowItWorks = useMemo(() => {
    if (cmsPayload?.howItWorks && cmsPayload.howItWorks.length >= 4) return cmsPayload.howItWorks;
    return [
      { title: t("landing.howItWorks.step1.title"), description: t("landing.howItWorks.step1.description") },
      { title: t("landing.howItWorks.step2.title"), description: t("landing.howItWorks.step2.description") },
      { title: t("landing.howItWorks.step3.title"), description: t("landing.howItWorks.step3.description") },
      { title: t("landing.howItWorks.step4.title"), description: t("landing.howItWorks.step4.description") },
    ];
  }, [cmsPayload?.howItWorks, t]);
  const dynamicPricing = useMemo(() => {
    if (cmsPayload?.pricing && cmsPayload.pricing.length >= 3) {
      return cmsPayload.pricing;
    }
    return [
      {
        name: t("landing.pricing.free.name"),
        price: t("landing.pricing.free.price"),
        description: t("landing.pricing.free.description"),
        cta: t("landing.pricing.free.cta"),
        features: translations.landing.pricing.free.features as string[],
        notIncluded: translations.landing.pricing.free.notIncluded as string[],
        popular: false,
      },
      {
        name: t("landing.pricing.pro.name"),
        price: t("landing.pricing.pro.price"),
        description: t("landing.pricing.pro.description"),
        cta: t("landing.pricing.pro.cta"),
        features: translations.landing.pricing.pro.features as string[],
        notIncluded: translations.landing.pricing.pro.notIncluded as string[],
        popular: true,
      },
      {
        name: t("landing.pricing.enterprise.name"),
        price: t("landing.pricing.enterprise.price"),
        description: t("landing.pricing.enterprise.description"),
        cta: t("landing.pricing.enterprise.cta"),
        features: translations.landing.pricing.enterprise.features as string[],
        notIncluded: [],
        popular: false,
      },
    ];
  }, [cmsPayload?.pricing, t, translations]);
  const featureVisuals = [
    {
      icon: Bot,
      iconWrap: "from-violet-500/20 to-fuchsia-500/20 text-violet-600 dark:text-violet-300",
      accent: "from-violet-500 to-indigo-500",
      ring: "ring-violet-500/30",
    },
    {
      icon: Target,
      iconWrap: "from-cyan-500/20 to-sky-500/20 text-cyan-600 dark:text-cyan-300",
      accent: "from-cyan-500 to-blue-500",
      ring: "ring-cyan-500/30",
    },
    {
      icon: Zap,
      iconWrap: "from-amber-500/20 to-orange-500/20 text-amber-600 dark:text-amber-300",
      accent: "from-amber-500 to-orange-500",
      ring: "ring-amber-500/30",
    },
  ] as const;
  const howIcons = [User, Sparkles, Search, Award] as const;
  const heroJobs = isRu
    ? [
        { title: "Frontend-разработчик", company: "EPAM Systems", salary: "$1200–1800", match: "98%", color: "from-purple-400 to-indigo-500" },
        { title: "React-инженер", company: "Click.uz", salary: "$900–1400", match: "94%", color: "from-cyan-400 to-blue-500" },
        { title: "UI/UX-дизайнер", company: "Uzum Market", salary: "$800–1200", match: "91%", color: "from-pink-400 to-rose-500" },
        { title: "Аналитик данных", company: "Payme", salary: "$1000–1500", match: "87%", color: "from-amber-400 to-orange-500" },
      ]
    : [
        { title: "Frontend dasturchi", company: "EPAM Systems", salary: "$1200–1800", match: "98%", color: "from-purple-400 to-indigo-500" },
        { title: "React muhandisi", company: "Click.uz", salary: "$900–1400", match: "94%", color: "from-cyan-400 to-blue-500" },
        { title: "UI/UX dizayner", company: "Uzum Market", salary: "$800–1200", match: "91%", color: "from-pink-400 to-rose-500" },
        { title: "Ma'lumotlar tahlilchisi", company: "Payme", salary: "$1000–1500", match: "87%", color: "from-amber-400 to-orange-500" },
      ];

  // Auto-rotate testimonials
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % Math.max(dynamicTestimonials.length, 1));
    }, 5000);
    return () => clearInterval(timer);
  }, [dynamicTestimonials.length]);

  return (
    <div className="min-h-screen bg-white text-surface-900 transition-colors dark:bg-surface-950 dark:text-surface-100">
      {/* ===================================================================
          NAVIGATION
          =================================================================== */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-surface-200/50 bg-white/80 backdrop-blur-xl transition-colors dark:border-surface-700/60 dark:bg-surface-950/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2">
              <Image
                src="/logo-mark.png"
                alt="IshTop"
                width={36}
                height={36}
                priority
                className="h-9 w-9 rounded-xl"
              />
              <span className="font-display text-xl font-bold text-surface-900 dark:text-surface-100">IshTop</span>
            </Link>

            {/* Nav Links */}
            <div className="hidden items-center gap-8 md:flex">
              <Link
                href="#features"
                className="text-base font-semibold text-surface-700 transition-colors hover:text-surface-950 dark:text-surface-200 dark:hover:text-white"
              >
                {t("nav.features")}
              </Link>
              <Link
                href="#how-it-works"
                className="text-base font-semibold text-surface-700 transition-colors hover:text-surface-950 dark:text-surface-200 dark:hover:text-white"
              >
                {t("nav.howItWorks")}
              </Link>
              <Link
                href="#pricing"
                className="text-base font-semibold text-surface-700 transition-colors hover:text-surface-950 dark:text-surface-200 dark:hover:text-white"
              >
                {t("nav.pricing")}
              </Link>
              <Link
                href="#testimonials"
                className="text-base font-semibold text-surface-700 transition-colors hover:text-surface-950 dark:text-surface-200 dark:hover:text-white"
              >
                {t("nav.testimonials")}
              </Link>
            </div>

            {/* Language Switcher + Auth Buttons */}
            <div className="flex items-center gap-3">
              {/* Dark Mode Toggle */}
              <ThemeToggle />
              
              {/* Language Switcher */}
              <LanguageSwitcher variant="minimal" />
              
              <Link
                href="/login"
                className="rounded-lg px-4 py-2 text-sm font-medium text-surface-600 transition-colors hover:text-surface-900 dark:text-surface-300 dark:hover:text-surface-100"
              >
                {t("nav.signIn")}
              </Link>
              <Link
                href="/register"
                className="rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-purple-500/25 transition-all hover:shadow-purple-500/40 hover:scale-[1.02]"
              >
                {t("nav.getStarted")}
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* ===================================================================
          HERO SECTION
          =================================================================== */}
      <section className="relative min-h-screen overflow-hidden pt-16">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-500 via-indigo-500 to-blue-600 dark:from-slate-950 dark:via-indigo-950 dark:to-slate-900">
          {/* Animated shapes */}
          <div className="absolute inset-0 overflow-hidden">
            <motion.div
              animate={{
                x: [0, 100, 0],
                y: [0, -50, 0],
                rotate: [0, 180, 360],
              }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute -top-20 -right-20 h-96 w-96 rounded-full bg-white/5 blur-3xl"
            />
            <motion.div
              animate={{
                x: [0, -100, 0],
                y: [0, 50, 0],
                rotate: [360, 180, 0],
              }}
              transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
              className="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-cyan-400/10 blur-3xl"
            />
            <motion.div
              animate={{
                x: [0, 50, 0],
                y: [0, -100, 0],
              }}
              transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
              className="absolute top-1/2 left-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-amber-400/10 blur-3xl"
            />
          </div>
          {/* Grid pattern */}
          <div
            className="absolute inset-0 opacity-10"
            style={{
              backgroundImage:
                "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
              backgroundSize: "50px 50px",
            }}
          />
        </div>

        {/* Content */}
        <motion.div
          style={{ y: heroY, opacity: heroOpacity }}
          className="relative mx-auto max-w-7xl px-4 pt-20 pb-32 sm:px-6 lg:px-8 lg:pt-32"
        >
          <div className="text-center">
            {/* Headline */}
            <motion.h1
              initial={false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mx-auto max-w-4xl font-display text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl xl:text-7xl"
            >
              {cmsPayload?.hero?.title || t("landing.hero.title")}
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              initial={false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mx-auto mt-6 max-w-2xl text-lg text-purple-100 sm:text-xl"
            >
              {cmsPayload?.hero?.subtitle || t("landing.hero.subtitle")}
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
            >
              <Link
                href="/register"
                className="group flex items-center gap-2 rounded-2xl bg-white px-8 py-4 text-lg font-semibold text-purple-600 shadow-xl shadow-black/10 transition-all hover:shadow-black/20 hover:scale-[1.02]"
              >
                {cmsPayload?.hero?.primaryCta || t("landing.hero.cta")}
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <a href="#demo" className="flex items-center gap-3 rounded-2xl border border-white/40 bg-white/15 px-8 py-4 text-lg font-semibold text-white backdrop-blur-sm transition-all hover:bg-white/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/80">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/20">
                  <Play className="h-5 w-5 fill-white" />
                </span>
                {cmsPayload?.hero?.secondaryCta || t("landing.hero.watchDemo")}
              </a>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="mt-16 grid grid-cols-2 gap-8 sm:grid-cols-4"
            >
              {dynamicStats.map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl font-bold text-white sm:text-4xl">{stat.value}</div>
                  <div className="mt-1 text-sm text-purple-100">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Hero Image / Dashboard Preview */}
          <motion.div
            initial={false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.8 }}
            className="relative mx-auto mt-16 max-w-5xl"
          >
            {/* Glow effect */}
            <div className="absolute -inset-4 rounded-3xl bg-gradient-to-r from-cyan-400/30 to-amber-400/30 blur-2xl" />

            {/* Dashboard mockup */}
            <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-white/10 shadow-2xl backdrop-blur-xl">
              {/* Browser chrome */}
              <div className="flex items-center gap-2 border-b border-white/10 bg-white/5 px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-red-400" />
                  <div className="h-3 w-3 rounded-full bg-yellow-400" />
                  <div className="h-3 w-3 rounded-full bg-green-400" />
                </div>
                <div className="ml-4 flex-1 rounded-lg bg-white/10 px-3 py-1 text-xs text-white/70">
                  ishtop.uz/dashboard
                </div>
              </div>

              {/* Content mockup */}
              <div className="grid gap-4 p-4 md:grid-cols-3">
                {/* Sidebar */}
                <div className="space-y-2 rounded-xl bg-white/10 p-4">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-white/40">Menyu</p>
                  {[
                    { icon: "🏠", label: "Dashboard", active: true },
                    { icon: "📄", label: "Resumelar", active: false },
                    { icon: "💼", label: "Ishlar", active: false },
                    { icon: "📋", label: "Arizalar", active: false },
                    { icon: "⚙️", label: "Sozlamalar", active: false },
                  ].map((item) => (
                    <div
                      key={item.label}
                      className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm ${
                        item.active ? "bg-white/20 text-white" : "text-white/60"
                      }`}
                    >
                      <span>{item.icon}</span>
                      <span>{item.label}</span>
                    </div>
                  ))}
                </div>

                {/* Main content */}
                <div className="col-span-2 space-y-3 rounded-xl bg-white/10 p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-white">Tavsiya etilgan ishlar</p>
                    <span className="rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 px-3 py-0.5 text-xs font-semibold text-white">AI moslik</span>
                  </div>
                  <div className="grid gap-3 md:grid-cols-2">
                    {heroJobs.map((job) => (
                      <div key={job.title} className="rounded-lg border border-white/10 bg-white/5 p-3">
                        <div className="mb-2 flex items-center gap-2.5">
                          <div className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br ${job.color} text-xs font-bold text-white`}>
                            {job.company[0]}
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-white">{job.title}</p>
                            <p className="text-xs text-white/50">{job.company}</p>
                          </div>
                          <span className="ml-auto rounded-full bg-green-400/20 px-1.5 py-0.5 text-xs font-bold text-green-400">{job.match}</span>
                        </div>
                        <p className="text-xs text-white/40">{job.salary}/oy</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* Wave separator */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-white dark:text-surface-950">
            <path
              d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
              fill="currentColor"
            />
          </svg>
        </div>
      </section>

      <section id="demo" className="bg-surface-100 py-16 dark:bg-surface-900/70">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl border border-surface-300/70 bg-white p-8 shadow-xl dark:border-surface-700 dark:bg-surface-900">
            <h2 className="font-display text-3xl font-bold text-surface-900 dark:text-white sm:text-4xl">
              {isRu ? "Как это работает в реальности" : "Platforma qanday ishlashini ko'ring"}
            </h2>
            <p className="mt-3 text-lg text-surface-700 dark:text-surface-200">
              {isRu
                ? "Краткий демо-обзор главных возможностей платформы."
                : "Platformaning asosiy imkoniyatlarini tezkor demo orqali ko'ring."}
            </p>
            <div className="mt-6 aspect-video overflow-hidden rounded-2xl border border-surface-300 dark:border-surface-700">
              <iframe
                title="IshTop demo video"
                className="h-full w-full"
                src="https://www.youtube.com/embed/dQw4w9WgXcQ"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          FEATURES SECTION
          =================================================================== */}
      <section id="features" className="relative py-24 lg:py-32 dark:bg-surface-950">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.12),transparent_48%)] dark:bg-[radial-gradient(ellipse_at_top,rgba(56,189,248,0.10),transparent_52%)]" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex rounded-full border border-violet-300/70 bg-violet-100/80 px-5 py-2 text-xs font-bold uppercase tracking-[0.16em] text-violet-700 dark:border-violet-400/30 dark:bg-violet-500/15 dark:text-violet-200">
              {t("landing.features.badge")}
            </span>
            <h2 className="mt-6 font-display text-4xl font-bold tracking-tight text-surface-900 dark:text-surface-100 sm:text-5xl">
              {t("landing.features.title")} <span className="bg-gradient-to-r from-violet-500 to-cyan-500 bg-clip-text text-transparent">{t("landing.features.titleHighlight")}</span>
            </h2>
            <p className="mt-5 text-xl leading-relaxed text-surface-600 dark:text-surface-300">{t("landing.features.subtitle")}</p>
          </div>

          <div className="mt-16 grid gap-7 md:grid-cols-3">
            {dynamicFeatures.slice(0, 3).map((feature, idx) => {
              const visual = featureVisuals[idx];
              const Icon = visual.icon;
              return (
                <motion.article
                  key={feature.title}
                  variants={fadeInUp}
                  whileHover={{ y: -8 }}
                  className={`group relative overflow-hidden rounded-3xl border border-surface-200/80 bg-white/95 p-8 shadow-xl shadow-surface-900/5 ring-1 ${visual.ring} transition-all hover:shadow-2xl dark:border-surface-700 dark:bg-surface-900/75`}
                >
                  <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${visual.accent}`} />
                  <div className={`mb-6 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${visual.iconWrap}`}>
                    <Icon className="h-7 w-7" />
                  </div>
                  <h3 className="mb-3 font-display text-2xl font-semibold text-surface-900 dark:text-surface-100">{feature.title}</h3>
                  <p className="text-base leading-7 text-surface-600 dark:text-surface-300">{feature.description}</p>
                  <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-violet-600 dark:text-violet-300">
                    {t("landing.features.learnMore")} <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </div>
                </motion.article>
              );
            })}
          </div>
        </div>
      </section>

      {/* ===================================================================
          HOW IT WORKS SECTION
          =================================================================== */}
      <section id="how-it-works" className="bg-surface-50 py-24 lg:py-32 dark:bg-surface-950/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex rounded-full border border-cyan-300/80 bg-cyan-100/80 px-5 py-2 text-xs font-bold uppercase tracking-[0.16em] text-cyan-700 dark:border-cyan-400/30 dark:bg-cyan-500/15 dark:text-cyan-200">{t("landing.howItWorks.badge")}</span>
            <h2 className="mt-6 font-display text-4xl font-bold tracking-tight text-surface-900 dark:text-surface-100 sm:text-5xl">{t("landing.howItWorks.title")}</h2>
          </div>

          <div className="relative mt-16">
            <div className="absolute left-1/2 top-10 hidden h-[calc(100%-5rem)] w-px -translate-x-1/2 bg-gradient-to-b from-violet-500 via-cyan-500 to-emerald-500 md:block" />
            <div className="grid gap-6 md:grid-cols-2">
              {dynamicHowItWorks.slice(0, 4).map((step, idx) => {
                const Icon = howIcons[idx] || User;
                const align = idx % 2 === 0 ? "md:mr-10" : "md:ml-10";
                return (
                  <motion.div key={step.title} variants={fadeInUp} className={`relative ${align}`}>
                    <div className="relative rounded-3xl border border-surface-200 bg-white/95 p-6 shadow-xl shadow-surface-900/5 dark:border-surface-700 dark:bg-surface-900/75">
                      <div className="mb-4 flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-500 text-white shadow-lg shadow-violet-500/25">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-xs font-bold uppercase tracking-[0.16em] text-violet-600 dark:text-violet-300">{t("landing.howItWorks.step")} {idx + 1}</p>
                          <h3 className="font-display text-xl font-semibold text-surface-900 dark:text-surface-100">{step.title}</h3>
                        </div>
                      </div>
                      <p className="text-base leading-7 text-surface-600 dark:text-surface-300">{step.description}</p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          PRICING SECTION
          =================================================================== */}
      <section id="pricing" className="relative py-24 lg:py-32 dark:bg-surface-950">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={false}
            whileInView="animate"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center"
          >
            <motion.span
              variants={fadeInUp}
              className="inline-block rounded-full bg-amber-100 px-4 py-1.5 text-sm font-semibold text-amber-700 dark:bg-amber-500/20 dark:text-amber-200"
            >
              {t("landing.pricing.badge")}
            </motion.span>
            <motion.h2
              variants={fadeInUp}
              className="mt-4 font-display text-3xl font-bold text-surface-900 dark:text-surface-100 sm:text-4xl lg:text-5xl"
            >
              {t("landing.pricing.title")}
            </motion.h2>
            <motion.p
              variants={fadeInUp}
              className="mx-auto mt-4 max-w-2xl text-lg text-surface-600 dark:text-surface-300"
            >
              {t("landing.pricing.subtitle")}
            </motion.p>
          </motion.div>

          <motion.div initial={false} whileInView="animate" viewport={{ once: true }} variants={staggerContainer} className="mt-16 grid gap-8 lg:grid-cols-3">
            {dynamicPricing.slice(0, 3).map((plan, idx) => {
              const isPopular = Boolean(plan.popular) || idx === 1;
              return (
                <motion.article
                  key={plan.name}
                  variants={fadeInUp}
                  whileHover={{ y: -8 }}
                  className={`relative rounded-3xl border bg-white/95 p-8 shadow-xl transition-all dark:bg-surface-900/75 ${
                    isPopular
                      ? "border-violet-400 shadow-violet-500/20 ring-1 ring-violet-400/30"
                      : "border-surface-200 dark:border-surface-700"
                  }`}
                >
                  {isPopular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-violet-500 to-indigo-500 px-4 py-1 text-sm font-semibold text-white shadow-lg">
                        <Star className="h-4 w-4 fill-amber-300 text-amber-300" />
                        {t("landing.pricing.mostPopular")}
                      </span>
                    </div>
                  )}
                  <h3 className="font-display text-2xl font-semibold text-surface-900 dark:text-surface-100">{plan.name}</h3>
                  <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">{plan.description}</p>
                  <div className="mt-5 flex items-end gap-1">
                    <span className="text-4xl font-bold tracking-tight text-surface-900 dark:text-surface-100">{plan.price}</span>
                    {idx !== 2 && <span className="pb-1 text-surface-500 dark:text-surface-400">/{t("landing.pricing.month")}</span>}
                  </div>
                  <ul className="mt-7 space-y-3">
                    {(plan.features || []).map((feature, fi) => (
                      <li key={fi} className="flex items-start gap-3 text-sm">
                        <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-500" />
                        <span className="text-surface-700 dark:text-surface-200">{feature}</span>
                      </li>
                    ))}
                    {(plan.notIncluded || []).map((feature, fi) => (
                      <li key={`x-${fi}`} className="flex items-start gap-3 text-sm opacity-65">
                        <X className="mt-0.5 h-4 w-4 flex-shrink-0 text-surface-400" />
                        <span className="text-surface-500 dark:text-surface-400">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Link
                    href="/register"
                    className={`mt-8 block w-full rounded-xl py-3 text-center text-sm font-semibold transition-all ${
                      isPopular
                        ? "bg-gradient-to-r from-violet-500 to-indigo-500 text-white shadow-lg shadow-violet-500/30 hover:shadow-violet-500/45"
                        : "border border-surface-300 text-surface-800 hover:bg-surface-100 dark:border-surface-600 dark:text-surface-100 dark:hover:bg-surface-800"
                    }`}
                  >
                    {plan.cta}
                  </Link>
                </motion.article>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* ===================================================================
          TESTIMONIALS SECTION
          =================================================================== */}
      <section id="testimonials" className="bg-surface-50 py-24 lg:py-32 dark:bg-surface-950/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={false}
            whileInView="animate"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center"
          >
            <motion.span
              variants={fadeInUp}
              className="inline-block rounded-full bg-green-100 px-4 py-1.5 text-sm font-semibold text-green-700 dark:bg-green-500/20 dark:text-green-200"
            >
              {t("landing.testimonials.badge")}
            </motion.span>
            <motion.h2
              variants={fadeInUp}
              className="mt-4 font-display text-3xl font-bold text-surface-900 dark:text-surface-100 sm:text-4xl lg:text-5xl"
            >
              {t("landing.testimonials.title")}
            </motion.h2>
            <motion.p
              variants={fadeInUp}
              className="mx-auto mt-4 max-w-2xl text-lg text-surface-600 dark:text-surface-300"
            >
              {t("landing.testimonials.subtitle")}
            </motion.p>
          </motion.div>

          {/* Testimonial Carousel */}
          <div className="relative mx-auto mt-16 max-w-5xl rounded-3xl border border-surface-200/80 bg-white/85 p-6 shadow-2xl shadow-surface-900/5 backdrop-blur-sm dark:border-surface-700 dark:bg-surface-900/70 md:p-10">
            <div className="flex items-center justify-center gap-4 md:gap-8">
              {/* Previous button */}
              <button
                onClick={() =>
                  setCurrentTestimonial(
                    (prev) => (prev - 1 + dynamicTestimonials.length) % dynamicTestimonials.length
                  )
                }
                className="flex h-11 w-11 items-center justify-center rounded-xl border border-surface-300 bg-white text-surface-700 shadow-sm transition-all hover:-translate-y-0.5 hover:border-violet-300 hover:text-violet-600 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-300 dark:hover:border-violet-400/40"
              >
                <ChevronLeft className="h-6 w-6" />
              </button>

              {/* Testimonial cards */}
              <div className="w-full max-w-3xl">
                <TestimonialCard
                  testimonial={dynamicTestimonials[currentTestimonial]}
                  isActive={true}
                />
              </div>

              {/* Next button */}
              <button
                onClick={() =>
                  setCurrentTestimonial((prev) => (prev + 1) % dynamicTestimonials.length)
                }
                className="flex h-11 w-11 items-center justify-center rounded-xl border border-surface-300 bg-white text-surface-700 shadow-sm transition-all hover:-translate-y-0.5 hover:border-violet-300 hover:text-violet-600 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-300 dark:hover:border-violet-400/40"
              >
                <ChevronRight className="h-6 w-6" />
              </button>
            </div>

            {/* Dots indicator */}
            <div className="mt-8 flex justify-center gap-2.5">
              {dynamicTestimonials.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentTestimonial(i)}
                  className={`h-2 rounded-full transition-all ${
                    i === currentTestimonial
                      ? "w-9 bg-gradient-to-r from-violet-500 to-indigo-500"
                      : "w-2.5 bg-surface-300 hover:bg-surface-400 dark:bg-surface-700 dark:hover:bg-surface-500"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================
          CTA SECTION
          =================================================================== */}
      <section className="py-20 lg:py-32">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={false}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-700 p-8 text-center md:p-16"
          >
            {/* Decorative elements */}
            <div className="absolute -right-20 -top-20 h-60 w-60 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute -bottom-20 -left-20 h-60 w-60 rounded-full bg-cyan-400/20 blur-3xl" />
            <div className="absolute right-1/4 top-1/4 h-40 w-40 rounded-full bg-amber-400/10 blur-3xl" />

            <div className="relative">
              <motion.div
                initial={false}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ type: "spring", delay: 0.2 }}
                className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-white/10 backdrop-blur-sm"
              >
                <Rocket className="h-10 w-10 text-white" />
              </motion.div>

              <h2 className="font-display text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
                {cmsPayload?.cta?.title || t("landing.cta.title")}
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-lg text-purple-100">
                {cmsPayload?.cta?.subtitle || t("landing.cta.subtitle")}
              </p>

              <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
                <Link
                  href="/register"
                  className="inline-flex items-center gap-2 rounded-2xl bg-white px-8 py-4 text-lg font-semibold text-purple-600 shadow-xl transition-all hover:bg-purple-50 hover:scale-[1.02]"
                >
                  {cmsPayload?.cta?.button || t("landing.cta.button")}
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===================================================================
          FOOTER
          =================================================================== */}
      <footer className="border-t border-surface-200 bg-white py-12 dark:border-surface-700 dark:bg-surface-950">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-4">
            {/* Brand */}
            <div>
              <Link href="/" className="flex items-center gap-2">
                <Image
                  src="/logo-mark.png"
                  alt="IshTop"
                  width={36}
                  height={36}
                  className="h-9 w-9 rounded-xl"
                />
                <span className="font-display text-xl font-bold text-surface-900 dark:text-surface-100">
                  IshTop
                </span>
              </Link>
              <p className="mt-4 text-sm text-surface-500 dark:text-surface-400">
                {cmsPayload?.footer?.description || t("landing.footer.description")}
              </p>
            </div>

            {/* Product */}
            <div>
              <h4 className="font-semibold text-surface-900 dark:text-surface-100">{t("landing.footer.product")}</h4>
              <ul className="mt-4 space-y-2 text-sm text-surface-500 dark:text-surface-400">
                <li>
                  <Link href="#features" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.features")}
                  </Link>
                </li>
                <li>
                  <Link href="#pricing" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.pricingLink")}
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.api")}
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.integrations")}
                  </Link>
                </li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="font-semibold text-surface-900 dark:text-surface-100">{t("landing.footer.company")}</h4>
              <ul className="mt-4 space-y-2 text-sm text-surface-500 dark:text-surface-400">
                <li>
                  <Link href="#" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.about")}
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.blog")}
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.careers")}
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.contact")}
                  </Link>
                </li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="font-semibold text-surface-900 dark:text-surface-100">{t("landing.footer.legal")}</h4>
              <ul className="mt-4 space-y-2 text-sm text-surface-500 dark:text-surface-400">
                <li>
                  <Link href="/privacy" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.privacy")}
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.terms")}
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-surface-900 dark:hover:text-surface-200">
                    {t("landing.footer.cookies")}
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom */}
          <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-surface-200 pt-8 md:flex-row dark:border-surface-700">
            <p className="text-sm text-surface-500 dark:text-surface-400">
              © {new Date().getFullYear()} IshTop. {t("landing.footer.rights")}
            </p>
            <div className="flex gap-4">
              <Link
                href="#"
                className="text-surface-400 transition-colors hover:text-surface-600 dark:text-surface-500 dark:hover:text-surface-300"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
                </svg>
              </Link>
              <Link
                href="#"
                className="text-surface-400 transition-colors hover:text-surface-600 dark:text-surface-500 dark:hover:text-surface-300"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
              </Link>
              <Link
                href="#"
                className="text-surface-400 transition-colors hover:text-surface-600 dark:text-surface-500 dark:hover:text-surface-300"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
              </Link>
              <Link
                href="#"
                className="text-surface-400 transition-colors hover:text-surface-600 dark:text-surface-500 dark:hover:text-surface-300"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
