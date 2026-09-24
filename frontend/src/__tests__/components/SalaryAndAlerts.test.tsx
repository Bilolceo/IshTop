/**
 * The salary and job-alert UI (2026-09-24). These screens sit behind a login,
 * so they are verified here rather than in a browser.
 */

import { render, screen, fireEvent } from "@testing-library/react";
import { SalaryInsight } from "@/components/jobs/SalaryInsight";
import { JobAlertCta } from "@/components/jobs/JobAlertCta";
import { JobCard } from "@/components/jobs/JobCard";
import { mln, mlnRange, diffVerdict, groupLabel } from "@/lib/salary";
import { jobAlertBotLink } from "@/lib/jobAlerts";
import type { Job, SalaryInsight as Insight } from "@/types/api";

jest.mock("framer-motion", () => ({
  motion: { div: ({ children, initial, animate, transition, ...rest }: any) => <div {...rest}>{children}</div> },
}));
jest.mock("next/link", () => ({ __esModule: true, default: ({ href, children, ...r }: any) => <a href={href} {...r}>{children}</a> }));
jest.mock("@/hooks/useTranslation", () => ({ useTranslation: () => ({ locale: "uz", t: (k: string) => k }) }));

const base: Insight = {
  kind: "role", id: "Sotuv menejeri", label: "Sotuv menejeri", label_ru: "Менеджер по продажам",
  count: 32, total: 39, median: 10_800_000, p25: 6_700_000, p75: 14_500_000,
  min: 4_800_000, max: 20_000_000, job_value: null, diff_pct: null,
};

describe("salary helpers", () => {
  it("formats millions", () => {
    expect(mln(10_800_000)).toBe("10.8 mln");
    expect(mln(6_000_000)).toBe("6 mln");
    expect(mln(6_000_000, true)).toBe("6 млн");
    expect(mlnRange(6_700_000, 14_500_000)).toBe("6.7–14.5 mln");
    expect(mlnRange(5_000_000, 5_000_000)).toBe("5 mln");
  });

  it("words the verdict, and 'at least' for a floor", () => {
    expect(diffVerdict(30, false)?.text).toBe("o'rtachadan 30% yuqori");
    expect(diffVerdict(30, false, true)?.text).toBe("o'rtachadan kamida 30% yuqori");
    expect(diffVerdict(-20, false)?.tone).toBe("down");
    expect(diffVerdict(5, false)?.tone).toBe("flat");
    expect(diffVerdict(null, false)).toBeNull();
  });

  it("labels a soha from the shared table, not the backend string", () => {
    expect(groupLabel({ kind: "category", id: "it", label: "x", label_ru: "y" }, false)).toContain("IT");
    expect(groupLabel({ kind: "role", id: "a", label: "Sotuvchi", label_ru: "Продавец" }, true)).toBe("Продавец");
  });
});

describe("SalaryInsight", () => {
  it("tells a hidden-pay listing what to expect", () => {
    render(<SalaryInsight insight={base} isRu={false} />);
    expect(screen.getByText(/10.8 mln/)).toBeInTheDocument();
    expect(screen.getByText(/Ish beruvchi maoshni ko'rsatmagan/)).toBeInTheDocument();
    expect(screen.getByText(/6.7–14.5 mln so'm atrofini/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Barcha kasblar/ })).toHaveAttribute("href", "/maosh");
  });

  it("says above average for a well-paid listing", () => {
    render(<SalaryInsight insight={{ ...base, job_value: 14_000_000, diff_pct: 30 }} isRu={false} />);
    expect(screen.getByText(/Bu vakansiya: 14 mln — o'rtachadan 30% yuqori/)).toBeInTheDocument();
  });

  it("never lets a floor read as the pay itself", () => {
    render(<SalaryInsight insight={{ ...base, job_value: 8_000_000, job_is_floor: true, diff_pct: null }} isRu={false} />);
    expect(screen.getByText(/Bu vakansiya: 8 mln dan/)).toBeInTheDocument();
    expect(screen.queryByText(/past/)).not.toBeInTheDocument();
  });

  it("gives no verdict against a whole soha", () => {
    render(<SalaryInsight insight={{ ...base, kind: "category", id: "sales", job_value: 4_000_000, diff_pct: null }} isRu={false} />);
    expect(screen.getByText(/aniq solishtirmaymiz/)).toBeInTheDocument();
  });

  it("renders in Russian", () => {
    render(<SalaryInsight insight={{ ...base, job_value: 9_000_000, job_is_ceiling: true, diff_pct: -17 }} isRu />);
    expect(screen.getByText(/Эта вакансия: до 9 млн — на 17% ниже среднего/)).toBeInTheDocument();
  });
});

describe("JobAlertCta", () => {
  beforeEach(() => window.localStorage.clear());

  it("opens the bot's alerts, or a city directly when the page knows it", () => {
    expect(jobAlertBotLink()).toBe("https://t.me/ishtop_ariza_bot?start=alerts");
    expect(jobAlertBotLink({ city: "toshkent" })).toBe("https://t.me/ishtop_ariza_bot?start=alert_t_toshkent");
    expect(jobAlertBotLink({ city: "unknown-place" })).toBe("https://t.me/ishtop_ariza_bot?start=alerts");
    render(<JobAlertCta city="samarqand" />);
    expect(screen.getByRole("link", { name: /Xabarnomani yoqish/ })).toHaveAttribute(
      "href", "https://t.me/ishtop_ariza_bot?start=alert_t_samarqand");
  });

  it("stays closed once dismissed", () => {
    const { unmount } = render(<JobAlertCta storageKey="k" />);
    fireEvent.click(screen.getByLabelText("Yopish"));
    expect(screen.queryByText(/birinchi bo'lib biling/)).not.toBeInTheDocument();
    unmount();
    render(<JobAlertCta storageKey="k" />);
    expect(screen.queryByText(/birinchi bo'lib biling/)).not.toBeInTheDocument();
  });
});

describe("JobCard salary line", () => {
  const job = (over: Partial<Job>): Job =>
    ({
      id: "1", title: "Sotuv menejeri", company: { name: "Acme" }, location: "Toshkent",
      job_type: "full_time", created_at: new Date().toISOString(), salary_currency: "UZS",
      salary_min: null, salary_max: null, ...over,
    }) as unknown as Job;
  const card = (j: Job) =>
    render(<JobCard job={j} isSelected={false} isSaved={false} onSelect={() => {}} onToggleSave={() => {}} onQuickApply={() => {}} />);

  it("marks pay that beats the kasb median", () => {
    card(job({ salary_min: 14_000_000, salary_max: 14_000_000, salary_insight: { ...base, job_value: 14_000_000, diff_pct: 30 } }));
    expect(screen.getAllByText(/o'rtachadan 30% yuqori/).length).toBeGreaterThan(0);
  });

  it("does not shame pay below the median on a list row", () => {
    card(job({ salary_min: 7_000_000, salary_max: 7_000_000, salary_insight: { ...base, job_value: 7_000_000, diff_pct: -35 } }));
    expect(screen.queryByText(/past/)).not.toBeInTheDocument();
  });

  it("shows the typical figure where the employer hid the pay", () => {
    card(job({ salary_insight: base }));
    expect(screen.getByText(/odatda ~10.8 mln/)).toBeInTheDocument();
  });

  it("still renders without any insight", () => {
    card(job({}));
    expect(screen.getByText(/Maosh ko'rsatilmagan/)).toBeInTheDocument();
  });
});
