"""
News sources to analyze.
NewsAPI source IDs: https://newsapi.org/sources
"""

SOURCES = [
    {"id": "reuters",               "name": "Reuters",              "category": "Wire"},
    {"id": "associated-press",      "name": "Associated Press",     "category": "Wire"},
    {"id": "bbc-news",              "name": "BBC News",             "category": "International"},
    {"id": "npm",                   "name": "NPR",                  "category": "US Broadcast"},
    {"id": "cnn",                   "name": "CNN",                  "category": "US Cable"},
    {"id": "msnbc",                 "name": "MSNBC",                "category": "US Cable"},
    {"id": "fox-news",              "name": "Fox News",             "category": "US Cable"},
    {"id": "the-new-york-times",    "name": "New York Times",       "category": "US Print"},
    {"id": "the-washington-post",   "name": "Washington Post",      "category": "US Print"},
    {"id": "the-wall-street-journal","name": "Wall Street Journal", "category": "US Print"},
    {"id": "the-guardian-us",       "name": "The Guardian (US)",    "category": "International"},
    {"id": "the-hill",              "name": "The Hill",             "category": "US Digital"},
    {"id": "politico",              "name": "Politico",             "category": "US Digital"},
    {"id": "breitbart-news",        "name": "Breitbart News",       "category": "US Digital"},
]

SOURCE_MAP = {s["id"]: s for s in SOURCES}
