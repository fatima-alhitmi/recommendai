# RecommendAI

A personalized movie recommendation platform built with Python, FastAPI, and React. RecommendAI analyzes historical movie ratings and genre preferences to rank movie suggestions for individual users.

## Overview

The application combines movie-rating statistics, user genre preferences, and popularity signals to generate personalized recommendations using the MovieLens 1M dataset. A React frontend provides movie discovery, search, and user-specific recommendations through a FastAPI backend.

## Features

- Personalized movie recommendations based on historical user ratings
- Genre preference scoring
- Weighted movie ratings to account for differences in rating counts
- Popularity-aware recommendation ranking
- Explanations accompanying personalized recommendations
- Movie discovery and search by title or genre
- REST API with interactive documentation

## Technology Stack

- **Backend:** Python, FastAPI, Pandas, Pydantic
- **Frontend:** React, Vite, JavaScript, CSS
- **Dataset:** MovieLens 1M
- **Version control:** Git and GitHub

## Recommendation Method

The API ranks candidate movies using a combined score:

`Score = Weighted Rating + 0.15 × Genre Preference Score + 0.1 × Popularity Bonus`

Genre preferences are estimated from the user's historical ratings. Movies the user has already rated are excluded from the recommendation candidates. The popularity bonus is capped to limit its influence.

The score is a ranking value, not a predicted rating or a probability of user satisfaction.

## Dataset

The MovieLens 1M dataset contains 1,000,209 ratings across 3,883 movies, contributed by approximately 6,000 users.

Dataset: [GroupLens MovieLens 1M](https://grouplens.org/datasets/movielens/1m/)

The dataset is not included in this repository. Download and extract it into `data/ml-1m/`. The backend requires `ratings.dat` and `movies.dat`.

## Evaluation

A separate experiment in `evaluate.py` compared a global-average rating baseline with an evaluation model using a held-out test set.

| Metric | Global Baseline | Evaluation Model |
|---|---:|---:|
| MAE | 0.9359 | 0.8007 |
| RMSE | 1.1196 | 1.0056 |

The experiment used 800,167 training ratings and 200,016 test ratings. The evaluation model achieved lower MAE and RMSE than the baseline.

These results describe the separate rating-prediction experiment and are not measurements of the current API ranking algorithm.

## Installation and Usage

### Requirements

- Python 3
- Node.js and npm
- MovieLens 1M dataset

### 1. Clone the repository

```bash
git clone https://github.com/fatima-alhitmi/recommendai.git
cd recommendai
```

### 2. Download the dataset

Download MovieLens 1M from GroupLens and extract the files into `data/ml-1m/`.

### 3. Start the backend

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install fastapi "uvicorn[standard]" pandas
uvicorn backend.main:app --reload
```

API documentation: http://127.0.0.1:8000/docs

### 4. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally http://localhost:5173/.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status and dataset statistics |
| GET | `/movies/popular` | Retrieve popular movies |
| POST | `/recommend` | Generate personalized recommendations |
| GET | `/users/{user_id}/ratings` | Retrieve a user's ratings |

Example request to `POST /recommend`:

```json
{
  "user_id": 1,
  "limit": 10
}
```

## Project Structure

```text
recommendai/
├── backend/
│   └── main.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── index.html
├── data/ml-1m/       # Download separately
├── evaluate.py
├── inspect_data.py
├── recommender.py
└── README.md
```

## Future Work

- Integrate item-item collaborative filtering into the live recommendation API
- Evaluate ranking quality using Precision@K and Recall@K
- Add user accounts and saved movie lists
- Integrate movie posters and additional metadata
- Deploy the application online

## Author

**Fatima Al-Hitmi**  
[GitHub Profile](https://github.com/fatima-alhitmi)
