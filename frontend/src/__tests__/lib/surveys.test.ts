import fs from "fs";
import path from "path";

import { STUDENT_SURVEY, firstMissing, toggleMulti } from "@/lib/surveys";

describe("student survey", () => {
  it("uses exactly the question and option ids the server accepts", () => {
    // The server rejects any id it doesn't know; drift here means 422s in prod.
    const py = fs.readFileSync(
      path.join(__dirname, "../../../../backend/app/core/surveys.py"),
      "utf8",
    );
    for (const q of STUDENT_SURVEY) {
      const block = py.match(new RegExp(`\\{"id": "${q.id}", "kind": "${q.kind}"[\\s\\S]*?\\}(?=,\\n)`));
      expect(block).not.toBeNull();
      const serverOpts = [...(block![0].match(/"options": \[([\s\S]*?)\]/)?.[1] ?? "").matchAll(/"([a-z0-9_]+)"/g)].map((m) => m[1]);
      expect((q.options ?? []).map((o) => o.id)).toEqual(serverOpts);
      expect(block![0].includes('"required": True')).toBe(q.required);
    }
  });

  it("points at the first unanswered required question", () => {
    expect(firstMissing({})).toBe("status");
    expect(firstMissing({ status: "working", searched: "no", pains: [] })).toBe("pains");
    expect(
      firstMissing({ status: "working", searched: "no", pains: ["scams"], channels: ["hh"], pay: "no" }),
    ).toBeNull();
  });

  it("caps multi picks at max and toggles off", () => {
    expect(toggleMulti(["a", "b", "c"], "d", 3)).toEqual(["a", "b", "c"]);
    expect(toggleMulti(["a", "b"], "a", 3)).toEqual(["b"]);
    expect(toggleMulti(undefined, "a")).toEqual(["a"]);
  });
});
