/**
 * The survey form's interview ask and the admin traction page (2026-09-25).
 * The admin page sits behind a login, so it is verified here, not in a browser.
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import { SurveyForm } from "@/components/survey/SurveyForm";
import AdminMetricsPage from "@/app/(dashboard)/admin/metrics/page";

jest.mock("next/link", () => ({
  __esModule: true,
  default: ({ href, children, ...r }: any) => <a href={href} {...r}>{children}</a>,
}));
jest.mock("@/hooks/useTranslation", () => ({ useTranslation: () => ({ locale: "uz", t: (k: string) => k }) }));
jest.mock("@/components/ui/language-switcher", () => ({ LanguageSwitcherInline: () => null }));

const submit = jest.fn().mockResolvedValue({ data: { success: true } });
const volunteer = jest.fn().mockResolvedValue({ data: { success: true } });

jest.mock("@/lib/api", () => ({
  __esModule: true,
  default: { get: jest.fn() },
  getErrorMessage: () => "xato",
  surveyApi: {
    submit: (...a: unknown[]) => submit(...a),
    volunteer: (...a: unknown[]) => volunteer(...a),
    status: jest.fn().mockResolvedValue({ data: { data: { answered: false } } }),
    summary: jest.fn().mockResolvedValue({
      data: {
        data: {
          total: 3, signed_in: 1, distinct_ips: 3, sources: { tatu: 2, direct: 1 },
          first_at: null, last_at: null,
          questions: [
            { id: "status", kind: "single", answered: 3,
              options: [{ id: "course_3_4", count: 2, pct: 66.7 }, { id: "working", count: 1, pct: 33.3 }] },
            { id: "comment", kind: "text", answered: 1, texts: ["tajriba so'rashadi"] },
          ],
        },
      },
    }),
    leads: jest.fn().mockResolvedValue({
      data: { data: { total: 1, leads: [{ id: "1", contact: "@ali", source: "tatu", status: "new", created_at: "2026-09-25T10:00:00Z" }] } },
    }),
    traction: jest.fn().mockResolvedValue({
      data: {
        data: {
          generated_at: "2026-09-25T10:00:00Z",
          excluded_markers: ["test", "demo"],
          excluded: { students: 11, applications: 12 },
          students: { total: 189, active_7d: 9, active_30d: 24, telegram_linked: 14 },
          funnel: [
            { step: "signed_up", value: 189, pct: 100 },
            { step: "hired", value: 0, pct: 0 },
          ],
          applications: { total: 8, by_status: { pending: 8 } },
          employers: { companies: 3, live_jobs: 40, live_jobs_posted_by_companies: 2, live_jobs_imported: 38 },
          engagement: { job_alerts_active: 5, job_alert_chats: 4, survey_responses: 3 },
          weekly: { signups: [{ week: "2026-09-21", value: 4 }], applications: [{ week: "2026-09-21", value: 1 }] },
        },
      },
    }),
    exportUrl: (k: string) => `/surveys/${k}/export`,
  },
}));

// jsdom has no layout, so the form's "scroll to the unanswered question" is a no-op here.
beforeAll(() => {
  Element.prototype.scrollIntoView = jest.fn();
  window.scrollTo = jest.fn();
});

function answerEverything() {
  // Required: status, searched, pains, channels, pay.
  fireEvent.click(screen.getByLabelText(/3–4-kurs talabasi/));
  fireEvent.click(screen.getByLabelText(/Ha, hali qidiryapman/));
  fireEvent.click(screen.getByLabelText(/Tajriba talab qilishadi/));
  fireEvent.click(screen.getByLabelText(/Telegram kanallar/));
  fireEvent.click(screen.getByLabelText(/To'lamagan bo'lardim/));
}

describe("survey form", () => {
  beforeEach(() => jest.clearAllMocks());

  it("will not submit until every required question is answered", () => {
    render(<SurveyForm />);
    fireEvent.click(screen.getByRole("button", { name: /Yuborish/ }));
    expect(submit).not.toHaveBeenCalled();
    expect(screen.getAllByText(/Iltimos, javob bering/).length).toBe(1);
  });

  it("asks for an interview contact after thanking, and keeps answers unlinked", async () => {
    render(<SurveyForm />);
    answerEverything();
    fireEvent.click(screen.getByRole("button", { name: /Yuborish/ }));

    await screen.findByText("Rahmat!");
    const [, body] = submit.mock.calls[0] as [string, Record<string, unknown>];
    // the contact is never part of the answers payload
    expect(Object.keys(body.answers as object)).not.toContain("contact");

    expect(screen.getByText(/10 daqiqa gaplashamizmi/)).toBeInTheDocument();
    fireEvent.change(screen.getByPlaceholderText(/@username/), { target: { value: " @ali " } });
    fireEvent.click(screen.getAllByRole("button", { name: /Yuborish/ })[0]);

    await waitFor(() => expect(volunteer).toHaveBeenCalledWith("student-2026", { contact: "@ali", source: null }));
    expect(await screen.findByText(/Yaqin kunlarda yozamiz/)).toBeInTheDocument();
  });

  it("does not send a contact that is too short", async () => {
    render(<SurveyForm />);
    answerEverything();
    fireEvent.click(screen.getByRole("button", { name: /Yuborish/ }));
    await screen.findByText("Rahmat!");
    fireEvent.change(screen.getByPlaceholderText(/@username/), { target: { value: "@" } });
    fireEvent.click(screen.getAllByRole("button", { name: /Yuborish/ })[0]);
    expect(volunteer).not.toHaveBeenCalled();
  });
});

describe("admin traction page", () => {
  it("shows the real numbers, proves the filter, and lists interview volunteers", async () => {
    render(<AdminMetricsPage />);

    // 189 shows twice: the stat tile and the top of the funnel.
    expect((await screen.findAllByText("189")).length).toBe(2);
    expect(screen.getByText("Talabalar")).toBeInTheDocument();
    // the claim "test accounts excluded" is backed by how many were removed
    expect(screen.getByText(/11 test\/demo\/xodim akkaunti · 12 ariza/)).toBeInTheDocument();
    expect(screen.getByText(/test, demo/)).toBeInTheDocument();
    // employer-posted vs imported jobs are not conflated
    expect(screen.getByText(/kompaniyalardan: 2/)).toBeInTheDocument();
    expect(screen.getByText("@ali")).toBeInTheDocument();
    expect(screen.getByText("tajriba so'rashadi")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /CSV/ })).toBeEnabled();
  });
});
