# ai_brain.py
# -------------------------------
# AI Brain - Communicate with local LLM (Ollama + Llama 3)
# -------------------------------

import subprocess

# FIX: system instruction to match the user's language
SYSTEM_PROMPT = "You are a helpful data assistant. Always reply in the same language as the user's question."

def query_ai(prompt: str, timeout: int = 300) -> str:
    """
    Sends a prompt to Llama 3 via Ollama and returns the AI response.
    The AI will automatically reply in the same language as the question.
    timeout: seconds to wait for a response (default 5 minutes)
    """
    try:
        # Inject system instruction before the user prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        process = subprocess.Popen(
            ["ollama", "run", "llama3"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        stdout, stderr = process.communicate(full_prompt, timeout=timeout)

        if process.returncode != 0 and stderr:
            return f"AI Error: {stderr.strip()}"

        return stdout.strip()

    except subprocess.TimeoutExpired:
        process.kill()
        return (
            f"AI Error: timeout expired after {timeout}s.\n"
            "Tips: try a shorter question, or increase the timeout value."
        )
    except FileNotFoundError:
        return "AI Error: Ollama is not installed or not found in PATH."
    except Exception as e:
        return f"Error communicating with AI: {e}"
