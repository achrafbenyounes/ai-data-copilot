import requests
import streamlit as st

# ─── Clé API sécurisée via Streamlit Secrets ───────────────────
# En local : créer .streamlit/secrets.toml avec GROQ_API_KEY = "gsk_..."
# En production : ajouter la clé dans Settings > Secrets sur share.streamlit.io
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

SYSTEM_PROMPT = (
    "You are a senior data analyst. "
    "CRITICAL RULE: always reply in the exact language the user writes in — "
    "never switch to another language under any circumstances. "
    "Be concise and precise."
)

def query_ai(prompt: str, timeout: int = 300) -> str:
    if not GROQ_API_KEY:
        return "Erreur : clé API Groq manquante. Configurez GROQ_API_KEY dans les Secrets Streamlit."

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1024
            },
            timeout=timeout
        )

        data = response.json()

        if "choices" not in data:
            error_msg = data.get("error", {}).get("message", str(data))
            return f"Erreur API Groq : {error_msg}"

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "Erreur : délai d'attente dépassé."
    except requests.exceptions.ConnectionError:
        return "Erreur : impossible de joindre l'API Groq. Vérifiez votre connexion."
    except Exception as e:
        return f"Erreur inattendue : {e}"