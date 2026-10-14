
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path("data/ml-1m")


class MovieRecommender:
    def __init__(self):
        self.ratings = pd.read_csv(
            DATA_DIR / "ratings.dat",
            sep="::",
            engine="python",
            names=["user_id", "movie_id", "rating", "timestamp"],
            encoding="latin-1",
        )

        self.movies = pd.read_csv(
            DATA_DIR / "movies.dat",
            sep="::",
            engine="python",
            names=["movie_id", "title", "genres"],
            encoding="latin-1",
        )

        # Map original IDs to matrix positions.
        self.user_ids = sorted(self.ratings["user_id"].unique())
        self.movie_ids = sorted(self.movies["movie_id"].unique())

        self.user_to_index = {
            user_id: index
            for index, user_id in enumerate(self.user_ids)
        }
        self.movie_to_index = {
            movie_id: index
            for index, movie_id in enumerate(self.movie_ids)
        }

        rows = self.ratings["user_id"].map(self.user_to_index)
        cols = self.ratings["movie_id"].map(self.movie_to_index)

        self.user_movie_matrix = csr_matrix(
            (
                self.ratings["rating"].to_numpy(dtype=float),
                (rows.to_numpy(), cols.to_numpy()),
            ),
            shape=(len(self.user_ids), len(self.movie_ids)),
        )

        # Compare movies using rating patterns across users.
        self.movie_similarity = cosine_similarity(
            self.user_movie_matrix.T,
            dense_output=True,
        )

        # Popularity baseline: require enough ratings to reduce
        # the influence of movies with only a handful of ratings.
        self.popular_movies = (
            self.ratings.groupby("movie_id")["rating"]
            .agg(["mean", "count"])
            .query("count >= 50")
            .sort_values(["mean", "count"], ascending=False)
            .reset_index()
            .merge(self.movies, on="movie_id")
        )

    def recommend(self, user_id, limit=10):
        if user_id not in self.user_to_index:
            raise ValueError(f"Unknown user ID: {user_id}")

        user_index = self.user_to_index[user_id]
        user_ratings = self.user_movie_matrix.getrow(user_index)

        watched_indices = set(user_ratings.indices)
        scores = np.zeros(len(self.movie_ids))

        # For each movie the user rated, add its similarity to
        # unseen movies, weighted by the user's rating.
        for movie_index, rating in zip(
            user_ratings.indices,
            user_ratings.data,
        ):
            scores += self.movie_similarity[movie_index] * (
                rating - 3.0
            )

        scores[ list(watched_indices) ] = -np.inf

        ranked_indices = np.argsort(scores)[::-1]
        recommendations = []

        for index in ranked_indices:
            if not np.isfinite(scores[index]):
                continue

            movie_id = self.movie_ids[index]
            movie = self.movies.loc[
                self.movies["movie_id"] == movie_id
            ].iloc[0]

            recommendations.append(
                {
                    "movie_id": int(movie_id),
                    "title": movie["title"],
                    "genres": movie["genres"],
                    "score": round(float(scores[index]), 3),
                }
            )

            if len(recommendations) >= limit:
                break

        return recommendations

    def popular(self, limit=10):
        return self.popular_movies.head(limit)[
            ["movie_id", "title", "genres", "mean", "count"]
        ].to_dict(orient="records")


if __name__ == "__main__":
    recommender = MovieRecommender()

    print("=== RecommendAI: Recommendation Engine ===")
    print(f"Loaded {len(recommender.ratings):,} ratings")
    print(f"Loaded {len(recommender.movies):,} movies")
    print("\n=== Popular Movies (baseline) ===")

    for movie in recommender.popular(5):
        print(
            f"{movie['title']} | "
            f"Average: {movie['mean']:.2f} | "
            f"Ratings: {movie['count']}"
        )

    print("\n=== Recommendations for Sample User 1 ===")

    for movie in recommender.recommend(user_id=1, limit=5):
        print(
            f"{movie['title']} | "
            f"Genres: {movie['genres']} | "
            f"Score: {movie['score']}"
        )
