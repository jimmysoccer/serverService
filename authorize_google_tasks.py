"""Create or replace the local Google Tasks OAuth token."""

from app.routers.canvas_sync.canvas_route import TOKEN_PATH, authorize_google


if __name__ == "__main__":
    authorize_google()
    print(f"Google Tasks authorization saved to {TOKEN_PATH}")
