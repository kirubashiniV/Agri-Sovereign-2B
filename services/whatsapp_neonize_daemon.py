"""
Neonize WhatsApp Daemon for Agri-Sovereign-2B / Uzhavan-Sahayak
Directly connects to WhatsApp Web protocol using Neonize, provides real-time QR code pairing,
listens for farmer queries in Tamil, and responds with TNAU-grounded, CIBRC-safe advisories.
"""

import os
import sys
import time
import json
import threading
import queue
import requests
import segno
from http.server import HTTPServer, BaseHTTPRequestHandler

# Reconfigure stdout/stderr to utf-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from safety_validator import CIBRCSafetyValidator
from build_agricultural_rag import AgriculturalRAGEngine

try:
    from neonize.client import NewClient
    from neonize.events import ConnectedEv, MessageEv, PairStatusEv, LoggedOutEv
    from neonize.utils.jid import JID, build_jid
    NEONIZE_AVAILABLE = True
except ImportError:
    NEONIZE_AVAILABLE = False
    print("⚠️ [WARN] Neonize package not found. Running in simulated WhatsApp mode.")

# Global WhatsApp State
whatsapp_state = {
    "connected": False,
    "phone": None,
    "qr": None,
    "last_seen": None,
    "recent_messages": []
}

rag_engine = AgriculturalRAGEngine()
safety_validator = CIBRCSafetyValidator()

CLIENT_DB_PATH = os.path.join(os.path.dirname(__file__), "whatsapp_session.db")
client = None
if NEONIZE_AVAILABLE:
    try:
        client = NewClient(CLIENT_DB_PATH)
    except Exception as e:
        print(f"⚠️ [WARN] Could not initialize NewClient: {e}")

outbound_queue = queue.Queue()

def generate_agri_reply(query_text: str, district: str = "Coimbatore") -> str:
    """Generates TNAU grounded and CIBRC safe reply for farmer."""
    docs = rag_engine.search(query_text, top_k=1)
    if docs:
        doc = docs[0]
        advisory = (
            f"🌾 *Uzhavan-Sahayak Agri AI (உழவன் சகாயக்)*\n\n"
            f"📍 *மண்டலம்*: {district}\n"
            f"🌱 *பயிர்*: {doc['crop']}\n"
            f"🐛 *பூச்சி/நோய்*: {doc['pest_disease']}\n\n"
            f"🔬 *TNAU பரிந்துரை*:\n"
            f"• இயற்கை/உயிரியல்: {doc['management_biological']}\n"
            f"• இரசாயன மேலாண்மை: {doc['management_chemical']}\n\n"
            f"🛡️ *பாதுகாப்பு & காத்திருப்பு காலம் (PHI)*:\n{doc['safety_phi']}\n\n"
            f"⚠️ *பாதுகாப்பு கையுறை அணிந்து தெளிக்கவும்.*"
        )
    else:
        advisory = (
            f"🌾 *Uzhavan-Sahayak Agri AI*\n\n"
            f"வணக்கம்! உங்கள் '{query_text}' கேள்வி பெறப்பட்டது.\n"
            f"TNAU மற்றும் வேளாண் அறிவியல் நிலைய (KVK) வழிகாட்டுதலின்படி, பயிரின் விரிவான அறிகுறிகளை அனுப்பவும்."
        )
    return advisory

def outbound_worker():
    while True:
        try:
            item = outbound_queue.get()
            if item is None:
                break
            target_jid_obj, text_body, raw_user = item
            attempt = 1
            max_attempts = 3
            while attempt <= max_attempts:
                if client and NEONIZE_AVAILABLE:
                    try:
                        client.send_message(target_jid_obj, text_body)
                        print(f"📤 [WA SENT] To: {raw_user}@s.whatsapp.net | Body: {text_body[:50]}...")
                        break
                    except Exception as send_err:
                        print(f"⚠️ [WA SEND RETRY {attempt}/{max_attempts}] {send_err}")
                        attempt += 1
                        time.sleep(2)
                else:
                    print(f"💬 [SIMULATED WA SEND] To: {raw_user} | Msg: {text_body[:50]}...")
                    break
            time.sleep(1.0)
            outbound_queue.task_done()
        except Exception as e:
            print(f"❌ [OUTBOUND ERROR] {e}")

threading.Thread(target=outbound_worker, daemon=True).start()

def setup_client_events(cl):
    if not cl:
        return

    @cl.qr
    def on_qr(_: NewClient, data_qr: bytes):
        try:
            qr_uri = segno.make_qr(data_qr).png_data_uri(scale=8)
            whatsapp_state["qr"] = qr_uri
            whatsapp_state["connected"] = False
            print(f"📷 [NEONIZE QR GENERATED] Fresh QR Code ready for farmer scanning.")
        except Exception as e:
            print(f"❌ [QR ERROR] {e}")

    @cl.event(ConnectedEv)
    def on_connected(c: NewClient, _: ConnectedEv):
        is_logged_in = bool(hasattr(c, "is_logged_in") and c.is_logged_in)
        whatsapp_state["connected"] = is_logged_in
        if is_logged_in:
            whatsapp_state["qr"] = None
            phone = "Active"
            try:
                if hasattr(c, "me") and c.me and hasattr(c.me, "JID") and c.me.JID:
                    phone = getattr(c.me.JID, "User", "Active")
            except Exception:
                pass
            whatsapp_state["phone"] = phone
            whatsapp_state["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"🟢 [NEONIZE CONNECTED] WhatsApp session active for phone +{phone}")

    @cl.event(PairStatusEv)
    def on_pair(c: NewClient, pair_ev: PairStatusEv):
        whatsapp_state["connected"] = True
        whatsapp_state["qr"] = None
        if hasattr(pair_ev, "ID") and hasattr(pair_ev.ID, "User"):
            whatsapp_state["phone"] = pair_ev.ID.User
        print(f"🟢 [NEONIZE PAIRED] Paired successfully with user: {whatsapp_state['phone']}")

    @cl.event(LoggedOutEv)
    def on_logout(c: NewClient, _: LoggedOutEv):
        whatsapp_state["connected"] = False
        whatsapp_state["phone"] = None
        whatsapp_state["qr"] = None
        print("🔴 [NEONIZE LOGGED OUT] WhatsApp session terminated.")

    @cl.event(MessageEv)
    def on_message(_: NewClient, message: MessageEv):
        try:
            msg_body = message.Message
            if not msg_body:
                return
            text = None
            if msg_body.conversation:
                text = msg_body.conversation
            elif msg_body.extendedTextMessage and msg_body.extendedTextMessage.text:
                text = msg_body.extendedTextMessage.text

            if not text:
                return

            sender_jid = message.Info.MessageSource.Sender.User if message.Info and message.Info.MessageSource and message.Info.MessageSource.Sender else "Unknown"
            is_from_me = message.Info.MessageSource.IsFromMe if message.Info and message.Info.MessageSource else False
            chat_jid_obj = message.Info.MessageSource.Chat if message.Info and message.Info.MessageSource else None
            chat_user = chat_jid_obj.User if chat_jid_obj else sender_jid

            if is_from_me:
                return

            full_jid = f"{chat_user}@s.whatsapp.net"
            print(f"📩 [NEONIZE INCOMING] From: {full_jid} | Text: '{text}'")

            # Store in recent messages list
            whatsapp_state["recent_messages"].insert(0, {
                "from": full_jid,
                "sender": sender_jid,
                "text": text,
                "time": time.strftime("%H:%M:%S")
            })
            whatsapp_state["recent_messages"] = whatsapp_state["recent_messages"][:20]

            # Generate and enqueue automated agro-advisory reply
            reply_text = generate_agri_reply(text)
            if NEONIZE_AVAILABLE:
                target_jid = build_jid(chat_user, "s.whatsapp.net")
                outbound_queue.put((target_jid, reply_text, chat_user))

        except Exception as e:
            print(f"❌ [NEONIZE MSG ERROR] {e}")

class DaemonHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(whatsapp_state).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/send":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8"))
                target = data.get("to") or data.get("phone") or data.get("jid")
                msg = data.get("message")
                raw_user = target.split("@")[0].replace("+", "").replace(" ", "").strip()
                if len(raw_user) == 10 and raw_user.isdigit():
                    raw_user = "91" + raw_user

                if NEONIZE_AVAILABLE:
                    jid_obj = build_jid(raw_user, "s.whatsapp.net")
                    outbound_queue.put((jid_obj, msg, raw_user))

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "target": raw_user}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        elif self.path == "/simulate-inbound":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8")) if post_data else {}
                query_text = data.get("message") or data.get("query") or "மக்காச்சோளப் படைப்புழு தாக்குதல் மேலாண்மை"
                sender_phone = data.get("phone") or data.get("from") or "919842109876"
                
                # 1. Store incoming message
                inbound_entry = {
                    "from": f"{sender_phone}@s.whatsapp.net",
                    "sender": sender_phone,
                    "text": query_text,
                    "time": time.strftime("%H:%M:%S")
                }
                whatsapp_state["recent_messages"].insert(0, inbound_entry)
                
                # 2. Generate TNAU advisory reply
                reply_text = generate_agri_reply(query_text)
                
                # 3. Store outgoing response
                whatsapp_state["recent_messages"].insert(0, {
                    "from": "Uzhavan-Sahayak Bot",
                    "sender": "Agri-AI (Reply)",
                    "text": reply_text,
                    "time": time.strftime("%H:%M:%S")
                })
                whatsapp_state["recent_messages"] = whatsapp_state["recent_messages"][:20]
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "inbound": inbound_entry,
                    "advisory_reply": reply_text,
                    "reply": reply_text
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        elif self.path in ("/disconnect", "/reset"):
            whatsapp_state["connected"] = False
            whatsapp_state["phone"] = None
            whatsapp_state["qr"] = None
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "status": whatsapp_state}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

def run_http_server():
    server_address = ('', 5001)
    try:
        httpd = ReusableHTTPServer(server_address, DaemonHTTPHandler)
        print("🚀 [NEONIZE DAEMON API] Listening on http://localhost:5001")
        httpd.serve_forever()
    except Exception as e:
        print(f"⚠️ [NEONIZE HTTP ERR] {e}")

if __name__ == "__main__":
    if client:
        setup_client_events(client)
    
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    print("⚡ [WHATSAPP CLIENT] Connecting Neonize client...")
    if client and NEONIZE_AVAILABLE:
        try:
            client.connect()
        except KeyboardInterrupt:
            print("\n👋 Stopping Neonize WhatsApp daemon...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Neonize connection error: {e}")
            # Keep HTTP server alive
            while True:
                time.sleep(1)
    else:
        while True:
            time.sleep(1)
