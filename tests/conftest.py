import pytest


@pytest.fixture
def sample_articles():
    return [
        {"title": "Markets rally amid inflation concerns",
         "description": "Stocks surged on Tuesday as investors weighed new data."},
        {"title": "Congress debates spending bill",
         "description": "Lawmakers are at odds over a new domestic package."},
    ]


@pytest.fixture
def sample_result():
    return {
        "source_name": "Reuters",
        "sentiment_score": -0.3,
        "emotional_intensity": 4.5,
        "ideological_lean_score": 0.2,
        "ideological_lean_label": "Center",
        "ideological_lean_reasoning": "Neutral language throughout.",
        "top_topics": ["Economy", "Congress", "Inflation"],
        "framing_patterns": ["Factual reporting"],
        "distinctive_language": ["surged", "at odds"],
        "notable_omissions": "none apparent",
        "one_line_summary": "Balanced coverage of economic and political news.",
        "article_count": 2,
    }


@pytest.fixture
def sample_results(sample_result):
    base = sample_result.copy()
    return {
        "reuters": {**base, "source_name": "Reuters",
                    "ideological_lean_score": 0.2, "ideological_lean_label": "Center"},
        "fox-news": {**base, "source_name": "Fox News",
                     "ideological_lean_score": 3.5, "ideological_lean_label": "Right"},
        "cnn":      {**base, "source_name": "CNN",
                     "ideological_lean_score": -2.0, "ideological_lean_label": "Center-Left"},
    }
