"""Salary statistics — which listings count, and when a comparison is honest."""
from __future__ import annotations

import pytest

from app.services import salary_stats as ss


class TestMonthlyValue:
    def test_range_is_its_midpoint(self):
        assert ss.monthly_value(4_000_000, 6_000_000, "UZS") == 5_000_000

    def test_a_bare_floor_counts_as_the_floor(self):
        assert ss.monthly_value(5_000_000, None, "UZS") == 5_000_000
        assert ss.monthly_value(None, 7_000_000, "UZS") == 7_000_000

    def test_daily_wages_and_typos_are_left_out(self):
        assert ss.monthly_value(350_000, None, "UZS") is None     # a shift rate
        assert ss.monthly_value(500_000_000, None, "UZS") is None

    def test_other_currencies_and_hidden_pay_are_left_out(self):
        assert ss.monthly_value(750, None, "USD") is None
        assert ss.monthly_value(5_000_000, None, "UZS", visible=False) is None

    def test_no_salary(self):
        assert ss.monthly_value(None, None, "UZS") is None

    def test_swapped_bounds(self):
        assert ss.monthly_value(6_000_000, 4_000_000, "UZS") == 5_000_000


def _add(db, company, title, lo=None, hi=None, location="Toshkent", visible=True):
    from app.models.job import Job

    j = Job(company_id=company.id, title=title, description="", location=location,
            status="active", salary_min=lo, salary_max=hi, salary_currency="UZS",
            is_salary_visible=visible, job_type="full_time", experience_level="junior")
    db.add(j)
    db.commit()
    return j


class TestInsight:
    @pytest.fixture(autouse=True)
    def _fresh_cache(self):
        ss._cache.update({"ts": 0.0, "data": None})
        yield
        ss._cache.update({"ts": 0.0, "data": None})

    def test_compares_against_the_kasb_when_it_is_big_enough(self, test_db, test_company):
        for pay in (8, 9, 10, 11, 12):
            _add(test_db, test_company, "Sotuv menejeri", pay * 1_000_000)
        out = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="Toshkent",
                             salary_min=15_000_000, salary_max=None, salary_currency="UZS")
        assert out["kind"] == "role" and out["id"] == "Sotuv menejeri"
        assert out["median"] == 10_000_000
        assert out["diff_pct"] == 50

    def test_russian_title_is_the_same_kasb(self, test_db, test_company):
        for pay in (8, 9, 10, 11, 12):
            _add(test_db, test_company, "Менеджер по продажам", pay * 1_000_000)
        out = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="",
                             salary_min=None, salary_max=None, salary_currency="UZS")
        assert out["id"] == "Sotuv menejeri" and out["count"] == 5

    def test_falls_back_to_the_soha_when_the_kasb_is_small(self, test_db, test_company):
        for t in ("Sotuvchi", "Kassir", "Savdo vakili", "Sotuv operatori", "Sotuvchi-konsultant"):
            _add(test_db, test_company, t, 5_000_000)
        out = ss.insight_for(test_db, title="Kassir", description="", location="",
                             salary_min=5_000_000, salary_max=5_000_000, salary_currency="UZS")
        assert out["kind"] == "category"
        # A soha mixes kasbs, so no above/below verdict against it.
        assert out["diff_pct"] is None and out["job_value"] == 5_000_000

    def test_a_floor_proves_only_more_and_a_ceiling_only_less(self, test_db, test_company):
        for pay in (8, 9, 10, 11, 12):
            _add(test_db, test_company, "Sotuv menejeri", pay * 1_000_000)
        below = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="",
                               salary_min=8_000_000, salary_max=None, salary_currency="UZS")
        assert below["job_is_floor"] and below["diff_pct"] is None   # "8 mln dan" may pay 12
        above = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="",
                               salary_min=13_000_000, salary_max=None, salary_currency="UZS")
        assert above["diff_pct"] == 30
        ceiling_hi = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="",
                                    salary_min=None, salary_max=13_000_000, salary_currency="UZS")
        assert ceiling_hi["job_is_ceiling"] and ceiling_hi["diff_pct"] is None  # "13 mln gacha" may pay 5
        ceiling_lo = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="",
                                    salary_min=None, salary_max=6_000_000, salary_currency="UZS")
        assert ceiling_lo["diff_pct"] == -40
        ranged = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="",
                                salary_min=7_000_000, salary_max=9_000_000, salary_currency="UZS")
        assert ranged["diff_pct"] == -20 and not ranged["job_is_floor"]

    def test_no_comparison_from_a_handful(self, test_db, test_company):
        for pay in (5, 6, 7):
            _add(test_db, test_company, "Buxgalter", pay * 1_000_000)
        assert ss.insight_for(test_db, title="Buxgalter", description="", location="",
                              salary_min=6_000_000, salary_max=None, salary_currency="UZS") is None

    def test_listing_without_pay_still_gets_the_typical_figure(self, test_db, test_company):
        for pay in (8, 9, 10, 11, 12):
            _add(test_db, test_company, "Sotuv menejeri", pay * 1_000_000)
        out = ss.insight_for(test_db, title="Sotuv menejeri", description="", location="",
                             salary_min=None, salary_max=None, salary_currency="UZS")
        assert out["median"] == 10_000_000
        assert out["job_value"] is None and out["diff_pct"] is None

    def test_hidden_salaries_do_not_leak_into_the_median(self, test_db, test_company):
        for pay in (8, 9, 10, 11, 12):
            _add(test_db, test_company, "Sotuv menejeri", pay * 1_000_000)
        _add(test_db, test_company, "Sotuv menejeri", 90_000_000, visible=False)
        s = ss.public_summary(test_db)
        role = next(r for r in s["roles"] if r["id"] == "Sotuv menejeri")
        assert role["count"] == 5 and role["total"] == 6 and role["max"] == 12_000_000


def test_endpoint_is_not_swallowed_by_the_job_id_route(client):
    res = client.get("/api/v1/jobs/salary-stats")
    assert res.status_code == 200
    assert {"overall", "roles", "categories", "cities"} <= set(res.json())
