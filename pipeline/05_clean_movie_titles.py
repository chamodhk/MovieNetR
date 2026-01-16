import pandas as pd
import re
import unicodedata
from rapidfuzz import process, fuzz

from core.db_core import get_db_session
from models.movie_models import Movie

# -------------------------
# CONFIG
# -------------------------
TSV_PATH = "./input/title.basics.tsv"
FUZZY_THRESHOLD = 96.5

# -------------------------
# DB SESSION
# -------------------------
session = get_db_session()

# -------------------------
# NORMALIZATION
# -------------------------
def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -------------------------
# LOAD CANONICAL MOVIES
# -------------------------
print("Loading canonical movie list...")

canon_df = pd.read_csv(TSV_PATH, sep="\t", low_memory=False)
canon_df = canon_df[canon_df["titleType"] == "movie"]

canon_df["norm_title"] = canon_df["primaryTitle"].map(str).map(normalize)

norm_canon_titles = canon_df["norm_title"].tolist()
norm_to_canonical = dict(
    zip(canon_df["norm_title"], canon_df["primaryTitle"])
)

print(f"Loaded {len(norm_canon_titles)} canonical movie titles")

# -------------------------
# MATCHING FUNCTION
# -------------------------
def find_canonical(raw_title):
    norm = normalize(raw_title)

    # 1. Exact normalized match
    if norm in norm_to_canonical:
        return norm_to_canonical[norm], "exact", 100

    # 2. Fuzzy match
    match = process.extractOne(
        norm,
        norm_canon_titles,
        scorer=fuzz.token_sort_ratio
    )

    if match and match[1] >= FUZZY_THRESHOLD:
        return norm_to_canonical[match[0]], "fuzzy", match[1]

    # 3. No confident match
    return None, "unmatched", None

# -------------------------
# FETCH DISTINCT MOVIE NAMES
# -------------------------
print("Fetching distinct movie names to canonicalize...")

distinct_titles = (
    session.query(Movie.movie_name)
    .filter(Movie.canonical_name.is_(None))
    .distinct()
    .all()
)

distinct_titles = [t[0] for t in distinct_titles]

print(f"Found {len(distinct_titles)} unique titles")

# -------------------------
# CANONICALIZATION LOOP
# -------------------------
updated = 0
unmatched = 0

for raw_title in distinct_titles:
    canonical, method, score = find_canonical(raw_title)

    if canonical:
        session.query(Movie).filter(
            Movie.movie_name == raw_title
        ).update(
            {Movie.canonical_name: canonical},
            synchronize_session=False
        )
        updated += 1
        if method == "fuzzy":
            print(raw_title,canonical, score )
    else:
        unmatched += 1

session.commit()

# -------------------------
# SUMMARY
# -------------------------
print("Canonicalization complete.")
print(f"Titles canonicalized : {updated}")
print(f"Titles unmatched     : {unmatched}")

session.close()
