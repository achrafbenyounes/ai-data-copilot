# ai_brain.py
import requests

GROQ_API_KEY = "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"

SYSTEM_PROMPT = """You are a senior data analyst. Always reply in the same language as the user's question.
                Instructions:
                    - analyze the data carefully
                    - answer clearly
                    - if the question is about statistics compute insights
                    - if it is about text summarize it
                """

def query_ai(prompt: str, timeout: int = 300) -> str:
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",  # FIX: nouveau nom du modèle
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 10000
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
