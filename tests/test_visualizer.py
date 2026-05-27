import pytest

from visualizer import (
    ideological_spectrum_chart,
    sentiment_bar_chart,
    topic_heatmap,
    intensity_radar,
    lean_bar_chart,
)

EMPTY = {}
ALL_ERRORS = {"reuters": {"source_name": "Reuters", "error": True}}


@pytest.fixture
def results():
    base = {
        "sentiment_score": -0.2,
        "emotional_intensity": 5.0,
        "ideological_lean_score": 0.5,
        "ideological_lean_label": "Center",
        "top_topics": ["Politics", "Economy", "Climate"],
        "article_count": 10,
        "one_line_summary": "Balanced news coverage.",
    }
    return {
        "reuters":  {**base, "source_name": "Reuters",
                     "ideological_lean_score": 0.1,  "ideological_lean_label": "Center"},
        "fox-news": {**base, "source_name": "Fox News",
                     "ideological_lean_score": 3.5,  "ideological_lean_label": "Right"},
        "cnn":      {**base, "source_name": "CNN",
                     "ideological_lean_score": -2.0, "ideological_lean_label": "Center-Left"},
    }


class TestIdeologicalSpectrumChart:
    def test_returns_html_div(self, results):
        assert "<div" in ideological_spectrum_chart(results)

    def test_empty_input_returns_fallback(self):
        assert ideological_spectrum_chart(EMPTY) == "<p>No data available.</p>"

    def test_all_errors_returns_fallback(self):
        assert ideological_spectrum_chart(ALL_ERRORS) == "<p>No data available.</p>"

    def test_output_does_not_include_full_html_doc(self, results):
        result = ideological_spectrum_chart(results)
        assert "<!DOCTYPE" not in result


class TestSentimentBarChart:
    def test_returns_html_div(self, results):
        assert "<div" in sentiment_bar_chart(results)

    def test_empty_input_returns_fallback(self):
        assert sentiment_bar_chart(EMPTY) == "<p>No data available.</p>"

    def test_all_errors_returns_fallback(self):
        assert sentiment_bar_chart(ALL_ERRORS) == "<p>No data available.</p>"


class TestTopicHeatmap:
    def test_returns_html_div(self, results):
        assert "<div" in topic_heatmap(results)

    def test_empty_input_returns_fallback(self):
        assert topic_heatmap(EMPTY) == "<p>No topic data available.</p>"

    def test_handles_many_topics_without_error(self, results):
        results["reuters"]["top_topics"] = [f"Topic{i}" for i in range(20)]
        result = topic_heatmap(results)
        assert "<div" in result

    def test_single_source_renders(self, results):
        assert "<div" in topic_heatmap({"reuters": results["reuters"]})


class TestIntensityRadar:
    def test_returns_html_div(self, results):
        assert "<div" in intensity_radar(results)

    def test_empty_input_returns_fallback(self):
        assert intensity_radar(EMPTY) == "<p>No data available.</p>"

    def test_all_errors_returns_fallback(self):
        assert intensity_radar(ALL_ERRORS) == "<p>No data available.</p>"


class TestLeanBarChart:
    def test_returns_html_div(self, results):
        assert "<div" in lean_bar_chart(results)

    def test_empty_input_returns_fallback(self):
        assert lean_bar_chart(EMPTY) == "<p>No data available.</p>"

    def test_all_errors_returns_fallback(self):
        assert lean_bar_chart(ALL_ERRORS) == "<p>No data available.</p>"

    def test_single_source_renders(self, results):
        assert "<div" in lean_bar_chart({"reuters": results["reuters"]})
