from fastapi import FastAPI, Request
from datetime import datetime, timedelta

app = FastAPI()

# ==== CONFIGURATION ====
YOUTUBE_LINK = "https://get.thepremiumadvantage.com/podcastguest"
RAFFLE_LINK = "https://get.thepremiumadvantage.com/opt-in-page"
EVENTS_LINK = "https://xiexiemedia.com/events-1"
DISCOVERY_LINK = "https://get.thepremiumadvantage.com/discoveryappt"
SUBSCRIBERS_TXT = "16,900"
NEXT_DATE_TXT = "Friday, October 24"
SENDER_NAME = "Roberto Coello"
SENDER_BLOCK = (
    "The Premium Advantage | Xie Xie Media\n"
    "info@mypremium.site • Text/Call 832-770-7458"
)

# ==== EMAIL TEMPLATES ====
def case1_email(first_name: str, event_name: str):
    subject = "Feature Your Houston Business – Free In-Person YouTube Episode at The ION"
    body = f"""Morning {first_name},

It was great meeting you at {event_name}. As promised, here’s the link to join us as a featured Houston business owner or special guest for our in-person YouTube episode at The ION:
👉 {YOUTUBE_LINK}

Next open date: {NEXT_DATE_TXT}
We’re now at {SUBSCRIBERS_TXT} subscribers—great free exposure in a professional setting.

Stay in the loop:
• Weekly raffle & newsletter: {RAFFLE_LINK}

For questions or RSVP help, email info@mypremium.site or text/call 832-770-7458.

Best,
{SENDER_NAME}
{SENDER_BLOCK}
"""
    sms = (
        f"Morning {first_name} — Roberto here. Free in-person YouTube episode @ The ION. "
        f"Next: {NEXT_DATE_TXT}. Sign up: {YOUTUBE_LINK}. Questions? Text 832-770-7458"
    )
    return subject, body, sms


def case2_email(first_name: str, event_name: str):
    subject = "FREE In-Person YouTube Business Episode @ The ION – Sign-Up Link & Info"
    body = f"""Morning {first_name},

Great meeting you at {event_name}. Share with your team to review and register as a Houston business owner, sales manager, marketing rep, or special guest for our LIVE in-person Friday YouTube Episodes at The ION:
👉 {YOUTUBE_LINK}

We currently have:
• 2 on-screen guest spots per episode
• Up to 15 audience seats
• Next open date: {NEXT_DATE_TXT}
Our community is {SUBSCRIBERS_TXT} subscribers strong.

More free resources:
• Weekly raffle & newsletter: {RAFFLE_LINK}
• Free community events: {EVENTS_LINK}
• Free discovery appointments (about our programs): {DISCOVERY_LINK}

For questions or RSVP help, email info@mypremium.site or text/call 832-770-7458.

Warm regards,
{SENDER_NAME}
{SENDER_BLOCK}
"""
    sms = (
        f"Reminder: {NEXT_DATE_TXT} ION episode — 2 guest spots, 15 audience seats. "
        f"Register: {YOUTUBE_LINK}. Questions? Text 832-770-7458"
    )
    return subject, body, sms


# ==== DECISION RULE ====
def choose_case(contact: dict) -> str:
    """
    Returns 'case1' or 'case2'.
    Rules:
      - If source mentions 'chamber' or 'networking' → Case 1 (credibility)
      - If contact tags include 'info' or source mentions 'details' → Case 2 (resources)
    """
    src = (contact.get("source") or contact.get("notes") or "").lower()
    tags = [t.lower() for t in contact.get("tags", [])]
    if "info" in tags or "details" in src:
        return "case2"
    if "chamber" in src or "network" in src:
        return "case1"
    # Default to informative Case 2
    return "case2"


# ==== API ENDPOINT ====
@app.post("/followup")
async def followup(request: Request):
    payload = await request.json()
    contact = payload.get("contact", {})
    first_name = contact.get("first_name") or "there"
    event_name = contact.get("event_name") or "the event"

    chosen = choose_case(contact)
    if chosen == "case1":
        subject, email_body, sms_body = case1_email(first_name, event_name)
        tag = "Engage:Case1"
    else:
        subject, email_body, sms_body = case2_email(first_name, event_name)
        tag = "Engage:Case2"

    next_followup = (datetime.utcnow() + timedelta(days=3)).isoformat()

    return {
        "template": chosen,
        "add_tags": [tag, "FollowUp:Sent"],
        "next_followup_date": next_followup,
        "email_subject": subject,
        "email_body": email_body,
        "sms_body": sms_body
    }
