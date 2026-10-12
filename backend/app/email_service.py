"""Sending email.

DEV MODE  (SMTP_HOST empty in .env): emails are saved as .eml files in backend/outbox/ - open them to see
          exactly what would be sent. No account needed.
LIVE MODE (SMTP_HOST set): emails go through your SMTP server (Gmail app password, Brevo, SendGrid, etc.).
"""
import logging
import smtplib
import ssl
import time
from email.message import EmailMessage
from html import escape
from pathlib import Path

from . import config

log = logging.getLogger(__name__)
OUTBOX = Path(__file__).resolve().parent.parent / "outbox"


def send_email(to: str, subject: str, text: str, html: str | None = None) -> str:
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = config.SMTP_FROM, to, subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")
    if not config.SMTP_HOST:
        if config.APP_ENV == "production":
            log.warning("SMTP_HOST not set in production. Email to %s skipped.", to)
            return "skipped_no_smtp"
        # DEV MODE: save to local outbox
        OUTBOX.mkdir(exist_ok=True)
        name = f"{int(time.time() * 1000)}_{to.replace('@', '_at_')}.eml"
        (OUTBOX / name).write_bytes(bytes(msg))
        return "saved_to_outbox"
    try:                                                       # LIVE MODE
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as s:
            if config.SMTP_TLS:
                s.starttls(context=ssl.create_default_context())
            if config.SMTP_USER:
                s.login(config.SMTP_USER, config.SMTP_PASSWORD)
            s.send_message(msg)
        return "sent"
    except Exception:
        log.exception("Could not send email to %s", to)
        return "failed"


def build_match_email(recipient_name: str, other: dict, percent: float, reasons: list[str],
                      shared_tags: list[str], shared_projects: list[str], app_url: str) -> tuple[str, str, str]:
    """Return (subject, plain_text, html). `other` has: name, organization, department, domain,
    and optionally email (only included when the other person agreed to be contactable)."""
    subject = f"ResearchConnect: you have a {round(percent)}% research match with {other['name']}"
    contact = (f"Contact: {other['email']}" if other.get("email")
               else "Contact: log in to ResearchConnect and send a collaboration request.")
    lines = [f"Hello {recipient_name},", "",
             f"ResearchConnect found a research match for you: {other['name']} "
             f"({other.get('department') or 'department not set'}, {other['organization']}).",
             f"Match score: {round(percent)}%", ""]
    if other.get("domain"):
        lines.append(f"Research domain: {other['domain']}")
    lines.append("Why you match:")
    lines += [f"  - {r}" for r in reasons]
    if shared_tags:
        lines.append("Shared topics and skills: " + ", ".join(shared_tags[:8]))
    if shared_projects:
        lines.append("Their related projects: " + "; ".join(shared_projects[:3]))
    lines += ["", contact, f"View and connect: {app_url}", "",
              "You receive this because email alerts are on in your profile. You can turn them off there.",
              "- ResearchConnect"]
    text = "\n".join(lines)

    e = escape
    li = "".join(f"<li>{e(r)}</li>" for r in reasons)
    tags = "".join(f"<span style='background:#e5eff6;border-radius:12px;padding:2px 8px;margin:2px;display:inline-block'>{e(t)}</span>"
                   for t in shared_tags[:8])
    projs = "".join(f"<li>{e(p)}</li>" for p in shared_projects[:3])
    contact_html = (f"<p><b>Contact:</b> {e(other['email'])}</p>" if other.get("email")
                    else "<p><b>Contact:</b> log in and send a collaboration request.</p>")
    html = f"""<div style="font-family:Arial,sans-serif;max-width:560px;color:#0f2438">
<h2 style="color:#0b3a5b">You have a new research match</h2>
<p>Hello {e(recipient_name)},</p>
<p><b>{e(other['name'])}</b> ({e(other.get('department') or 'department not set')}, {e(other['organization'])})
is a <b>{round(percent)}%</b> match for your work.</p>
{f"<p><b>Research domain:</b> {e(other['domain'])}</p>" if other.get('domain') else ""}
<p><b>Why you match</b></p><ul>{li}</ul>
{f"<p><b>Shared topics:</b> {tags}</p>" if tags else ""}
{f"<p><b>Their related projects</b></p><ul>{projs}</ul>" if projs else ""}
{contact_html}
<p><a href="{e(app_url)}" style="background:#0e8c82;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none">View and connect</a></p>
<p style="font-size:12px;color:#5b6c8f">You receive this because email alerts are on in your profile. You can turn them off there.</p>
</div>"""
    return subject, text, html
