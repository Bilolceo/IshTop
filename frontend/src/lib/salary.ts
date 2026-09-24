import type { SalaryGroup } from "@/types/api";
import { categoryLabel } from "@/lib/jobCategories";

/** "6 mln", "10.8 mln" — millions read faster than "10 800 000". */
export function mln(value: number, isRu = false): string {
  const v = Math.round(value / 100_000) / 10;
  const s = Number.isInteger(v) ? String(v) : v.toFixed(1);
  return `${s} ${isRu ? "млн" : "mln"}`;
}

export function mlnRange(lo: number, hi: number, isRu = false): string {
  if (Math.round(lo / 100_000) === Math.round(hi / 100_000)) return mln(lo, isRu);
  return `${mln(lo, isRu).split(" ")[0]}–${mln(hi, isRu)}`;
}

/** A group's name in the reader's language (soha names come from the shared table). */
export function groupLabel(g: Pick<SalaryGroup, "kind" | "id" | "label" | "label_ru">, isRu: boolean): string {
  if (g.kind === "category") return categoryLabel(g.id, isRu);
  return isRu ? g.label_ru || g.label : g.label;
}

/** Above/below-median wording; within ±10% counts as "about average". */
export function diffVerdict(diff: number | null | undefined, isRu: boolean, isFloor = false) {
  if (diff === null || diff === undefined) return null;
  if (diff >= 10) {
    const atLeast = isFloor ? (isRu ? "минимум " : "kamida ") : "";
    return {
      tone: "up" as const,
      text: isRu ? `${atLeast}на ${diff}% выше среднего` : `o'rtachadan ${atLeast}${diff}% yuqori`,
    };
  }
  if (diff <= -10)
    return { tone: "down" as const, text: isRu ? `на ${-diff}% ниже среднего` : `o'rtachadan ${-diff}% past` };
  return { tone: "flat" as const, text: isRu ? "на уровне среднего" : "o'rtacha darajada" };
}
