import os

import uvicorn


def run_app() -> None:
    env = os.getenv("ENV", "prod")
    use_web_concurrency = "WEB_CONCURRENCY" in os.environ
    options = {
        "host": os.environ.get("GUNICORN_HOST", "0.0.0.0"),  # noqa: S104
        "port": os.environ.get("GUNICORN_PORT", 8000),  # noqa: WPS432
        "log_level": os.getenv("LOG_LEVEL", "debug").lower(),
        "workers": os.getenv("WEB_CONCURRENCY") if use_web_concurrency else 3,
        "reload": env == "development",
        "debug": env == "development",
    }

    uvicorn.run("deps_documents.app:create_app", **options)
