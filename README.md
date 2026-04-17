# TicTacToe FastAPI REST API

REST API for authenticated TicTacToe gameplay with persistent game state and move history.

## Features

- FastAPI app with JWT authentication (OAuth2 password flow)
- SQLAlchemy ORM persistence (PostgreSQL-ready)
- Full TicTacToe game logic:
  - move validation
  - win detection (rows, columns, diagonals)
  - draw detection
- Game history stored as ordered move list
- OpenAPI/Swagger documentation with endpoint descriptions and schema examples
- Pytest test suite for auth and game endpoints including edge cases

## Authentication

- Users must register and log in.
- All core game endpoints require Bearer JWT authentication.
- Token endpoint:
  - `POST /auth/login`

## Game State Model

- `board`: list with 9 entries (`"X"`, `"O"`, or `""`)
- `current_player`: `"X"` or `"O"`
- `status`: `"waiting"`, `"ongoing"`, `"won"`, `"draw"`
- `winner`: `"X"` / `"O"` / `null`
- `moves`: ordered list of `{ player, position }`

## API Endpoints

### Auth

- `POST /auth/register` - create user
- `POST /auth/login` - get access token
- `GET /auth/me` - get current user profile
- `PUT /auth/me` - update display name

### Games

- `POST /games` - create a new game
- `GET /games` - list current user's games with move history and status
- `GET /games/{game_id}` - get details of a specific game
- `PUT /games/{game_id}/move/{position}` - make a move (position 1-9)

Additional endpoints:

- `GET /games/available` - list games waiting for an opponent
- `POST /games/{game_id}/join` - join as player O
- `DELETE /games/{game_id}` - delete a completed game (`won` or `draw`)

## Error Handling

Move and game validation errors return HTTP 400 with clear messages, for example:

- `Invalid position`
- `Position already taken`
- `Not your turn`
- `Game is not in progress`

## Local Setup

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Run with PostgreSQL (Docker)

```bash
docker compose up --build
```

The app starts at `http://localhost:8000`.
PostgreSQL runs on `localhost:5432` and pgAdmin runs on `http://localhost:5050`.

pgAdmin login:

- email: `admin@example.com`
- password: `admin123`

Add a server in pgAdmin with:

- host: `db`
- port: `5432`
- user: `admin`
- password: `Kennwort1`
- database: `testuserdb`

### 3. Run locally without Docker

Copy [.env.example](.env.example) to `.env`, then adjust the connection values for your local PostgreSQL instance:

```bash
cp .env.example .env
```

Then run the app normally:

```bash
uvicorn src.main:app --reload
```

If `.env` is present, the app reads `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, and `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` from it. If not, it falls back to in-memory SQLite and default JWT settings.

## Database Notes

- Application runtime uses PostgreSQL when `DATABASE_URL` is set, either through Docker or a local `.env` file.
- The test suite still uses in-memory SQLite, so tests stay fast and isolated.

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with:

```bash
pytest
```

API endpoint tests include:

- successful auth and gameplay paths
- authentication failures (missing/invalid tokens)
- invalid moves (out-of-bounds, occupied position, wrong turn)
- win and draw scenarios

## Requirement Coverage

- FastAPI + auth: implemented with JWT/OAuth2 password flow
- CRUD game operations: create, update (moves), delete completed games
- Business logic: win/draw detection and invalid move handling
- Required endpoints: all implemented
- Unit testing: endpoint tests and edge-case tests included
- Documentation: OpenAPI + this README
- Code quality: modular structure (`api`, `crud`, `model`, `schema`, `utils`, `test`)