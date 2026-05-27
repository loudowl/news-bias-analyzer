import pytest
from unittest.mock import patch

import server
from server import app, _label, _inject_nav, PAGE_SIZE


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def archive_dir(tmp_path):
    """Temp archive with three report files."""
    archive = tmp_path / "archive"
    archive.mkdir()
    for stem in ["2026-05-27_08-00", "2026-05-27_12-00", "2026-05-27_17-00"]:
        (archive / f"{stem}.html").write_text(
            f'<!DOCTYPE html><html><body><p id="{stem}">{stem}</p></body></html>'
        )
    return archive


@pytest.fixture
def large_archive_dir(tmp_path):
    """Temp archive with more files than PAGE_SIZE."""
    archive = tmp_path / "archive"
    archive.mkdir()
    for i in range(PAGE_SIZE + 2):
        stem = f"2026-05-27_{i:02d}-00"
        (archive / f"{stem}.html").write_text(
            f'<!DOCTYPE html><html><body><p>{stem}</p></body></html>'
        )
    return archive


class TestLabel:
    def test_formats_morning_time(self):
        assert _label("2026-05-27_08-00") == "May 27, 2026 · 08:00 AM"

    def test_formats_afternoon_time(self):
        result = _label("2026-05-27_17-00")
        assert "May 27, 2026" in result
        assert "PM" in result

    def test_returns_stem_unchanged_on_bad_format(self):
        assert _label("not-a-date") == "not-a-date"

    def test_returns_stem_unchanged_on_partial_format(self):
        assert _label("2026-05-27") == "2026-05-27"


class TestInjectNav:
    def test_no_change_when_archive_dir_missing(self, tmp_path):
        html = "<html><body><p>content</p></body></html>"
        with patch.object(server, "ARCHIVE_DIR", tmp_path / "nonexistent"):
            result = _inject_nav(html, "any-stem", "/", 1)
        assert result == html

    def test_injects_nav_before_body_close(self, archive_dir):
        html = "<html><body><p>content</p></body></html>"
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            result = _inject_nav(html, "2026-05-27_08-00", "/", 1)
        assert result.endswith("</body></html>")
        assert "archive-nav" in result

    def test_current_stem_receives_active_class(self, archive_dir):
        html = "<html><body></body></html>"
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            result = _inject_nav(html, "2026-05-27_08-00", "/", 1)
        assert "archive-link active" in result

    def test_other_stems_do_not_receive_active_class(self, archive_dir):
        html = "<html><body></body></html>"
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            result = _inject_nav(html, "2026-05-27_08-00", "/", 1)
        # count active links — only one should be active
        assert result.count("archive-link active") == 1

    def test_older_button_appears_on_page_1_of_large_archive(self, large_archive_dir):
        html = "<html><body></body></html>"
        with patch.object(server, "ARCHIVE_DIR", large_archive_dir):
            result = _inject_nav(html, None, "/", 1)
        assert "Older" in result

    def test_newer_button_appears_on_page_2(self, large_archive_dir):
        html = "<html><body></body></html>"
        with patch.object(server, "ARCHIVE_DIR", large_archive_dir):
            result = _inject_nav(html, None, "/", 2)
        assert "Newer" in result

    def test_no_pagination_when_under_page_size(self, archive_dir):
        html = "<html><body></body></html>"
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            result = _inject_nav(html, None, "/", 1)
        assert "Older" not in result
        assert "Newer" not in result


class TestIndexRoute:
    def test_returns_404_when_no_reports_exist(self, client, tmp_path):
        with patch.object(server, "ARCHIVE_DIR", tmp_path / "empty"):
            resp = client.get("/")
        assert resp.status_code == 404

    def test_returns_200_when_reports_exist(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/")
        assert resp.status_code == 200

    def test_serves_latest_report_content(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/")
        # Latest file sorted descending is 2026-05-27_17-00
        assert b"2026-05-27_17-00" in resp.data

    def test_archive_nav_is_injected(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/")
        assert b"archive-nav" in resp.data

    def test_page_query_param_accepted(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/?page=1")
        assert resp.status_code == 200


class TestArchiveRoute:
    def test_returns_200_for_existing_report(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/archive/2026-05-27_08-00")
        assert resp.status_code == 200

    def test_serves_requested_report_content(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/archive/2026-05-27_08-00")
        assert b"2026-05-27_08-00" in resp.data

    def test_returns_404_for_missing_report(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/archive/1999-01-01_00-00")
        assert resp.status_code == 404

    def test_archive_nav_is_injected(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/archive/2026-05-27_12-00")
        assert b"archive-nav" in resp.data

    def test_page_query_param_accepted(self, client, archive_dir):
        with patch.object(server, "ARCHIVE_DIR", archive_dir):
            resp = client.get("/archive/2026-05-27_08-00?page=1")
        assert resp.status_code == 200
