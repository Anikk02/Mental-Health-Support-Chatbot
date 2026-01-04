# MentalChat Backend

## Setup
1. Create virtualenv:
   python -m venv .venv
   source .venv/bin/activate
2. Install:
   pip install -r requirements.txt
3. Set env vars:
   export MONGO_URI="mongodb://localhost:27017"
   export MODEL_PATH="./trained-mentalchat-model"
   export JWT_SECRET_KEY="change_me"
   export FRONTEND_BASE="http://localhost:3000"
   (OPTIONAL) SMTP_HOST, SMTP_USER, SMTP_PASS, FROM_EMAIL
4. Create indexes:
   python -m backend.app.indexes_setup
5. Run:
   uvicorn backend.app.main:app --reload --port 8000

## Notes
- Uses MongoDB (Motor)
- All ObjectId fields are used and converted when returning JSON
- Auth collections: users, auth_refresh_tokens, auth_verifications, auth_password_resets, auth_2fa, rate_limits
