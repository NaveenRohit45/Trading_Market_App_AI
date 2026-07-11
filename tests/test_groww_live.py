from growwapi import GrowwAPI

from backend.config import settings


print("=" * 60)
print("GROWW LIVE DATA TEST")
print("=" * 60)

access_token = GrowwAPI.get_access_token(
    api_key=settings.groww_api_key,
    secret=settings.groww_api_secret
)

groww = GrowwAPI(access_token)

print("✅ Connected to Groww")
print()
print("Available live-data methods:")

for name in dir(groww):
    if any(word in name.lower() for word in [
        "quote",
        "ltp",
        "instrument",
        "live"
    ]):
        print("  ", name)