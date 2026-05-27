import json
from unittest.mock import MagicMock

from analyzer import analyze_source, analyze_all, _empty_result


VALID_LLM_RESPONSE = {
    "sentiment_score": -0.2,
    "emotional_intensity": 5.0,
    "ideological_lean_score": 0.5,
    "ideological_lean_label": "Center",
    "ideological_lean_reasoning": "Balanced language patterns observed.",
    "top_topics": ["Politics", "Economy"],
    "framing_patterns": ["Neutral framing"],
    "distinctive_language": ["reported", "according to"],
    "notable_omissions": "none apparent",
    "one_line_summary": "Balanced coverage of current events.",
}


def _mock_client(payload):
    client = MagicMock()
    client.chat.completions.create.return_value.choices[0].message.content = json.dumps(payload)
    return client


class TestEmptyResult:
    def test_has_error_flag(self):
        assert _empty_result("Reuters")["error"] is True

    def test_preserves_source_name(self):
        assert _empty_result("BBC News")["source_name"] == "BBC News"

    def test_numeric_fields_are_zero(self):
        r = _empty_result("CNN")
        assert r["sentiment_score"] == 0.0
        assert r["emotional_intensity"] == 0.0
        assert r["ideological_lean_score"] == 0.0

    def test_list_fields_are_empty(self):
        r = _empty_result("Fox News")
        assert r["top_topics"] == []
        assert r["framing_patterns"] == []
        assert r["distinctive_language"] == []


class TestAnalyzeSource:
    def test_returns_parsed_llm_response(self):
        result = analyze_source("Reuters", "1. HEADLINE: Test", _mock_client(VALID_LLM_RESPONSE))
        assert result["sentiment_score"] == VALID_LLM_RESPONSE["sentiment_score"]
        assert result["ideological_lean_label"] == "Center"

    def test_returns_empty_result_on_invalid_json(self):
        client = MagicMock()
        client.chat.completions.create.return_value.choices[0].message.content = "not { valid json"
        result = analyze_source("Reuters", "headlines", client)
        assert result["error"] is True
        assert result["source_name"] == "Reuters"

    def test_returns_empty_result_on_api_exception(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception("API unavailable")
        result = analyze_source("Reuters", "headlines", client)
        assert result["error"] is True

    def test_passes_model_to_api(self):
        client = _mock_client(VALID_LLM_RESPONSE)
        analyze_source("Reuters", "headlines", client, model="gpt-4o-mini")
        call_kwargs = client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-4o-mini"


class TestAnalyzeAll:
    def test_skips_source_with_empty_content(self):
        source_data = {"reuters": {"name": "Reuters", "content": "", "article_count": 0}}
        client = MagicMock()
        result = analyze_all(source_data, client)
        assert result["reuters"]["error"] is True
        client.chat.completions.create.assert_not_called()

    def test_skips_source_with_placeholder_content(self):
        source_data = {
            "reuters": {"name": "Reuters", "content": "(no articles retrieved)", "article_count": 0}
        }
        client = MagicMock()
        result = analyze_all(source_data, client)
        assert result["reuters"]["error"] is True
        client.chat.completions.create.assert_not_called()

    def test_processes_source_with_valid_content(self):
        source_data = {
            "reuters": {"name": "Reuters", "content": "1. HEADLINE: World news", "article_count": 5}
        }
        result = analyze_all(source_data, _mock_client(VALID_LLM_RESPONSE))
        assert "error" not in result["reuters"]
        assert result["reuters"]["ideological_lean_label"] == "Center"

    def test_attaches_source_name_and_article_count(self):
        source_data = {
            "bbc-news": {"name": "BBC News", "content": "1. HEADLINE: Story", "article_count": 12}
        }
        result = analyze_all(source_data, _mock_client(VALID_LLM_RESPONSE))
        assert result["bbc-news"]["source_name"] == "BBC News"
        assert result["bbc-news"]["article_count"] == 12

    def test_processes_multiple_sources(self):
        source_data = {
            "reuters": {"name": "Reuters", "content": "1. HEADLINE: A", "article_count": 1},
            "cnn":     {"name": "CNN",     "content": "1. HEADLINE: B", "article_count": 1},
        }
        result = analyze_all(source_data, _mock_client(VALID_LLM_RESPONSE))
        assert "reuters" in result
        assert "cnn" in result
