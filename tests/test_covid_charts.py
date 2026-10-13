import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Assignment_1_COVID_Dashboard"))

import covid_charts as cc  # noqa: E402


class CovidChartsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.country = cc.load_country_latest()
        cls.daily = cc.load_daily()
        cls.regions = sorted(cls.country["WHO Region"].unique())

    def test_kpis_match_column_sums(self):
        k = cc.kpi_totals(self.country)
        self.assertEqual(k["Confirmed"], int(self.country["Confirmed"].sum()))

    def test_three_charts_build(self):
        trend = cc.daily_trend(self.daily, self.regions, self.daily.Date.min(), self.daily.Date.max())
        for fig in (cc.bar_top_countries(self.country, "Deaths", 8),
                    cc.line_trend(trend, cc.METRICS, log=True),
                    cc.pie_by_region(self.country, "Confirmed")):
            self.assertTrue(cc.fig_to_png(fig).startswith(b"\x89PNG"))

    def test_region_filter_changes_trend(self):
        d0, d1 = self.daily.Date.min(), self.daily.Date.max()
        all_t = cc.daily_trend(self.daily, self.regions, d0, d1)
        one_t = cc.daily_trend(self.daily, self.regions[:1], d0, d1)
        self.assertLess(one_t["Confirmed"].iloc[-1], all_t["Confirmed"].iloc[-1])

    def test_pdf_builds(self):
        trend = cc.daily_trend(self.daily, self.regions, self.daily.Date.min(), self.daily.Date.max())
        figs = {"bar": cc.fig_to_png(cc.bar_top_countries(self.country, "Confirmed", 5)),
                "line": cc.fig_to_png(cc.line_trend(trend, ["Confirmed"])),
                "pie": cc.fig_to_png(cc.pie_by_region(self.country, "Confirmed"))}
        top = self.country.nlargest(5, "Confirmed")[["Country/Region"] + cc.METRICS]
        pdf = cc.build_pdf(cc.kpi_totals(self.country), figs, "test", top, "27 Jul 2020")
        self.assertTrue(pdf.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
