/**
 * A listing's text in the reader's language.
 *
 * The job's own fields are the text as written (Uzbek for imports);
 * `translations.<locale>` holds the other-language version (backend
 * jobs.translations). Switching the site to Russian used to
 * leave every description, requirement and title in whatever language the
 * post was written in. Any field the translation lacks falls back to Uzbek, so
 * a half-translated listing still reads whole.
 */

import type { Job } from "@/types/api";

type TextFields = Pick<Job, "title" | "description" | "requirements" | "responsibilities" | "benefits">;
type WithTranslations = { translations?: Record<string, Partial<TextFields>> | null };

/** Works on any job-shaped object (full Job, or the slimmer shapes some pages use). */
export function localizeJob<T>(job: T, locale: string): T {
  // Any locale can have a version: imports are written in Uzbek and carry
  // `ru`, but a company may post in Russian and get an `uz` version instead.
  if (!job) return job;
  const tr = (job as unknown as WithTranslations).translations?.[locale];
  if (!tr) return job;
  const out = { ...(job as object) } as Record<string, unknown>;
  if (tr.title) out.title = tr.title;
  if (tr.description) out.description = tr.description;
  for (const k of ["requirements", "responsibilities", "benefits"] as const) {
    const v = tr[k];
    if (Array.isArray(v) && v.length) out[k] = v;
  }
  return out as T;
}
