import Link from "next/link";

import { fetchSalaryStats } from "@/lib/discovery-api";
import { groupLabel, mln, mlnRange } from "@/lib/salary";
import { JobAlertCta } from "@/components/jobs/JobAlertCta";
import type { SalaryGroup, SalaryStats } from "@/types/api";

export const revalidate = 600;

export const metadata = {
  title: "O'zbekistonda maoshlar — kasb, soha va shahar bo'yicha | IshTop",
  description:
    "Sotuv menejeri, operator, dasturchi, buxgalter va boshqa kasblarga O'zbekistonda qancha to'lashadi — IshTop'dagi faol vakansiyalar asosida o'rtacha maosh va oraliq.",
  alternates: { canonical: "/maosh" },
};

function Table({ title, intro, rows }: { title: string; intro: string; rows: SalaryGroup[] }) {
  if (!rows.length) return null;
  const top = Math.max(...rows.map((r) => r.p75));
  const pct = (v: number) => `${Math.min(100, (v / top) * 100)}%`;
  return (
    <section className="mb-10">
      <h2 className="text-xl font-bold text-surface-900 dark:text-white">{title}</h2>
      <p className="mt-1 text-sm text-surface-500">{intro}</p>
      <div className="mt-4 divide-y divide-surface-100 overflow-hidden rounded-2xl border border-surface-200 bg-white dark:divide-surface-800 dark:border-surface-700 dark:bg-surface-900">
        {rows.map((r) => (
          <div key={`${r.kind}-${r.id}`} className="grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-2 px-4 py-3 sm:grid-cols-[minmax(0,14rem)_1fr_auto]">
            <div className="min-w-0">
              <p className="truncate font-medium text-surface-900 dark:text-white">{groupLabel(r, false)}</p>
              <p className="text-xs text-surface-500">
                {r.count} ta vakansiya{r.count < 5 ? " · kam ma'lumot" : ""}
              </p>
            </div>
            {/* Middle half of the market as a band, the median as a tick. */}
            <div className="relative order-3 col-span-2 h-2 rounded-full bg-surface-100 dark:bg-surface-800 sm:order-none sm:col-span-1" aria-hidden>
              <div
                className="absolute inset-y-0 rounded-full bg-emerald-200 dark:bg-emerald-500/30"
                style={{ left: pct(r.p25), width: `calc(${pct(r.p75)} - ${pct(r.p25)})` }}
              />
              <div className="absolute -top-1 h-4 w-0.5 rounded bg-emerald-600 dark:bg-emerald-400" style={{ left: pct(r.median) }} />
            </div>
            <div className="text-right">
              <p className="font-bold text-surface-900 dark:text-white">{mln(r.median)}</p>
              <p className="text-xs text-surface-500">{mlnRange(r.p25, r.p75)}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default async function SalariesPage() {
  let stats: SalaryStats | null = null;
  try {
    stats = await fetchSalaryStats();
  } catch {
    stats = null;
  }
  const o = stats?.overall;
  const updated = stats ? new Date(stats.computed_at).toLocaleDateString("uz-UZ", { day: "numeric", month: "long", year: "numeric" }) : "";

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <header className="mb-8">
        <p className="text-sm text-surface-500">Maosh statistikasi</p>
        <h1 className="mt-2 text-3xl font-bold text-surface-900 dark:text-white">
          O'zbekistonda qancha to'lashadi?
        </h1>
        {o ? (
          <p className="mt-3 max-w-3xl text-surface-600 dark:text-surface-300">
            IshTop'dagi {o.total} ta faol vakansiyaning {o.count} tasida maosh ochiq yozilgan. Ularning
            o'rtachasi (mediana) — <strong className="text-surface-900 dark:text-white">{mln(o.median)} so'm</strong>,
            ko'pchiligi {mlnRange(o.p25, o.p75)} so'm oralig'ida. Quyida — har bir kasb, soha va shahar bo'yicha.
          </p>
        ) : (
          <p className="mt-3 text-surface-600 dark:text-surface-300">
            Statistika hozir yuklanmadi — birozdan so'ng qayta urinib ko'ring.
          </p>
        )}
        {updated && <p className="mt-2 text-xs text-surface-400">Yangilangan: {updated}</p>}
      </header>

      {stats && (
        <>
          <Table
            title="Kasblar bo'yicha"
            intro="Katta raqam — o'rtacha (mediana) oylik; ostida — vakansiyalarning ko'pchiligi to'laydigan oraliq."
            rows={stats.roles}
          />
          <Table title="Sohalar bo'yicha" intro="Bir soha ichida kasblar orasidagi farq katta bo'lishi mumkin — aniqroq raqam uchun kasblar jadvaliga qarang." rows={stats.categories} />
          <Table title="Shaharlar bo'yicha" intro="Vakansiyalarning ko'pchiligi Toshkentda; boshqa shaharlar uchun ma'lumot hozircha kam." rows={stats.cities} />
        </>
      )}

      <div className="mb-10">
        <JobAlertCta />
      </div>

      <section className="rounded-2xl border border-surface-200 bg-surface-50 p-5 text-sm text-surface-600 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-300">
        <h2 className="font-semibold text-surface-900 dark:text-white">Raqamlar qanday hisoblanadi</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Faqat hozir faol, maoshi ochiq yozilgan vakansiyalar; ish beruvchi yashirgan maosh hisobga olinmaydi.</li>
          <li>Oraliq berilgan bo'lsa ("6–8 mln") — o'rtasi; faqat pastki chegara bo'lsa ("5 mln dan") — o'sha chegara.</li>
          <li>O'rtacha arifmetik emas, mediana: bitta juda katta maosh raqamni buzmaydi.</li>
          <li>Faqat so'mda; 1 mln so'mdan kami (kunlik yoki smenali stavka) hisobga olinmaydi.</li>
          <li>"O'rtachadan yuqori/past" faqat o'sha kasbning kamida 5 ta vakansiyasi bilan solishtirib aytiladi. Soha ichida kasblar aralash (kassir va sotuv menejeri), shuning uchun soha bo'yicha faqat odatiy raqam ko'rsatiladi.</li>
          <li>"5 mln dan" kabi pastki chegara maosh o'rtachadan past deb baholanmaydi — ish beruvchi ko'proq to'lashi mumkin.</li>
        </ul>
        <Link href="/register" className="mt-4 inline-block font-medium text-brand-600 hover:underline dark:text-brand-400">
          Vakansiyalarni ko'rish va ariza berish →
        </Link>
      </section>
    </main>
  );
}
