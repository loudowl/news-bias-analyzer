import re

from sources import SOURCES, SOURCE_MAP


class TestSourcesList:
    def test_all_entries_have_required_fields(self):
        for s in SOURCES:
            assert "id" in s,       f"Missing 'id' in {s}"
            assert "name" in s,     f"Missing 'name' in {s}"
            assert "category" in s, f"Missing 'category' in {s}"

    def test_no_duplicate_ids(self):
        ids = [s["id"] for s in SOURCES]
        assert len(ids) == len(set(ids)), f"Duplicate source IDs: {ids}"

    def test_no_duplicate_names(self):
        names = [s["name"] for s in SOURCES]
        assert len(names) == len(set(names)), f"Duplicate source names: {names}"

    def test_ids_are_lowercase_hyphenated(self):
        for s in SOURCES:
            assert re.match(r"^[a-z0-9-]+$", s["id"]), \
                f"Source ID '{s['id']}' must be lowercase letters, digits, and hyphens only"

    def test_names_are_non_empty_strings(self):
        for s in SOURCES:
            assert isinstance(s["name"], str) and s["name"].strip(), \
                f"Source name must be a non-empty string: {s}"

    def test_at_least_one_source_defined(self):
        assert len(SOURCES) > 0


class TestSourceMap:
    def test_map_length_matches_sources_list(self):
        assert len(SOURCE_MAP) == len(SOURCES)

    def test_map_keys_match_source_ids(self):
        for s in SOURCES:
            assert s["id"] in SOURCE_MAP, f"'{s['id']}' missing from SOURCE_MAP"

    def test_map_values_are_same_objects_as_sources(self):
        for s in SOURCES:
            assert SOURCE_MAP[s["id"]] is s

    def test_npr_id_is_correct(self):
        ids = [s["id"] for s in SOURCES]
        assert "npr" in ids, "NPR source ID should be 'npr', not 'npm' or other typo"
