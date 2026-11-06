# Vynora Live WhatsApp Booking System

This is the separate WhatsApp implementation of Vynora Live. The existing Telegram application and its database must remain untouched.

## Current backend foundation

- FastAPI application for the WhatsApp Cloud API webhook.
- `GET /webhook` verifies Meta webhook subscriptions.
- `POST /webhook` receives incoming WhatsApp messages.
- Webhook requests are checked using Meta's SHA-256 signature.
- Sending `HI`, `HELLO`, `START`, or `MENU` opens the starter menu.
- Incoming WhatsApp phone numbers are saved in Supabase's `public.users` table.
- `GET /health` provides a basic health check.

## Project files

- `main.py` - FastAPI app and WhatsApp webhook.
- `database.py` - Supabase connection and user registration helper.
- `requirements.txt` - Python dependencies.
- `.env.example` - Names of required environment variables. It contains no real credentials.
- `supabase/schema.sql` - Initial database table definition.
- `Procfile` - Generic Python web start command.

## Setup steps

1. Create the Supabase project.
2. Open Supabase **SQL Editor** and run the contents of `supabase/schema.sql`.
3. Deploy this repository to a Python-compatible hosting provider.
4. Add the environment variables listed below in the hosting provider's Environment/Secrets settings.
5. In Meta Developer Dashboard, set the webhook callback URL to `https://YOUR-HOST/webhook`.
6. Use the same value for Meta's Verify Token and `WHATSAPP_VERIFY_TOKEN`.
7. Subscribe the WhatsApp webhook to the `messages` field.
8. Test by sending `HI` to the connected WhatsApp number.

## Required environment variables

- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_APP_SECRET`
- `WHATSAPP_GRAPH_API_VERSION` (the code has a default)
- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`

Optional:

- `LOG_LEVEL`

Never put real API tokens, app secrets, Supabase secret keys, database passwords, or customer data in GitHub. Add them only through your hosting provider's private Environment/Secrets settings.

Use the Supabase **Secret API key** only on the backend. Do not put it in browser-side code.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Business rules to preserve

- Do not change the existing booking prices: 1 minute = 50 coins; 2 minutes = 150 coins; 5 minutes = 300 coins; 10 minutes = 600 coins; 30 minutes = 1500 coins.
- Recharge plans: ₹50, ₹150, ₹300, ₹600, and ₹1500 for matching coin amounts.
- Host share is 60%; platform share is 40%.
- Minimum host withdrawal is ₹700.
- One free 10-second demo per user, recorded in the database.
- A paid-call timer starts only after both the user and host are confirmed connected in Agora.
- Pending bookings expire after 10 minutes and receive the applicable refund.
- Recharge approval must be idempotent: the same recharge must never credit coins twice.
- The Telegram project and its database must not be modified as part of this separate WhatsApp build.

## Development status

This repository currently contains the WhatsApp webhook starter and initial Supabase user-registration foundation. Booking, host management, wallet, recharge approvals, earnings, withdrawals, gifts, admin dashboard, and Agora call flows still need to be implemented and tested. Do not treat these modules as complete yet.
