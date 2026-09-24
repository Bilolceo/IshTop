"""
=============================================================================
SALARY STATISTICS — "bu kasbga o'rtacha qancha to'lashadi"
=============================================================================

Medians over the live listings, grouped three ways: kasb (canonical role from
the title), soha (classify_job) and city (classify_city).

What a listing contributes — decided against the real rows, 2026-09-24:
  * a range contributes its midpoint; a bare floor ("5 mln dan", 94 of 257
    rows) contributes the floor, which leans the median slightly low rather
    than inventing a ceiling nobody offered;
  * so'm only — one USD listing is not a USD market;
  * under 1 mln so'm is a daily or shift wage written without saying so (a
    cook at 350 000), and would drag a monthly median down; over 100 mln is a
    typo. Both are left out;
  * a salary the employer marked hidden stays out even of the aggregate.

Medians, not means: one 25 mln listing moves a mean of twelve by 1.5 mln.

A job is compared only against a group of at least MIN_COMPARE listings, most
specific first (kasb, then soha). A smaller group can be listed on the
statistics page with its count, but "20% above average" from three listings
would be noise presented as fact.

Computed in-process and cached for CACHE_TTL: ~340 rows is a few ms of work,
and a salary median does not change minute to minute.
=============================================================================
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.job_categories import category_meta, city_meta, classify_city, classify_job
from app.core.job_roles import canonical_role, role_label_ru

logger = logging.getLogger(__name__)

MIN_COMPARE = 5     # listings a group needs before a job is compared with it
MIN_LIST = 3        # listings a group needs to appear on the statistics page
MIN_MONTHLY = 1_000_000
MAX_MONTHLY = 100_000_000
CACHE_TTL = 600.0

_lock = threading.Lock()
_cache: dict = {"ts": 0.0, "data": None}


@dataclass
class Group:
    kind: str       # role | category | city | all
    id: str
    label_uz: str
    label_ru: str
    values: list
    total: int = 0  # listings in the group, with or without a salary

    def summary(self) -> dict:
        v = sorted(self.values)
        q1, med, q3 = _quartiles(v)
        return {
            "kind": self.kind, "id": self.id,
            "label": self.label_uz, "label_ru": self.label_ru,
            "count": len(v), "total": self.total,
            "median": med, "p25": q1, "p75": q3,
            "min": _round(v[0]), "max": _round(v[-1]),
        }


def _quartiles(v: list) -> tuple[int, int, int]:
    if len(v) == 1:
        return _round(v[0]), _round(v[0]), _round(v[0])
    q = statistics.quantiles(v, n=4, method="inclusive")
    return _round(q[0]), _round(statistics.median(v)), _round(q[2])


def _round(x: float) -> int:
    # 100 000 so'm steps: "6.25 mln" is precision the data does not have.
    return int(round(x / 100_000) * 100_000)


def monthly_value(salary_min, salary_max, currency, visible=True) -> float | None:
    """The single figure a listing contributes, or None when it contributes none."""
    if visible is False or (currency or "UZS") != "UZS":
        return None
    lo, hi = salary_min, salary_max
    if lo is None and hi is None:
        return None
    lo = float(lo if lo is not None else hi)
    hi = float(hi if hi is not None else lo)
    if hi < lo:
        lo, hi = hi, lo
    value = (lo + hi) / 2
    if value < MIN_MONTHLY or value > MAX_MONTHLY:
        return None
    return value


def _job_keys(title: str, description: str, location: str) -> tuple[str, str, str]:
    # Same category formula as job_to_response, so the soha a card shows is
    # the soha its salary is compared within.
    return (
        canonical_role(title or ""),
        classify_job(title or "", (description or "")[:200]),
        classify_city(location or ""),
    )


def _load(db) -> dict:
    from app.models.job import Job, visible_job_filters

    rows = (
        db.query(Job.title, Job.description, Job.location, Job.salary_min,
                 Job.salary_max, Job.salary_currency, Job.is_salary_visible)
        .filter(*visible_job_filters())
        .all()
    )
    groups: dict[tuple[str, str], Group] = {}
    overall = Group("all", "all", "Barcha vakansiyalar", "Все вакансии", [])

    def group(kind: str, gid: str) -> Group:
        key = (kind, gid)
        if key not in groups:
            if kind == "role":
                uz, ru = gid, role_label_ru(gid)
            elif kind == "category":
                meta = category_meta(gid)
                uz, ru = meta["label"], meta.get("label_ru", meta["label"])
            else:
                meta = city_meta(gid)
                uz, ru = meta["label"], meta.get("label_ru", meta["label"])
            groups[key] = Group(kind, gid, uz, ru, [])
        return groups[key]

    for r in rows:
        role, cid, city = _job_keys(r.title, r.description, r.location)
        members = [group("category", cid), group("city", city)]
        if role:
            members.append(group("role", role))
        value = monthly_value(r.salary_min, r.salary_max, r.salary_currency, r.is_salary_visible)
        overall.total += 1
        for g in members:
            g.total += 1
        if value is not None:
            overall.values.append(value)
            for g in members:
                g.values.append(value)

    return {
        "groups": groups,
        "overall": overall,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


def get_stats(db, force: bool = False) -> dict:
    now = time.time()
    with _lock:
        if not force and _cache["data"] and now - _cache["ts"] < CACHE_TTL:
            return _cache["data"]
    data = _load(db)
    with _lock:
        _cache.update({"ts": now, "data": data})
    return data


def public_summary(db) -> dict:
    """Everything the statistics page shows, biggest groups first."""
    data = get_stats(db)

    def listed(kind: str) -> list[dict]:
        gs = [g for (k, _), g in data["groups"].items()
              if k == kind and len(g.values) >= MIN_LIST and g.id != "other"]
        return [g.summary() for g in sorted(gs, key=lambda g: (-len(g.values), g.id))]

    overall = data["overall"]
    return {
        "overall": overall.summary() if overall.values else None,
        "roles": listed("role"),
        "categories": listed("category"),
        "cities": listed("city"),
        "min_compare": MIN_COMPARE,
        "computed_at": data["computed_at"],
    }


def insight_for(db, *, title: str, description: str, location: str,
                salary_min, salary_max, salary_currency, is_salary_visible=True) -> dict | None:
    """How this listing's pay sits against its kasb (or soha), or None if we cannot say.

    Returned for listings WITHOUT a salary too: "this kasb usually pays X" is
    the most useful line on a listing that hides its pay.
    """
    data = get_stats(db)
    role, cid, _city = _job_keys(title, description, location)
    chosen = None
    for kind, gid in (("role", role), ("category", cid)):
        if not gid or gid == "other":
            continue
        g = data["groups"].get((kind, gid))
        if g and len(g.values) >= MIN_COMPARE:
            chosen = g
            break
    if chosen is None:
        return None

    out = chosen.summary()
    value = monthly_value(salary_min, salary_max, salary_currency, is_salary_visible)
    out["job_value"] = _round(value) if value is not None else None
    # "5 mln dan" is a floor, not the pay: it can prove a job pays MORE than
    # the median, never that it pays less.
    out["job_is_floor"] = value is not None and salary_min is not None and salary_max is None
    # "8 mln gacha" is the mirror case: it can prove less, never more.
    out["job_is_ceiling"] = value is not None and salary_max is not None and salary_min is None
    diff = None
    # Above/below only against the same kasb. A soha mixes kasbs — "Savdo"
    # holds sales managers at ~11 mln and cashiers at ~4 — so a cashier came
    # out "41% below average" for being a cashier. Against a soha we give the
    # typical figure and no verdict.
    if value is not None and out["median"] and chosen.kind == "role":
        diff = int(round((value - out["median"]) / out["median"] * 100))
        if out["job_is_floor"] and diff < 10:
            diff = None
        if out["job_is_ceiling"] and diff > -10:
            diff = None
    out["diff_pct"] = diff
    return out
