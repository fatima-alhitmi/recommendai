from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path("data/ml-1m")
RANDOM_STATE = 42


def load_ratings():
    return pd.read_csv(
        DATA_DIR / "ratings.dat",
        sep="::",
        engine="python",
        names=["user_id", "movie_id", "rating", "timestamp"],
        encoding="latin-1",
    )


def main():
    print("Loading MovieLens ratings...")

    ratings = load_ratings()

    train, test = train_test_split(
        ratings,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    # Create ID mappings using the training data only.
    user_ids = sorted(train["user_id"].unique())
    movie_ids = sorted(train["movie_id"].unique())

    user_to_index = {
        value: i for i, value in enumerate(user_ids)
    }
    movie_to_index = {
        value: i for i, value in enumerate(movie_ids)
    }

    # Keep only users and movies represented in training.
    train = train[
        train["user_id"].isin(user_to_index)
        & train["movie_id"].isin(movie_to_index)
    ].copy()

    test = test[
        test["user_id"].isin(user_to_index)
        & test["movie_id"].isin(movie_to_index)
    ].copy()

    # Build the user-movie ratings matrix.
    user_indices = train["user_id"].map(user_to_index).to_numpy()
    movie_indices = train["movie_id"].map(movie_to_index).to_numpy()

    matrix = np.zeros(
        (len(user_ids), len(movie_ids)),
        dtype=np.float32,
    )

    matrix[user_indices, movie_indices] = (
        train["rating"].to_numpy()
    )

    # Calculate movie-to-movie cosine similarities.
    print("Calculating movie similarities...")

    similarity = cosine_similarity(matrix.T)

    global_mean = train["rating"].mean()

    # Baseline: predict the global average for every test rating.
    y_true = test["rating"].to_numpy()
    baseline_predictions = np.full(
        len(test),
        global_mean,
        dtype=np.float32,
    )

    # Predict ratings using movies the user has already rated.
    predictions = []

    for row in test.itertuples(index=False):
        user_index = user_to_index[row.user_id]
        movie_index = movie_to_index[row.movie_id]

        user_ratings = matrix[user_index]
        rated = user_ratings > 0

        weights = similarity[movie_index, rated]
        values = user_ratings[rated]

        if len(values) == 0 or np.abs(weights).sum() == 0:
            prediction = global_mean
        else:
            prediction = np.average(
                values,
                weights=np.abs(weights),
            )

        predictions.append(
            float(np.clip(prediction, 1, 5))
        )

    # Evaluate both approaches on the same test set.
    baseline_mae = mean_absolute_error(
        y_true,
        baseline_predictions,
    )
    baseline_rmse = np.sqrt(
        mean_squared_error(y_true, baseline_predictions)
    )

    model_mae = mean_absolute_error(
        y_true,
        predictions,
    )
    model_rmse = np.sqrt(
        mean_squared_error(y_true, predictions)
    )

    print("\n=== RecommendAI Evaluation ===")
    print(f"Training ratings: {len(train):,}")
    print(f"Test ratings:     {len(test):,}")
    print(f"Global mean:      {global_mean:.3f}")

    print("\nMetric comparison (lower is better):")
    print(f"Global baseline MAE:  {baseline_mae:.4f}")
    print(f"Model MAE:            {model_mae:.4f}")
    print(f"Global baseline RMSE: {baseline_rmse:.4f}")
    print(f"Model RMSE:           {model_rmse:.4f}")


if __name__ == "__main__":
    main()