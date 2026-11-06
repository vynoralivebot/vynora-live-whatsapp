import os
import json
import hmac
import hashlib
import logging
from typing import Any

import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from database import save_whatsapp_user

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("vynora-whatsapp")

app = FastAPI(title="Vynora Live WhatsApp", version="0.2.0")

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
GRAPH_VERSION = os.getenv("WHATSAPP_GRAPH_API_VERSION", "v23.0")


@app.get("/")
async def home():
    return {
        "service": "Vynora Live WhatsApp",
        "status": "running",
        "database": "configured" if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SECRET_KEY") else "not_configured",
        "webhook": "/webhook",
    }


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and VERIFY_TOKEN and token == VERIFY_TOKEN and challenge:
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


def send_whatsapp_text(to: str, body: str) -> None:
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        logger.error("Missing WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID")
        return
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    if not response.ok:
        logger.error("WhatsApp API error %s: %s", response.status_code, response.text)
        response.raise_for_status()


def send_main_menu(to: str) -> None:
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        logger.error("Missing WhatsApp API credentials")
        return
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "Vynora Live"},
            "body": {"text": "Welcome to Vynora Live ❤️\nChoose what you want to do."},
            "footer": {"text": "Private 1-to-1 video calls"},
            "action": {
                "button": "Open Menu",
                "sections": [{
                    "title": "Main Menu",
                    "rows": [
                        {"id": "book_call", "title": "Book a Call", "description": "Book a private video call"},
                        {"id": "view_hosts", "title": "Real Hosts", "description": "Explore available hosts"},
                        {"id": "wallet", "title": "Wallet / Recharge", "description": "Wallet and coin recharge"},
                        {"id": "my_bookings", "title": "My Bookings", "description": "View your bookings"},
                        {"id": "support", "title": "Support", "description": "Get help from our team"},
                    ],
                }],
            },
        },
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    if not response.ok:
        logger.error("WhatsApp menu error %s: %s", response.status_code, response.text)
        response.raise_for_status()


def valid_signature(raw_body: bytes, signature: str) -> bool:
    if not APP_SECRET:
        return False
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")


def handle_incoming_message(message: dict[str, Any]) -> None:
    sender = message.get("from")
    if not sender:
        return

    # Save each WhatsApp sender as a user; repeated messages update the same row.
    try:
        save_whatsapp_user(sender)
    except Exception:
        logger.exception("Could not save WhatsApp user in Supabase")

    message_type = message.get("type")
    if message_type == "text":
        incoming = message.get("text", {}).get("body", "").strip().lower()
        if incoming in {"hi", "hello", "hey", "start", "menu", "namaste", "नमस्ते"}:
            send_main_menu(sender)
        else:
            send_whatsapp_text(sender, "Vynora Live में आपका स्वागत है ❤️\nMenu खोलने के लिए HI लिखें।")
        return

    if message_type == "interactive":
        interactive = message.get("interactive", {})
        selected = (
            interactive.get("list_reply", {}).get("id")
            or interactive.get("button_reply", {}).get("id")
        )
        replies = {
            "book_call": "Booking module अगले development चरण में जोड़ा जाएगा।",
            "view_hosts": "Hosts की live listing अगले development चरण में जोड़ी जाएगी।",
            "wallet": "Wallet और recharge module अगले development चरण में जोड़ा जाएगा।",
            "my_bookings": "My Bookings अगले development चरण में जोड़ा जाएगा।",
            "support": "Support के लिए कृपया अपना सवाल यहाँ लिखें।",
        }
        send_whatsapp_text(sender, replies.get(selected, "Menu खोलने के लिए HI लिखें।"))
        return

    send_whatsapp_text(sender, "Menu खोलने के लिए HI लिखें।")


@app.post("/webhook")
async def receive_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not valid_signature(raw_body, signature):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(status_code=400, detail="Invalid JSON")

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                try:
                    handle_incoming_message(message)
                except requests.RequestException:
                    logger.exception("Could not send WhatsApp reply")
                except Exception:
                    logger.exception("Could not process incoming WhatsApp message")

    return {"ok": True}
