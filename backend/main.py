
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "ml-1m"

app = FastAPI(
    title="RecommendAI",
    description=(
        "A movie recommendation API using movie ratings "
        "and genre preferences, with explanations."
    ),
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_data():
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

    return ratings, movies


# Load the MovieLens dataset.
ratings, movies = load_data()

# Calculate each movie's average rating and number of ratings.
movie_stats = (
    ratings.groupby("movie_id")["rating"]
    .agg(["mean", "count"])
    .reset_index()
)

movie_stats = movie_stats.merge(movies, on="movie_id")

# Use a weighted rating to avoid overvaluing movies
# that have very few ratings.
minimum_votes = 50
global_mean = float(ratings["rating"].mean())

popular_movies = movie_stats[
    movie_stats["count"] >= minimum_votes
].copy()

popular_movies["weighted_rating"] = (
    (
        popular_movies["count"]
        / (popular_movies["count"] + minimum_votes)
    )
    * popular_movies["mean"]
    + (
        minimum_votes
        / (popular_movies["count"] + minimum_votes)
    )
    * global_mean
)

popular_movies = popular_movies.sort_values(
    ["weighted_rating", "count"],
    ascending=[False, False],
)


class RecommendationRequest(BaseModel):
    user_id: int = Field(gt=0)
    limit: int = Field(default=10, ge=1, le=50)


@app.get("/")
def home():
    return {
        "message": "RecommendAI API is running!",
        "docs": "/docs",
        "total_movies": int(len(movies)),
        "total_ratings": int(len(ratings)),
    }


@app.get("/movies/popular")
def get_popular_movies(
    limit: int = Query(default=10, ge=1, le=50),
):
    results = popular_movies.head(limit)

    return {
        "count": len(results),
        "movies": [
            {
                "movie_id": int(row["movie_id"]),
                "title": row["title"],
                "genres": row["genres"],
                "average_rating": round(float(row["mean"]), 2),
                "rating_count": int(row["count"]),
                "weighted_rating": round(
                    float(row["weighted_rating"]), 3
                ),
            }
            for _, row in results.iterrows()
        ],
    }


@app.post("/recommend")
def recommend(request: RecommendationRequest):
    # Find all ratings belonging to this user.
    user_ratings = ratings[
        ratings["user_id"] == request.user_id
    ]

    if user_ratings.empty:
        raise HTTPException(
            status_code=404,
            detail="User not found in the MovieLens dataset.",
        )

    # Exclude movies the user has already rated.
    rated_movie_ids = set(user_ratings["movie_id"])

    candidates = popular_movies[
        ~popular_movies["movie_id"].isin(rated_movie_ids)
    ].copy()

    # Learn the user's genre preferences from their ratings.
    rated_details = user_ratings.merge(movies, on="movie_id")

    genre_preferences = {}

    for row in rated_details.itertuples(index=False):
        for genre in row.genres.split("|"):
            genre_preferences[genre] = (
                genre_preferences.get(genre, 0.0)
                + (float(row.rating) - 3.0)
            )

    def score_movie(row):
        genres = row["genres"].split("|")

        preference_score = sum(
            genre_preferences.get(genre, 0.0)
            for genre in genres
        )

        quality_score = float(row["weighted_rating"])

        popularity_bonus = min(
            float(row["count"]) / 1000.0,
            1.0,
        )

        return (
            quality_score
            + 0.15 * preference_score
            + 0.1 * popularity_bonus
        )

    # Calculate a personalized score for every candidate.
    candidates["score"] = candidates.apply(
        score_movie,
        axis=1,
    )

    # Explain each recommendation using the user's
    # observed genre preferences and the ranking signals.
    def explain_recommendation(row):
        genres = row["genres"].split("|")

        matching_genres = [
            genre
            for genre in genres
            if genre_preferences.get(genre, 0.0) > 0
        ]

        if matching_genres:
            best_genres = sorted(
                matching_genres,
                key=lambda genre: genre_preferences[genre],
                reverse=True,
            )[:2]

            genre_text = " and ".join(best_genres)

            return (
                f"Recommended because your ratings suggest "
                f"you enjoy {genre_text} movies."
            )

        return (
            "Selected for its strong overall rating "
            "and popularity."
        )

    # Highest-scoring movies appear first.
    candidates = candidates.sort_values(
        "score",
        ascending=False,
    )

    results = candidates.head(request.limit)

    return {
        "user_id": request.user_id,
        "count": len(results),
        "recommendations": [
            {
                "movie_id": int(row["movie_id"]),
                "title": row["title"],
                "genres": row["genres"],
                "average_rating": round(float(row["mean"]), 2),
                "score": round(float(row["score"]), 3),
                "reason": explain_recommendation(row),
            }
            for _, row in results.iterrows()
        ],
    }


@app.get("/users/{user_id}/ratings")
def get_user_ratings(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50),
):
    user_ratings = ratings[
        ratings["user_id"] == user_id
    ]

    if user_ratings.empty:
        raise HTTPException(
            status_code=404,
            detail="User not found in the MovieLens dataset.",
        )

    results = (
        user_ratings.merge(movies, on="movie_id")
        .head(limit)
    )

    return {
        "user_id": user_id,
        "count": len(results),
        "ratings": [
            {
                "movie_id": int(row.movie_id),
                "title": row.title,
                "genres": row.genres,
                "rating": float(row.rating),
            }
            for row in results.itertuples(index=False)
        ],
    }
