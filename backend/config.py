from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env", override=True)

print("BASE_DIR:", BASE_DIR)
print("ENV FILE:", BASE_DIR / ".env")
print("ENV EXISTS:", (BASE_DIR / ".env").exists())
print("APP_MODE RAW:", os.getenv("APP_MODE"))

class Settings(BaseModel):

    app_mode: str = os.getenv(
        "APP_MODE",
        "DEMO"
    ).upper()

    groww_api_key: str = os.getenv(
        "GROWW_API_KEY",
        ""
    )

    groww_api_secret: str = os.getenv(
        "GROWW_API_SECRET",
        ""
    )

    finnhub_api_key: str = os.getenv(
        "FINNHUB_API_KEY",
        ""
    )

    anthropic_api_key: str = os.getenv(
        "ANTHROPIC_API_KEY",
        ""
    )

    poll_seconds: int = int(
        os.getenv(
            "POLL_SECONDS",
            "3"
        )
    )

    prediction_interval_seconds: int = int(
        os.getenv(
            "PREDICTION_INTERVAL_SECONDS",
            "180"
        )
    )

    db_path: Path = BASE_DIR / os.getenv(
        "DB_PATH",
        "data/market_intelligence.db"
    )


settings = Settings()