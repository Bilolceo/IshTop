"""
=============================================================================
SURVEY DEFINITIONS
=============================================================================

Problem-validation surveys, defined in code so the server can reject any
answer that is not one of the offered options — the results are only worth
quoting if every row means exactly what the question asked.

Option ids are stable machine keys; the UI owns the uz/ru wording. Never
rename an id once responses exist — add a new one instead.
=============================================================================
"""

from typing import Any, Dict, List, Optional

# kind: "single" = one option id, "multi" = list of option ids, "text" = free text
SURVEYS: Dict[str, Dict[str, Any]] = {
    "student-2026": {
        "questions": [
            {"id": "status", "kind": "single", "required": True,
             "options": ["course_1_2", "course_3_4", "graduate_1y", "working", "other"]},
            {"id": "searched", "kind": "single", "required": True,
             "options": ["yes_found", "yes_searching", "no_plan", "no"]},
            {"id": "pains", "kind": "multi", "required": True, "max": 3,
             "options": ["experience_required", "hard_to_find", "scams", "resume",
                         "no_reply", "salary_unknown", "interview_prep", "other"]},
            {"id": "channels", "kind": "multi", "required": True,
             "options": ["telegram", "hh", "olx", "friends", "linkedin",
                         "university", "other"]},
            {"id": "time_to_job", "kind": "single", "required": False,
             "options": ["lt_1m", "m1_3", "m3_6", "gt_6m", "not_yet"]},
            {"id": "pay", "kind": "single", "required": True,
             "options": ["no", "k10_20", "k20_50", "k50_plus"]},
            {"id": "comment", "kind": "text", "required": False, "max_len": 1000},
        ],
    },
}

SOURCE_MAX_LEN = 40


def get_survey(key: str) -> Optional[Dict[str, Any]]:
    return SURVEYS.get(key)


def validate_answers(survey: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
    """Return the cleaned answers, or raise ValueError naming the first bad field.

    Unknown keys are dropped rather than stored, so a tampered client can't
    park arbitrary JSON in the table.
    """
    if not isinstance(answers, dict):
        raise ValueError("answers must be an object")

    clean: Dict[str, Any] = {}
    for q in survey["questions"]:
        qid, kind = q["id"], q["kind"]
        value = answers.get(qid)
        empty = value is None or value == "" or value == []
        if empty:
            if q.get("required"):
                raise ValueError(f"{qid}: required")
            continue

        if kind == "single":
            if value not in q["options"]:
                raise ValueError(f"{qid}: unknown option")
            clean[qid] = value
        elif kind == "multi":
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise ValueError(f"{qid}: must be a list")
            picked: List[str] = list(dict.fromkeys(value))  # dedupe, keep order
            if any(v not in q["options"] for v in picked):
                raise ValueError(f"{qid}: unknown option")
            if len(picked) > q.get("max", len(q["options"])):
                raise ValueError(f"{qid}: too many options")
            clean[qid] = picked
        else:  # text
            if not isinstance(value, str):
                raise ValueError(f"{qid}: must be text")
            text = value.strip()[: q.get("max_len", 1000)]
            if text:
                clean[qid] = text
    return clean


def summarize(survey: Dict[str, Any], rows: List[Dict[str, Any]], text_limit: int = 100) -> Dict[str, Any]:
    """Per-option counts over `rows` (each a cleaned answers dict).

    For multi questions the percentages are of respondents, so they can sum
    past 100% — that is the honest reading of "pick up to three".
    """
    total = len(rows)
    questions = []
    for q in survey["questions"]:
        qid, kind = q["id"], q["kind"]
        if kind == "text":
            texts = [r[qid] for r in rows if r.get(qid)]
            questions.append({"id": qid, "kind": kind, "answered": len(texts),
                              "texts": texts[:text_limit]})
            continue
        counts = {opt: 0 for opt in q["options"]}
        answered = 0
        for r in rows:
            v = r.get(qid)
            if v is None:
                continue
            answered += 1
            for opt in (v if isinstance(v, list) else [v]):
                if opt in counts:
                    counts[opt] += 1
        questions.append({
            "id": qid, "kind": kind, "answered": answered,
            "options": [
                {"id": opt, "count": c,
                 "pct": round(100 * c / answered, 1) if answered else 0.0}
                for opt, c in counts.items()
            ],
        })
    return {"total": total, "questions": questions}
