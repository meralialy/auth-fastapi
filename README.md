# Auth FastAPI

A lightweight FastAPI authentication service with user registration, JWT login, logout token revocation, and protected user profile access. The project is designed to run locally and can also be mounted in a Cloudflare Workers ASGI runtime.

## Requirements

- Python 3.10+
- `uv` for dependency management and execution

## Running the App

Start the development server with the Makefile:

```bash
make dev
```

Or run it directly:

```bash
PYTHONPATH=src fastapi dev src/main.py
```

## Code Quality & Linting

This project uses Ruff for linting and formatting:

```bash
# Run lint checks
make lint

# Check formatting
make format
```

## Building and Deploying

Build and deploy to Cloudflare Workers:

```bash
make clean-deploy
```

Or run steps individually:

```bash
make build
make deploy
```

## CI/CD Pipeline

The GitHub Actions workflow is organized into separate stages:
1. `lint` — runs Ruff checks
2. `format` — validates formatting
3. `build` — builds the Cloudflare Worker package
4. `deploy` — deploys to Cloudflare when the earlier stages pass

## API Endpoints

### System
- `GET /` — welcome message
- `GET /version` — app version and timestamp

### Auth (`/api/v1/auth`)
- `POST /api/v1/auth/register` — register a new user
  - body: `firstName`, `lastName`, `email`, `password`
- `POST /api/v1/auth/login` — authenticate and receive a JWT access token
  - body: `email`, `password`
- `POST /api/v1/auth/logout` — revoke the current bearer token
  - requires `Authorization: Bearer <token>`

### Users (`/api/v1/users`)
- `GET /api/v1/users/me` — fetch the authenticated user's profile
  - requires `Authorization: Bearer <token>`

## Project Structure

```text
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD pipeline
├── src/
│   ├── config.py                # App secrets and JWT settings
│   ├── database.py              # In-memory user + revoked-token storage
│   ├── dependencies.py          # Auth guard dependency
│   ├── main.py                  # FastAPI app bootstrap and middleware
│   ├── security.py              # Password hashing and JWT generation
│   ├── schemas.py               # Request/response validation models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── system.py            # System routes: /, /version
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py          # Register/login/logout routes
│   │       └── users.py         # Authenticated profile route
│   └── __init__.py
├── pyproject.toml               # Project metadata and Ruff config
├── wrangler.toml                # Cloudflare Worker config
├── Makefile                     # Dev/build/deploy automation
├── README.md                    # Project documentation
├── .gitignore                   # Ignore rules
├── .python-version              # Python version pin (if present)
└── .github/                     # GitHub automation files
```

This keeps the project organized in a simple, feature-oriented layout and makes the repo structure easier to scan at a glance.

## Notes

This project currently uses an in-memory user store for demonstration and local development. The auth state is not persistent across server restarts or multiple worker instances, so it is best suited for prototype or stateless local use unless replaced with a proper database or external identity backend.



