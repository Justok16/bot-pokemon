import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def envoyer_alerte(message):
    """Envoie un message sur votre Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    reponse = requests.post(url, data=data)
    if reponse.status_code == 200:
        print("✅ Message envoyé sur Telegram !")
    else:
        print(f"❌ Erreur : {reponse.status_code}")
        print(reponse.text)


# --- TEST ---
print("📲 Envoi d'une alerte de test sur Telegram...\n")

message_test = (
    "🎯 <b>BONNE AFFAIRE DÉTECTÉE !</b>\n\n"
    "🃏 <b>Dracaufeu ex 199/165</b> — Série 151\n"
    "📊 Cote médiane : <b>350 €</b>\n"
    "💰 Prix trouvé : <b>310 €</b>\n"
    "📉 <b>-11%</b> sous la cote ✅\n"
    "🏪 Source : eBay\n\n"
    "🔗 <a href='https://www.ebay.fr'>Voir l'annonce</a>\n\n"
    "<i>(Ceci est un message de test 🧪)</i>"
)

envoyer_alerte(message_test)
print("\n🎉 Test terminé ! Vérifiez votre Telegram 📱")
