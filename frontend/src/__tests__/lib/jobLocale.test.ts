import { localizeJob } from "@/lib/jobLocale";

const job = {
  id: "1", title: "Sotuv menejeri", description: "O'zbekcha tavsif",
  requirements: ["Tajriba"], responsibilities: [], benefits: ["Tushlik"],
  translations: { ru: { title: "Менеджер по продажам", description: "Русское описание", requirements: ["Опыт"], benefits: [] } },
};

describe("localizeJob", () => {
  it("keeps the Uzbek text for uz", () => {
    expect(localizeJob(job, "uz")).toBe(job);
  });
  it("switches every text field for ru", () => {
    const ru = localizeJob(job, "ru");
    expect(ru.title).toBe("Менеджер по продажам");
    expect(ru.description).toBe("Русское описание");
    expect(ru.requirements).toEqual(["Опыт"]);
  });
  it("falls back to Uzbek for a field the translation lacks", () => {
    expect(localizeJob(job, "ru").benefits).toEqual(["Tushlik"]);
  });
  it("is a no-op without translations or for null", () => {
    const plain = { ...job, translations: null };
    expect(localizeJob(plain, "ru")).toBe(plain);
    expect(localizeJob(null, "ru")).toBeNull();
  });
});
