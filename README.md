# AI Data Copilot - Universal AI Data Assistant
# AI Data Copilot - Copilote IA universel pour les données
# AI Data Copilot - مساعد الذكاء الاصطناعي الشامل للبيانات

---

## Description / Description / الوصف

**English:**  
AI Data Copilot is a universal AI-powered assistant for exploring, analyzing, and understanding any type of data or document.  
Supports CSV, JSON, Parquet, Excel, TXT, PDF, Markdown, and logs.  

**Français:**  
AI Data Copilot est un assistant universel propulsé par l’IA pour explorer, analyser et comprendre tout type de données ou documents.  
Compatible CSV, JSON, Parquet, Excel, TXT, PDF, Markdown et logs.  

**العربية:**  
AI Data Copilot هو مساعد شامل مدعوم بالذكاء الاصطناعي لاستكشاف وتحليل وفهم أي نوع من البيانات أو المستندات.  
يدعم CSV، JSON، Parquet، Excel، TXT، PDF، Markdown وlogs.

---

## Features / Fonctionnalités / الميزات

- Upload and preview files (CSV, TXT, PDF)  
- Téléversement et aperçu des fichiers (CSV, TXT, PDF)  
- رفع وعرض الملفات (CSV، TXT، PDF)  

- Extract text from documents  
- Extraction de texte des documents  
- استخراج النصوص من المستندات  

- Local AI integration (Ollama + Llama 3)  
- Intégration IA locale (Ollama + Llama 3)  
- دمج الذكاء الاصطناعي المحلي (Ollama + Llama 3)  

- Multilingual support: English, French, Arabic  
- Support multilingue : anglais, français, arabe  
- دعم متعدد اللغات: الإنجليزية، الفرنسية، العربية

---

## Installation / Installation / التثبيت

### Prerequisites / Prérequis / المتطلبات

- Python 3.10+  
- Visual Studio Code (recommended)  
- Ollama (local LLM runtime)  

---

### Setup / Configuration / الإعداد

1. Clone the repository / Cloner le repo / استنساخ المستودع:

git clone https://github.com/USERNAME/ai-data-copilot.git
cd ai-data-copilot

2. Create and activate virtual environment / Créer et activer l’environnement virtuel / إنشاء وتفعيل البيئة الافتراضية:

python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

3. Install dependencies / Installer les dépendances / تثبيت المكتبات:

pip install streamlit pandas duckdb pyspark pymupdf requests

4. Start Ollama / Démarrer Ollama / تشغيل Ollama:

ollama run llama3

Usage / Utilisation / الاستخدام

1. Run the Streamlit app / Lancer l’application Streamlit / تشغيل تطبيق Streamlit:

streamlit run webapp/app.py

2. Open browser / Ouvrir le navigateur / افتح المتصفح:

http://localhost:8501

3. Upload a file (CSV, TXT, PDF) / Téléverser un fichier / رفع ملف

4. Preview dataset or document / Aperçu du fichier / عرض الملف

Example interactions / Exemples / أمثلة:

"Explain this dataset" → preview and insights

"Summarize this document" → text summary

"Generate SQL analysis" → future AI response

Future Steps / Étapes futures / الخطوات المستقبلية

- Connect AI Copilot to answer questions / Connecter le Copilote IA / توصيل المساعد للرد على الأسئلة

- Generate SQL / Spark pipelines automatically / Génération SQL / Spark automatiquement / توليد SQL / Spark تلقائيًا

- Multilingual auto-detection (EN/FR/AR) / Détection multilingue automatique / كشف اللغة تلقائيًا

- Cloud deployment / SaaS mode / Déploiement cloud / وضع SaaS

License / Licence / الترخيص

MIT License
