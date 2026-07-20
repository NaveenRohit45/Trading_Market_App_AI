import os
from dotenv import load_dotenv
import pyotp

load_dotenv()

secret = os.getenv("GROWW_API_SECRET", "")

print("Raw secret :", repr(secret))
print("Length     :", len(secret))

try:
    cleaned = secret.strip().strip('"').strip("'").replace(" ", "").replace("-", "").upper()

    print("Cleaned    :", repr(cleaned))
    print("Length     :", len(cleaned))

    otp = pyotp.TOTP(cleaned).now()
    print("✅ VALID")
    print("OTP:", otp)

except Exception as e:
    print("❌ INVALID")
    print(type(e).__name__)
    print(e)