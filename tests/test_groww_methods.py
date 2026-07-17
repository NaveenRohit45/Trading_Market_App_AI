import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from growwapi import GrowwAPI

from backend.config import settings



token = GrowwAPI.get_access_token(
    api_key=settings.groww_api_key,
    secret=settings.groww_api_secret,
)

client = GrowwAPI(token)

print("=" * 50)
print("GrowwAPI Methods")
print("=" * 50)

for method in dir(client):

    if not method.startswith("_"):

        print(method)