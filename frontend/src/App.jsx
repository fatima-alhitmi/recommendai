
import { useEffect, useState } from 'react'
import './App.css'

const API = 'http://127.0.0.1:8000'

function MovieCard({ movie, index }) {
  const [posterFailed, setPosterFailed] = useState(false)

  function posterUrl() {
    return `https://placehold.co/300x440/172554/f8fafc?text=${encodeURIComponent(movie.title)}`
  }

  return (
    <article className="movie-card">
      <div className="poster-wrap">
        <img
          className="poster"
          src={
            posterFailed
              ? `https://placehold.co/300x440/172554/f8fafc?text=Movie+${index + 1}`
              : posterUrl()
          }
          alt={`${movie.title} poster`}
          loading="lazy"
          onError={() => setPosterFailed(true)}
        />

        <span className="poster-rating">
          ★ {Number(movie.average_rating || 0).toFixed(1)}
        </span>
      </div>

      <div className="movie-info">
        <h3>{movie.title.replace(/\s*\(\d{4}\)\s*$/, '')}</h3>

        <p className="movie-year">
          {movie.title.match(/\((\d{4})\)/)?.[1] || 'Movie'}
        </p>

        <p className="genres">
          {(movie.genres || '').replaceAll('|', ' · ')}
        </p>

        {movie.reason && (
          <p className="recommendation-reason">
            ✦ {movie.reason}
          </p>
        )}

        <div className="rating-line">
          <span>
            {movie.reason ? 'Personalized score' : 'RecommendAI score'}
          </span>
          <strong>
            {Number(
              movie.weighted_rating ??
              movie.score ??
              movie.average_rating ??
              0
            ).toFixed(2)}
          </strong>
        </div>
      </div>
    </article>
  )
}

function App() {
  const [popular, setPopular] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [userId, setUserId] = useState('1')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [recommendLoading, setRecommendLoading] = useState(false)
  const [error, setError] = useState('')
  const [recommendationUserId, setRecommendationUserId] = useState(null)

  async function loadPopular() {
    try {
      setLoading(true)
      setError('')

      const response = await fetch(`${API}/movies/popular?limit=50`)

      if (!response.ok) {
        throw new Error('Could not load popular movies.')
      }

      const data = await response.json()
      setPopular(data.movies || [])
    } catch {
      setError(
        'Could not connect to RecommendAI. Make sure your backend is running on port 8000.'
      )
    } finally {
      setLoading(false)
    }
  }

  async function loadRecommendations(event) {
    event?.preventDefault()

    const id = Number(userId)

    if (!Number.isInteger(id) || id < 1) {
      setError('Please enter a valid positive user ID.')
      return
    }

    try {
      setRecommendLoading(true)
      setError('')

      const response = await fetch(`${API}/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: id,
          limit: 10,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Could not get recommendations.'
        )
      }

      setRecommendations(data.recommendations || [])
      setRecommendationUserId(id)
    } catch (err) {
      setError(err.message || 'Could not load recommendations.')
      setRecommendations([])
      setRecommendationUserId(null)
    } finally {
      setRecommendLoading(false)
    }
  }

  useEffect(() => {
    loadPopular()
  }, [])

  const filteredMovies = popular.filter((movie) =>
    `${movie.title} ${movie.genres}`
      .toLowerCase()
      .includes(search.toLowerCase())
  )

  const shownRecommendations = recommendations.filter((movie) =>
    `${movie.title} ${movie.genres}`
      .toLowerCase()
      .includes(search.toLowerCase())
  )

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="RecommendAI home">
          <span className="brand-icon">▶</span>
          <span>
            Recommend<span className="brand-accent">AI</span>
          </span>
        </a>

        <nav>
          <a href="#discover">Discover</a>
          <a href="#for-you">For you</a>
        </nav>

        <div className="topbar-tag">
          <span className="live-dot" />
          MOVIE DISCOVERY, REIMAGINED
        </div>
      </header>

      <main>
        <section className="hero-section">
          <div className="hero-copy">
            <p className="eyebrow">
              <span>✦</span> YOUR NEXT FAVORITE FILM AWAITS
            </p>

            <h1>
              Less scrolling.
              <br />
              <span>More watching.</span>
            </h1>

            <p className="hero-description">
              Discover movies picked for your taste, powered by data
              and a little movie magic.
            </p>

            <a className="primary-button" href="#discover">
              Explore movies <span>↗</span>
            </a>

            <div className="hero-stats">
              <div>
                <strong>3,883</strong>
                <span>Movies to explore</span>
              </div>

              <div className="stat-divider" />

              <div>
                <strong>1M+</strong>
                <span>Ratings analyzed</span>
              </div>
            </div>
          </div>

          <div className="hero-art" aria-label="Cinema illustration">
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <div className="hero-glow" />
            <div className="floating-ticket">✦ YOUR NEXT WATCH</div>

            <div className="cinema-screen">
              <div className="screen-stars">✦　·　✧　·　✦</div>
              <div className="screen-mountain mountain-back" />
              <div className="screen-mountain mountain-front" />
              <div className="screen-sun" />
            </div>

            <div className="hero-filmstrip">
              RECOMMENDAI&nbsp; • &nbsp;DISCOVER SOMETHING NEW&nbsp; •
            </div>

            <span className="spark spark-one">✦</span>
            <span className="spark spark-two">✧</span>
          </div>
        </section>

        <section className="search-section" id="discover">
          <div>
            <p className="section-kicker">THE COLLECTION</p>
            <h2>
              Find your next <span>favorite</span>
            </h2>
            <p className="section-subtitle">
              Critically loved picks and hidden gems, all in one place.
            </p>
          </div>

          <label className="search-box">
            <span>⌕</span>
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search titles or genres..."
              aria-label="Search movies or genres"
            />
            <kbd>⌘ K</kbd>
          </label>
        </section>

        {error && (
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}

        <section className="movie-section">
          <div className="section-heading">
            <div>
              <span className="heading-mark">✦</span>
              <h2>Popular right now</h2>
            </div>
            <span className="result-count">
              {filteredMovies.length} MOVIES
            </span>
          </div>

          {loading ? (
            <div className="loading-state">
              Finding something good to watch<span>…</span>
            </div>
          ) : filteredMovies.length > 0 ? (
            <div className="movie-grid">
              {filteredMovies.slice(0, 20).map((movie, index) => (
                <MovieCard
                  key={movie.movie_id}
                  movie={movie}
                  index={index}
                />
              ))}
            </div>
          ) : (
            <p className="empty-state">
              No movies match your search. Try another title or genre.
            </p>
          )}
        </section>

        <section className="personal-section" id="for-you">
          <div className="personal-copy">
            <p className="section-kicker">MADE FOR YOUR TASTE</p>

            <h2>
              Your next obsession
              <br />
              is <span>closer than you think.</span>
            </h2>

            <p>
              Enter a MovieLens user ID to get recommendations based
              on their movie ratings and genre preferences.
            </p>

            <form
              className="recommend-form"
              onSubmit={loadRecommendations}
            >
              <label htmlFor="userId">MovieLens user ID</label>

              <div className="recommend-input-row">
                <input
                  id="userId"
                  type="number"
                  min="1"
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                  placeholder="e.g. 1"
                  required
                />

                <button type="submit" disabled={recommendLoading}>
                  {recommendLoading
                    ? 'Finding…'
                    : 'Find my movies →'}
                </button>
              </div>
            </form>
          </div>

          <div className="personal-symbol" aria-hidden="true">
            <div className="symbol-ring ring-a" />
            <div className="symbol-ring ring-b" />
            <div className="symbol-center">✦</div>
            <span className="symbol-dot dot-a" />
            <span className="symbol-dot dot-b" />
            <span className="symbol-dot dot-c" />
            <span className="symbol-dot dot-d" />
          </div>
        </section>

        {recommendations.length > 0 && (
          <section className="movie-section recommendation-results">
            <div className="section-heading">
              <div>
                <span className="heading-mark">✦</span>
                <h2>Picked for user {recommendationUserId}</h2>
              </div>

              <span className="result-count">
                {shownRecommendations.length} MATCHES
              </span>
            </div>

            {shownRecommendations.length > 0 ? (
              <div className="movie-grid">
                {shownRecommendations.map((movie, index) => (
                  <MovieCard
                    key={movie.movie_id}
                    movie={movie}
                    index={index}
                  />
                ))}
              </div>
            ) : (
              <p className="empty-state">
                No recommendations match your search. Try another title
                or genre.
              </p>
            )}
          </section>
        )}
      </main>

      <footer className="footer">
        <a className="brand" href="#">
          <span className="brand-icon">▶</span>
          <span>
            Recommend<span className="brand-accent">AI</span>
          </span>
        </a>

        <p>Made for movie lovers. Powered by data. ✦</p>
        <span>BUILT WITH MOVIELENS DATA</span>
      </footer>
    </div>
  )
}

export default App
