from pathlib import Path

from reporter import _lean_position, _make_card, build_report


class TestLeanPosition:
    def test_center_is_50_percent(self):
        assert _lean_position(0) == 50.0

    def test_far_left_is_0_percent(self):
        assert _lean_position(-5) == 0.0

    def test_far_right_is_100_percent(self):
        assert _lean_position(5) == 100.0

    def test_midpoint_right(self):
        assert _lean_position(2.5) == 75.0

    def test_midpoint_left(self):
        assert _lean_position(-2.5) == 25.0

    def test_clamped_below_zero(self):
        assert _lean_position(-10) == 0.0

    def test_clamped_above_100(self):
        assert _lean_position(10) == 100.0


class TestMakeCard:
    def test_error_card_shows_no_data_message(self):
        card = _make_card({"source_name": "Reuters", "error": True})
        assert "No data retrieved" in card
        assert "Reuters" in card

    def test_card_contains_source_name(self, sample_result):
        assert "Reuters" in _make_card(sample_result)

    def test_card_contains_lean_label(self, sample_result):
        assert "Center" in _make_card(sample_result)

    def test_card_contains_score_labels(self, sample_result):
        card = _make_card(sample_result)
        assert "Lean:" in card
        assert "Sentiment:" in card
        assert "Intensity:" in card

    def test_card_contains_topic_tags(self, sample_result):
        card = _make_card(sample_result)
        assert "Economy" in card
        assert "Congress" in card

    def test_card_contains_reasoning(self, sample_result):
        assert "Neutral language throughout" in _make_card(sample_result)

    def test_card_contains_one_line_summary(self, sample_result):
        assert "Balanced coverage" in _make_card(sample_result)


class TestBuildReport:
    def test_creates_html_file(self, sample_results, tmp_path):
        out = str(tmp_path / "report.html")
        build_report(sample_results, output_path=out)
        assert Path(out).exists()

    def test_returns_output_path(self, sample_results, tmp_path):
        out = str(tmp_path / "report.html")
        result = build_report(sample_results, output_path=out)
        assert result == out

    def test_html_has_valid_document_structure(self, sample_results, tmp_path):
        out = str(tmp_path / "report.html")
        build_report(sample_results, output_path=out)
        html = Path(out).read_text()
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_html_contains_plotly_script(self, sample_results, tmp_path):
        out = str(tmp_path / "report.html")
        build_report(sample_results, output_path=out)
        assert "plotly" in Path(out).read_text()

    def test_html_contains_all_source_names(self, sample_results, tmp_path):
        out = str(tmp_path / "report.html")
        build_report(sample_results, output_path=out)
        html = Path(out).read_text()
        assert "Reuters" in html
        assert "Fox News" in html
        assert "CNN" in html

    def test_all_error_results_still_produces_valid_html(self, tmp_path):
        error_results = {
            "reuters": {"source_name": "Reuters", "error": True, "article_count": 0}
        }
        out = str(tmp_path / "report.html")
        build_report(error_results, output_path=out)
        html = Path(out).read_text()
        assert html.startswith("<!DOCTYPE html>")
