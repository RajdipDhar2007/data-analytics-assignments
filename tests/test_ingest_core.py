import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Assignment_2_Ingestion_Page"
sys.path.insert(0, str(APP))

import ingest_core as ic  # noqa: E402

SAMPLE = (APP / "sample_data" / "country_wise_latest.csv").read_bytes()


class IngestCoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "test.db"

    def tearDown(self):
        self.tmp.cleanup()

    def test_sanitize_table_name(self):
        self.assertEqual(ic.sanitize_table_name("COVID data (v2).CSV"), "covid_data_v2")
        self.assertEqual(ic.sanitize_table_name("2020 data.csv"), "t_2020_data")
        self.assertEqual(ic.sanitize_table_name("   "), "uploaded_data")

    def test_read_csv_rejects_empty(self):
        with self.assertRaises(ValueError):
            ic.read_csv_bytes(b"   \n")

    def test_load_and_count(self):
        df = ic.read_csv_bytes(SAMPLE)
        res = ic.write_to_db(df, self.db, "covid", "country_wise_latest.csv", "fail")
        self.assertEqual(res["rows_in_table"], len(df))
        tables = ic.list_tables(self.db)
        self.assertIn("covid", set(tables["table"]))

    def test_fail_then_append(self):
        df = ic.read_csv_bytes(SAMPLE)
        ic.write_to_db(df, self.db, "covid", "a.csv", "fail")
        with self.assertRaises(ValueError):
            ic.write_to_db(df, self.db, "covid", "a.csv", "fail")
        res = ic.write_to_db(df.head(10), self.db, "covid", "a.csv", "append")
        self.assertEqual(res["rows_in_table"], len(df) + 10)

    def test_reserved_table_name(self):
        df = ic.read_csv_bytes(SAMPLE)
        with self.assertRaises(ValueError):
            ic.write_to_db(df, self.db, "ingestion_log", "a.csv", "fail")

    def test_summary_pdf(self):
        df = ic.read_csv_bytes(SAMPLE)
        res = ic.write_to_db(df, self.db, "covid", "a.csv", "fail")
        pdf = ic.build_summary_pdf(ic.profile_dataframe(df), {"filename": "a.csv", **res})
        self.assertTrue(pdf.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
