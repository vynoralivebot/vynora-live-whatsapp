# Vynora Live WhatsApp Booking System

This repository is the separate WhatsApp version of Vynora Live.

## Project separation
- The existing Telegram project remains unchanged and continues to run separately.
- This repository is for the new WhatsApp service only.

## Current files
- `main.py` - FastAPI WhatsApp webhook verification and starter menu.
- `requirements.txt` - Python packages required by the service.

## Current development status
The first WhatsApp connection layer is prepared:
- Webhook verification endpoint: `/webhook`
- Incoming WhatsApp message endpoint: `/webhook`
- `HI`, `HELLO`, or `MENU` opens the starter menu.
- Menu options are placeholders until the booking and account modules are connected.

## Planned modules
1. WhatsApp user registration and profile
2. Real host listing and host availability
3. Booking requests and accept/reject flow
4. Wallet and recharge with admin approval
5. Host earnings and withdrawal
6. Admin management
7. Agora video-call launch page
8. Database connection and secure user/host records

## Business rules to preserve
- Existing booking/recharge pricing must be confirmed against the original live project before implementation. Do not change prices during migration.
- Free demo duration: 10 seconds, once per user.
- Host share: 60%; platform share: 40%.
- Call timer starts only after both user and host are actually connected.
- Existing Telegram project and its database must not be deleted or modified during this separate build.

## Render deployment (after credentials are configured)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Environment variables
Configure secrets in Render Environment settings, not in GitHub:
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_APP_SECRET`
- `WHATSAPP_GRAPH_API_VERSION`

Never commit access tokens, app secrets, database passwords, or customer data to this repository.
