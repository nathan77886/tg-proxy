from app import app, run_bot
from uvicorn import run
from threading import Thread


def start_app():
    run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    # start_app()
    Thread(target=start_app, daemon=True).start()
    run_bot()
