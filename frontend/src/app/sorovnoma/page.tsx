import { SurveyForm } from "@/components/survey/SurveyForm";

export const metadata = {
  title: "Ish qidirish qanchalik qiyin? — 2 daqiqalik so'rovnoma",
  description:
    "Talabalar va yosh mutaxassislar ish qidirishda nimaga duch kelishini o'rganyapmiz. Anonim, 2 daqiqa.",
  alternates: { canonical: "/sorovnoma" },
  robots: { index: false },
};

export default function SurveyPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <SurveyForm />
    </main>
  );
}
