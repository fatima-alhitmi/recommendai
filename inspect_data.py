
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data/ml-1m")

# MovieLens 1M files use "::" as their separator.
ratings = pd.read_csv(
    DATA_DIR / "ratings.dat",
    sep="::",
    engine="python",
    names=["user_id", "movie_id", "rating", "timestamp"],
    encoding="latin-1",
)

movies = pd.read_csv(
    DATA_DIR / "movies.dat",
    sep="::",
    engine="python",
    names=["movie_id", "title", "genres"],
    encoding="latin-1",
)

users = pd.read_csv(
    DATA_DIR / "users.dat",
    sep="::",
    engine="python",
    names=["user_id", "gender", "age", "occupation", "zip_code"],
    encoding="latin-1",
)

print("=== DATASET OVERVIEW ===")
print(f"Ratings: {len(ratings):,}")
print(f"Movies:  {len(movies):,}")
print(f"Users:   {len(users):,}")

print("\n=== RATINGS ===")
print(ratings.head())
print("\nRating distribution:")
print(ratings["rating"].value_counts().sort_index())

print("\n=== MOVIES ===")
print(movies.head())

print("\n=== DATA QUALITY ===")
print(f"Missing ratings values: {ratings.isna().sum().sum()}")
print(f"Duplicate rating rows:  {ratings.duplicated().sum()}")
print(f"Missing movie titles:   {movies['title'].isna().sum()}")