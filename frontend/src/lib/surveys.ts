/**
 * Wording for the problem-validation survey. The question/option ids are the
 * server's (backend/app/core/surveys.py) — it rejects anything else, so keep
 * the two lists in step. Only the text lives here.
 */

export const STUDENT_SURVEY_KEY = "student-2026";

type L = { uz: string; ru: string };

export type SurveyQuestion = {
  id: string;
  kind: "single" | "multi" | "text";
  required: boolean;
  max?: number;
  title: L;
  hint?: L;
  options?: { id: string; label: L }[];
};

const o = (id: string, uz: string, ru: string) => ({ id, label: { uz, ru } });

export const STUDENT_SURVEY: SurveyQuestion[] = [
  {
    id: "status",
    kind: "single",
    required: true,
    title: { uz: "Hozir kimsiz?", ru: "Кто вы сейчас?" },
    options: [
      o("course_1_2", "1–2-kurs talabasi", "Студент 1–2 курса"),
      o("course_3_4", "3–4-kurs talabasi", "Студент 3–4 курса"),
      o("graduate_1y", "Bitirganimga 1 yil bo'lmagan", "Выпускник (до 1 года)"),
      o("working", "Ishlayapman", "Работаю"),
      o("other", "Boshqa", "Другое"),
    ],
  },
  {
    id: "searched",
    kind: "single",
    required: true,
    title: {
      uz: "Oxirgi 6 oyda ish yoki amaliyot qidirdingizmi?",
      ru: "Искали ли вы работу или стажировку за последние 6 месяцев?",
    },
    options: [
      o("yes_found", "Ha, topdim", "Да, нашёл(а)"),
      o("yes_searching", "Ha, hali qidiryapman", "Да, всё ещё ищу"),
      o("no_plan", "Yo'q, lekin yaqinda boshlayman", "Нет, но скоро начну"),
      o("no", "Yo'q", "Нет"),
    ],
  },
  {
    id: "pains",
    kind: "multi",
    required: true,
    max: 3,
    title: {
      uz: "Ish qidirishda eng katta qiyinchilik nima?",
      ru: "Что сложнее всего в поиске работы?",
    },
    hint: { uz: "3 tagacha tanlang", ru: "Выберите до 3" },
    options: [
      o("experience_required", "Tajriba talab qilishadi", "Требуют опыт"),
      o("hard_to_find", "Menga mos vakansiya topish qiyin", "Сложно найти подходящую вакансию"),
      o("scams", "Firibgar / soxta e'lonlar", "Мошеннические / фейковые объявления"),
      o("resume", "Rezyume yozishni bilmayman", "Не умею писать резюме"),
      o("no_reply", "Ish beruvchi javob bermaydi", "Работодатель не отвечает"),
      o("salary_unknown", "Maosh yozilmagan", "Не указана зарплата"),
      o("interview_prep", "Suhbatga tayyorlanish", "Подготовка к собеседованию"),
      o("other", "Boshqa", "Другое"),
    ],
  },
  {
    id: "channels",
    kind: "multi",
    required: true,
    title: { uz: "Ishni qayerdan qidirasiz?", ru: "Где вы ищете работу?" },
    hint: { uz: "Bir nechtasini tanlash mumkin", ru: "Можно выбрать несколько" },
    options: [
      o("telegram", "Telegram kanallar", "Telegram-каналы"),
      o("hh", "hh.uz", "hh.uz"),
      o("olx", "OLX", "OLX"),
      o("friends", "Tanishlar orqali", "Через знакомых"),
      o("linkedin", "LinkedIn", "LinkedIn"),
      o("university", "Universitet", "Университет"),
      o("other", "Boshqa", "Другое"),
    ],
  },
  {
    id: "time_to_job",
    kind: "single",
    required: false,
    title: {
      uz: "Oxirgi ishingizni topish qancha vaqt oldi?",
      ru: "Сколько времени занял поиск последней работы?",
    },
    options: [
      o("lt_1m", "1 oydan kam", "Меньше месяца"),
      o("m1_3", "1–3 oy", "1–3 месяца"),
      o("m3_6", "3–6 oy", "3–6 месяцев"),
      o("gt_6m", "6 oydan ko'p", "Больше 6 месяцев"),
      o("not_yet", "Hali topmadim", "Ещё не нашёл(а)"),
    ],
  },
  {
    id: "pay",
    kind: "single",
    required: true,
    title: {
      uz: "Tezroq ish topishga yordam beradigan xizmat uchun oyiga qancha to'lagan bo'lardingiz?",
      ru: "Сколько в месяц вы заплатили бы за сервис, который помогает быстрее найти работу?",
    },
    options: [
      o("no", "To'lamagan bo'lardim", "Не стал(а) бы платить"),
      o("k10_20", "10–20 ming so'm", "10–20 тыс. сум"),
      o("k20_50", "20–50 ming so'm", "20–50 тыс. сум"),
      o("k50_plus", "50 ming so'mdan ko'p", "Больше 50 тыс. сум"),
    ],
  },
  {
    id: "comment",
    kind: "text",
    required: false,
    title: {
      uz: "Ish qidirishda nima eng ko'p asabingizga tegadi? (ixtiyoriy)",
      ru: "Что больше всего раздражает в поиске работы? (необязательно)",
    },
  },
];

export type SurveyAnswers = Record<string, string | string[]>;

/** First required question left unanswered, or null when the form is complete. */
export function firstMissing(answers: SurveyAnswers, questions = STUDENT_SURVEY): string | null {
  for (const q of questions) {
    if (!q.required) continue;
    const v = answers[q.id];
    if (v === undefined || v === "" || (Array.isArray(v) && v.length === 0)) return q.id;
  }
  return null;
}

/** Toggle an option in a multi question, refusing to go past `max`. */
export function toggleMulti(current: string[] | undefined, id: string, max?: number): string[] {
  const list = current ?? [];
  if (list.includes(id)) return list.filter((x) => x !== id);
  if (max && list.length >= max) return list;
  return [...list, id];
}
