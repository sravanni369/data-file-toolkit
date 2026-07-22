import json
import unittest

from toolkit import coerce, csv_to_rows, rows_to_json, json_to_csv, validate

CSV = """id,name,age,premium
1, Asha ,34,220.50
2,Ben,,180
,Cara,29,205.75
"""


class TestCoerce(unittest.TestCase):
    def test_int(self):
        self.assertEqual(coerce("42"), 42)

    def test_float(self):
        self.assertEqual(coerce("4.2"), 4.2)

    def test_string_stripped(self):
        self.assertEqual(coerce(" Asha "), "Asha")

    def test_empty_is_none(self):
        self.assertIsNone(coerce(""))
        self.assertIsNone(coerce("   "))
        self.assertIsNone(coerce(None))


class TestCsvToRows(unittest.TestCase):
    def test_parses_and_coerces(self):
        rows = csv_to_rows(CSV)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], {"id": 1, "name": "Asha", "age": 34, "premium": 220.5})
        self.assertIsNone(rows[1]["age"])
        self.assertIsNone(rows[2]["id"])


class TestRoundTrip(unittest.TestCase):
    def test_csv_json_round_trip(self):
        rows = csv_to_rows(CSV)
        self.assertEqual(json.loads(rows_to_json(rows)), rows)

    def test_json_to_csv_headers_and_missing(self):
        text = json.dumps([{"a": 1, "b": 2}, {"a": 3, "c": 4}])
        out = json_to_csv(text)
        lines = out.strip().split("\n")
        self.assertEqual(lines[0], "a,b,c")
        self.assertEqual(lines[1], "1,2,")
        self.assertEqual(lines[2], "3,,4")

    def test_json_to_csv_rejects_non_array(self):
        with self.assertRaises(ValueError):
            json_to_csv('{"a": 1}')


class TestValidate(unittest.TestCase):
    def test_counts_and_line_numbers(self):
        ok, errors = validate(CSV, ["id", "age", "premium"])
        self.assertEqual(ok, 1)
        self.assertEqual(len(errors), 2)
        self.assertIn("line 3", errors[0])
        self.assertIn("age", errors[0])
        self.assertIn("line 4", errors[1])
        self.assertIn("id", errors[1])

    def test_missing_column_reported_at_header(self):
        ok, errors = validate(CSV, ["id", "salary"])
        self.assertEqual(ok, 0)
        self.assertIn("header", errors[0])
        self.assertIn("salary", errors[0])


if __name__ == "__main__":
    unittest.main()
