from unittest.mock import MagicMock, patch
import requests as req_lib
import pytest

from fetcher import format_for_analysis, fetch_source, fetch_all


class TestFormatForAnalysis:
    def test_formats_title_and_description(self, sample_articles):
        result = format_for_analysis(sample_articles)
        assert "HEADLINE: Markets rally amid inflation concerns" in result
        assert "DESC: Stocks surged on Tuesday" in result

    def test_empty_list_returns_placeholder(self):
        assert format_for_analysis([]) == "(no articles retrieved)"

    def test_articles_are_numbered(self, sample_articles):
        result = format_for_analysis(sample_articles)
        assert result.startswith("1.")
        assert "\n2." in result

    def test_missing_title_omitted(self):
        articles = [{"title": None, "description": "Some description"}]
        result = format_for_analysis(articles)
        assert "HEADLINE" not in result
        assert "DESC: Some description" in result

    def test_missing_description_omitted(self):
        articles = [{"title": "A headline", "description": None}]
        result = format_for_analysis(articles)
        assert "HEADLINE: A headline" in result
        assert "DESC" not in result

    def test_both_fields_empty_produces_no_lines(self):
        articles = [{"title": None, "description": None}]
        result = format_for_analysis(articles)
        assert result == "(no articles retrieved)"


class TestFetchSource:
    def _mock_response(self, payload):
        resp = MagicMock()
        resp.json.return_value = payload
        return resp

    def test_returns_articles_on_success(self):
        resp = self._mock_response({"status": "ok", "articles": [{"title": "Test"}]})
        with patch("fetcher.requests.get", return_value=resp):
            result = fetch_source("reuters", "fake-key")
        assert result == [{"title": "Test"}]

    def test_returns_empty_list_on_api_error_status(self):
        resp = self._mock_response({"status": "error", "message": "Invalid key"})
        with patch("fetcher.requests.get", return_value=resp):
            result = fetch_source("reuters", "bad-key")
        assert result == []

    def test_returns_empty_list_on_network_exception(self):
        with patch("fetcher.requests.get", side_effect=req_lib.RequestException("timeout")):
            result = fetch_source("reuters", "key")
        assert result == []

    def test_returns_empty_list_when_articles_key_missing(self):
        resp = self._mock_response({"status": "ok"})
        with patch("fetcher.requests.get", return_value=resp):
            result = fetch_source("reuters", "key")
        assert result == []


class TestFetchAll:
    def test_returns_results_keyed_by_source_id(self):
        sources = [{"id": "reuters", "name": "Reuters"}, {"id": "cnn", "name": "CNN"}]
        with patch("fetcher.fetch_source", return_value=[{"title": "Story"}]):
            with patch("fetcher.time.sleep"):
                result = fetch_all(sources, "key")
        assert set(result.keys()) == {"reuters", "cnn"}

    def test_each_value_is_article_list(self):
        sources = [{"id": "reuters", "name": "Reuters"}]
        articles = [{"title": "Story 1"}, {"title": "Story 2"}]
        with patch("fetcher.fetch_source", return_value=articles):
            with patch("fetcher.time.sleep"):
                result = fetch_all(sources, "key")
        assert result["reuters"] == articles

    def test_sleeps_between_requests(self):
        sources = [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]
        with patch("fetcher.fetch_source", return_value=[]):
            with patch("fetcher.time.sleep") as mock_sleep:
                fetch_all(sources, "key", delay=0.5)
        mock_sleep.assert_called_once_with(0.5)

    def test_no_sleep_after_last_source(self):
        sources = [{"id": "only", "name": "Only"}]
        with patch("fetcher.fetch_source", return_value=[]):
            with patch("fetcher.time.sleep") as mock_sleep:
                fetch_all(sources, "key")
        mock_sleep.assert_not_called()
