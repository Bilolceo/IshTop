"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { CheckCircle2, Loader2 } from "lucide-react";

import { getErrorMessage, surveyApi } from "@/lib/api";
import {
  STUDENT_SURVEY,
  STUDENT_SURVEY_KEY,
  firstMissing,
  toggleMulti,
  type SurveyAnswers,
} from "@/lib/surveys";
import { useTranslation } from "@/hooks/useTranslation";
import { LanguageSwitcherInline } from "@/components/ui/language-switcher";

// ?src=tatu-chat tells us which chat or channel the respondent came from.
function readSource(): string | null {
  if (typeof window === "undefined") return null;
  const v = new URLSearchParams(window.location.search).get("src");
  return v ? v.slice(0, 40) : null;
}

export function SurveyForm() {
  const { locale } = useTranslation();
  const lang = locale === "ru" ? "ru" : "uz";
  const t = (uz: string, ru: string) => (lang === "ru" ? ru : uz);

  const [answers, setAnswers] = useState<SurveyAnswers>({});
  const [honeypot, setHoneypot] = useState("");
  const [missing, setMissing] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [contact, setContact] = useState("");
  const [contactState, setContactState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const source = useMemo(readSource, []);

  useEffect(() => {
    if (!missing) return;
    document.getElementById(`q-${missing}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [missing]);

  const set = (id: string, v: string | string[]) => {
    setAnswers((a) => ({ ...a, [id]: v }));
    if (missing === id) setMissing(null);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const gap = firstMissing(answers);
    if (gap) {
      setMissing(gap);
      return;
    }
    setSending(true);
    setError(null);
    try {
      await surveyApi.submit(STUDENT_SURVEY_KEY, { answers, source, website: honeypot });
      setDone(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSending(false);
    }
  };

  const sendContact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (contact.trim().length < 3) return;
    setContactState("sending");
    try {
      await surveyApi.volunteer(STUDENT_SURVEY_KEY, { contact: contact.trim(), source });
      setContactState("sent");
    } catch {
      setContactState("error");
    }
  };

  if (done) {
    return (
      <div className="space-y-4">
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center dark:border-emerald-500/30 dark:bg-emerald-500/10">
          <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-600" />
          <h1 className="mt-4 text-2xl font-bold text-surface-900 dark:text-white">
            {t("Rahmat!", "Спасибо!")}
          </h1>
          <p className="mt-2 text-surface-600 dark:text-surface-300">
            {t(
              "Javobingiz talabalarga ish topishni osonlashtirishga yordam beradi. So'rovnomani kursdoshlaringizga ham yuboring.",
              "Ваш ответ поможет сделать поиск работы проще для студентов. Отправьте опрос и однокурсникам.",
            )}
          </p>
        </div>

        {/* The interview ask: the survey says what is wrong, a conversation says why. */}
        <div className="rounded-2xl border border-surface-200 bg-white p-6 dark:border-surface-700 dark:bg-surface-900">
          {contactState === "sent" ? (
            <p className="text-center text-surface-700 dark:text-surface-200">
              {t(
                "Rahmat! Yaqin kunlarda yozamiz.",
                "Спасибо! Напишем в ближайшие дни.",
              )}
            </p>
          ) : (
            <form onSubmit={sendContact}>
              <h2 className="font-semibold text-surface-900 dark:text-white">
                {t("10 daqiqa gaplashamizmi?", "Поговорим 10 минут?")}
              </h2>
              <p className="mt-1 text-sm text-surface-600 dark:text-surface-300">
                {t(
                  "Bir nechta talaba bilan batafsil suhbatlashmoqchimiz. Xohlasangiz, Telegram username yoki telefon qoldiring.",
                  "Хотим подробно поговорить с несколькими студентами. Если хотите — оставьте Telegram username или телефон.",
                )}
              </p>
              <p className="mt-1 text-xs text-surface-500">
                {t(
                  "Kontakt alohida saqlanadi va yuqoridagi javoblaringiz bilan bog'lanmaydi — javoblar anonim qoladi.",
                  "Контакт хранится отдельно и не связывается с вашими ответами — ответы остаются анонимными.",
                )}
              </p>
              <div className="mt-3 flex flex-col gap-2 sm:flex-row">
                <input
                  value={contact}
                  onChange={(e) => setContact(e.target.value)}
                  placeholder={t("@username yoki +998…", "@username или +998…")}
                  maxLength={120}
                  className="flex-1 rounded-xl border border-surface-300 bg-transparent px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none dark:border-surface-600"
                />
                <button
                  type="submit"
                  disabled={contactState === "sending" || contact.trim().length < 3}
                  className="rounded-xl bg-surface-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-surface-800 disabled:opacity-50 dark:bg-white dark:text-surface-900"
                >
                  {t("Yuborish", "Отправить")}
                </button>
              </div>
              {contactState === "error" && (
                <p className="mt-2 text-sm text-red-600">
                  {t("Yuborilmadi, qaytadan urinib ko'ring.", "Не отправилось, попробуйте ещё раз.")}
                </p>
              )}
            </form>
          )}
        </div>

        <div className="flex flex-wrap justify-center gap-3 pt-2">
          <Link
            href="/jobs"
            className="rounded-xl bg-primary-600 px-5 py-2.5 font-medium text-white hover:bg-primary-700"
          >
            {t("Vakansiyalarni ko'rish", "Смотреть вакансии")}
          </Link>
          <Link
            href="/maosh"
            className="rounded-xl border border-surface-300 px-5 py-2.5 font-medium text-surface-700 hover:bg-surface-50 dark:border-surface-600 dark:text-surface-200 dark:hover:bg-surface-800"
          >
            {t("Maoshlar statistikasi", "Статистика зарплат")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={submit} noValidate>
      <header className="mb-8">
        <div className="flex items-start justify-between gap-4">
          <p className="text-sm font-medium text-primary-600">IshTop · {t("so'rovnoma", "опрос")}</p>
          <LanguageSwitcherInline />
        </div>
        <h1 className="mt-2 text-3xl font-bold text-surface-900 dark:text-white">
          {t("Ish qidirish qanchalik qiyin?", "Насколько сложно найти работу?")}
        </h1>
        <p className="mt-3 text-surface-600 dark:text-surface-300">
          {t(
            "Talabalar va yosh mutaxassislar ish qidirishda nimaga duch kelishini o'rganyapmiz. 2 daqiqa vaqt oladi.",
            "Мы изучаем, с чем сталкиваются студенты и молодые специалисты при поиске работы. Займёт 2 минуты.",
          )}
        </p>
        <p className="mt-2 text-xs text-surface-500">
          {t(
            "Anonim: ism, telefon yoki email so'ralmaydi. Javoblar faqat umumiy statistika uchun ishlatiladi.",
            "Анонимно: имя, телефон и email не запрашиваются. Ответы используются только для общей статистики.",
          )}
        </p>
      </header>

      {/* Honeypot — off-screen, skipped by keyboard and screen readers. */}
      <div aria-hidden className="absolute -left-[9999px] h-0 w-0 overflow-hidden">
        <label>
          Website
          <input tabIndex={-1} autoComplete="off" value={honeypot} onChange={(e) => setHoneypot(e.target.value)} />
        </label>
      </div>

      <ol className="space-y-6">
        {STUDENT_SURVEY.map((q, i) => {
          const flagged = missing === q.id;
          const picked = answers[q.id];
          const multi = (picked as string[] | undefined) ?? [];
          const full = q.kind === "multi" && q.max !== undefined && multi.length >= q.max;
          return (
            <li
              key={q.id}
              id={`q-${q.id}`}
              className={`rounded-2xl border bg-white p-5 dark:bg-surface-900 ${
                flagged ? "border-red-400 ring-2 ring-red-100 dark:ring-red-500/20" : "border-surface-200 dark:border-surface-700"
              }`}
            >
              <fieldset>
                <legend className="font-semibold text-surface-900 dark:text-white">
                  {i + 1}. {q.title[lang]}
                  {q.required && <span className="ml-1 text-red-500">*</span>}
                </legend>
                {q.hint && <p className="mt-1 text-sm text-surface-500">{q.hint[lang]}</p>}

                {q.kind === "text" ? (
                  <textarea
                    className="mt-3 w-full rounded-xl border border-surface-300 bg-transparent p-3 text-sm focus:border-primary-500 focus:outline-none dark:border-surface-600"
                    rows={3}
                    maxLength={1000}
                    value={(picked as string) ?? ""}
                    onChange={(e) => set(q.id, e.target.value)}
                  />
                ) : (
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {q.options!.map((opt) => {
                      const on = q.kind === "single" ? picked === opt.id : multi.includes(opt.id);
                      const disabled = q.kind === "multi" && full && !on;
                      return (
                        <label
                          key={opt.id}
                          className={`flex cursor-pointer items-center gap-3 rounded-xl border px-3 py-2.5 text-sm transition ${
                            on
                              ? "border-primary-500 bg-primary-50 text-primary-900 dark:bg-primary-500/10 dark:text-primary-100"
                              : "border-surface-200 text-surface-700 hover:border-surface-300 dark:border-surface-700 dark:text-surface-200"
                          } ${disabled ? "cursor-not-allowed opacity-50" : ""}`}
                        >
                          <input
                            type={q.kind === "single" ? "radio" : "checkbox"}
                            name={q.id}
                            className="accent-primary-600"
                            checked={on}
                            disabled={disabled}
                            onChange={() =>
                              set(q.id, q.kind === "single" ? opt.id : toggleMulti(multi, opt.id, q.max))
                            }
                          />
                          {opt.label[lang]}
                        </label>
                      );
                    })}
                  </div>
                )}
                {flagged && (
                  <p className="mt-2 text-sm text-red-600">{t("Iltimos, javob bering", "Пожалуйста, ответьте")}</p>
                )}
              </fieldset>
            </li>
          );
        })}
      </ol>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={sending}
        className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-primary-600 px-5 py-3 font-semibold text-white hover:bg-primary-700 disabled:opacity-60"
      >
        {sending && <Loader2 className="h-4 w-4 animate-spin" />}
        {t("Yuborish", "Отправить")}
      </button>
    </form>
  );
}
