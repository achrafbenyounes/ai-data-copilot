# core/ai/data_health_score.py
import pandas as pd
import numpy as np
import re


# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════════════════════════════

_T = {

    # ── 1. Valeurs manquantes ─────────────────────────────────────────────────
    "missing_values": {
        "fr": {
            "label":       "Données incomplètes",
            "explication": "{total_nulls} information(s) sont absentes de votre fichier ({null_pct} % des données au total).",
            "impact":      "Des données manquantes peuvent fausser vos analyses, générer des erreurs dans vos rapports et conduire à de mauvaises décisions.",
            "conseil":     "Vérifiez les sources de collecte et complétez les champs vides, ou excluez les lignes incomplètes si elles ne sont pas exploitables.",
        },
        "en": {
            "label":       "Incomplete Data",
            "explication": "{total_nulls} value(s) are missing from your file ({null_pct}% of all data).",
            "impact":      "Missing data can skew your analyses, cause errors in reports, and lead to poor decision-making.",
            "conseil":     "Review your data sources and fill in the blank fields, or remove incomplete rows if they cannot be used.",
        },
        "es": {
            "label":       "Datos Incompletos",
            "explication": "{total_nulls} valor(es) están ausentes en su archivo ({null_pct} % del total de datos).",
            "impact":      "Los datos faltantes pueden distorsionar sus análisis, generar errores en los informes y llevar a decisiones incorrectas.",
            "conseil":     "Revise las fuentes de recopilación y complete los campos vacíos, o elimine las filas incompletas si no son utilizables.",
        },
        "de": {
            "label":       "Unvollständige Daten",
            "explication": "{total_nulls} Wert(e) fehlen in Ihrer Datei ({null_pct} % aller Daten).",
            "impact":      "Fehlende Daten können Ihre Analysen verfälschen, Fehler in Berichten verursachen und zu schlechten Entscheidungen führen.",
            "conseil":     "Überprüfen Sie Ihre Datenquellen und füllen Sie die leeren Felder aus, oder entfernen Sie unvollständige Zeilen, wenn diese nicht nutzbar sind.",
        },
        "ar": {
            "label":       "بيانات غير مكتملة",
            "explication": "{total_nulls} قيمة(قيم) مفقودة في ملفك ({null_pct}٪ من إجمالي البيانات).",
            "impact":      "البيانات المفقودة يمكن أن تُشوّه تحليلاتك وتسبب أخطاء في التقارير وتؤدي إلى قرارات خاطئة.",
            "conseil":     "راجع مصادر جمع البيانات وأكمل الحقول الفارغة، أو احذف الصفوف غير المكتملة إذا لم تكن قابلة للاستخدام.",
        },
    },

    # ── 2. Doublons ───────────────────────────────────────────────────────────
    "duplicates": {
        "fr": {
            "label":       "Lignes en double",
            "explication": "{dup_count} ligne(s) apparaissent plusieurs fois dans votre fichier ({dup_pct} % du total).",
            "impact":      "Les doublons gonflent artificiellement vos chiffres : chiffre d'affaires surévalué, comptages clients incorrects, tableaux de bord trompeurs.",
            "conseil":     "Dédoublonnez vos données avant toute analyse. Vérifiez également le processus d'alimentation pour éviter que cela se reproduise.",
        },
        "en": {
            "label":       "Duplicate Rows",
            "explication": "{dup_count} row(s) appear more than once in your file ({dup_pct}% of total).",
            "impact":      "Duplicates artificially inflate your numbers: overstated revenue, incorrect customer counts, misleading dashboards.",
            "conseil":     "Remove duplicates before running any analysis. Also review your data pipeline to prevent this from recurring.",
        },
        "es": {
            "label":       "Filas Duplicadas",
            "explication": "{dup_count} fila(s) aparecen más de una vez en su archivo ({dup_pct} % del total).",
            "impact":      "Los duplicados inflan artificialmente sus cifras: ingresos sobrevalorados, conteos de clientes incorrectos, paneles engañosos.",
            "conseil":     "Elimine los duplicados antes de realizar cualquier análisis. Revise también el proceso de carga para evitar que vuelva a ocurrir.",
        },
        "de": {
            "label":       "Doppelte Zeilen",
            "explication": "{dup_count} Zeile(n) erscheinen mehr als einmal in Ihrer Datei ({dup_pct} % der Gesamtdaten).",
            "impact":      "Duplikate verfälschen Ihre Zahlen künstlich: überhöhte Umsätze, falsche Kundenzählungen, irreführende Dashboards.",
            "conseil":     "Entfernen Sie Duplikate vor jeder Analyse. Überprüfen Sie auch Ihren Datenpipeline-Prozess, um eine Wiederholung zu vermeiden.",
        },
        "ar": {
            "label":       "صفوف مكررة",
            "explication": "{dup_count} صف(صفوف) تظهر أكثر من مرة في ملفك ({dup_pct}٪ من الإجمالي).",
            "impact":      "التكرارات تُضخّم أرقامك اصطناعيًا: إيرادات مبالغ فيها، عدد عملاء غير صحيح، لوحات معلومات مضللة.",
            "conseil":     "احذف التكرارات قبل إجراء أي تحليل. راجع أيضًا عملية تحميل البيانات لتجنب تكرار هذا الأمر.",
        },
    },

    # ── 3. Colonnes quasi-vides ────────────────────────────────────────────────
    "empty_columns": {
        "fr": {
            "label":       "Colonnes presque vides",
            "explication": "{nb_cols} colonne(s) contiennent plus de 50 % de cases vides : {col_names}.",
            "impact":      "Ces colonnes sont peu fiables pour l'analyse. Les utiliser peut générer des résultats erronés ou des graphiques vides.",
            "conseil":     "Décidez si ces colonnes sont nécessaires. Si oui, organisez une collecte des données manquantes. Sinon, envisagez de les retirer de vos analyses.",
        },
        "en": {
            "label":       "Nearly Empty Columns",
            "explication": "{nb_cols} column(s) are more than 50% empty: {col_names}.",
            "impact":      "These columns are unreliable for analysis. Using them may produce incorrect results or empty charts.",
            "conseil":     "Decide whether these columns are necessary. If so, launch a data collection effort to fill them. Otherwise, consider removing them from your analyses.",
        },
        "es": {
            "label":       "Columnas Casi Vacías",
            "explication": "{nb_cols} columna(s) tienen más del 50 % de valores vacíos: {col_names}.",
            "impact":      "Estas columnas no son fiables para el análisis. Usarlas puede generar resultados incorrectos o gráficos vacíos.",
            "conseil":     "Decida si estas columnas son necesarias. Si es así, organice una campaña para recopilar los datos faltantes. De lo contrario, elimínelas de sus análisis.",
        },
        "de": {
            "label":       "Fast leere Spalten",
            "explication": "{nb_cols} Spalte(n) sind zu mehr als 50 % leer: {col_names}.",
            "impact":      "Diese Spalten sind für die Analyse unzuverlässig. Ihre Verwendung kann zu falschen Ergebnissen oder leeren Diagrammen führen.",
            "conseil":     "Entscheiden Sie, ob diese Spalten notwendig sind. Falls ja, starten Sie eine Datenerhebung. Andernfalls entfernen Sie sie aus Ihren Analysen.",
        },
        "ar": {
            "label":       "أعمدة شبه فارغة",
            "explication": "{nb_cols} عمود(أعمدة) تحتوي على أكثر من 50٪ من القيم الفارغة: {col_names}.",
            "impact":      "هذه الأعمدة غير موثوقة للتحليل. استخدامها قد يُنتج نتائج غير صحيحة أو مخططات فارغة.",
            "conseil":     "قرر ما إذا كانت هذه الأعمدة ضرورية. إذا كان الأمر كذلك، نظّم جمعًا للبيانات المفقودة. وإلا، فكّر في إزالتها من تحليلاتك.",
        },
    },

    # ── 4a. Outliers récurrents — segment distinct (produit premium, etc.) ────
    "outliers_recurring": {
        "fr": {
            "label":       "Segment de valeurs élevées détecté — « {col} »",
            "explication": "{n} valeur(s) dépassent la normale ({pct_data} % des lignes), toutes concentrées autour de {top_val}. La plage habituelle de cette colonne est {normal_range}.",
            "impact":      "Ce n'est probablement pas une erreur : il s'agit d'un groupe distinct (ex. produit haut de gamme, client grand compte, offre premium) qui tire vos moyennes vers le haut et peut fausser vos comparaisons globales.",
            "conseil":     "Vérifiez à quelle réalité correspond cette valeur (ex. quel produit, quelle catégorie). Si elle est légitime, analysez ce segment séparément pour obtenir des indicateurs fiables pour chaque groupe.",
        },
        "en": {
            "label":       "High-Value Segment Detected — '{col}'",
            "explication": "{n} value(s) exceed the normal range ({pct_data}% of rows), all concentrated around {top_val}. The usual range for this column is {normal_range}.",
            "impact":      "This is likely not an error: it represents a distinct group (e.g. premium product, enterprise account, high-end offer) pulling your averages up and skewing global comparisons.",
            "conseil":     "Identify what this value corresponds to (e.g. which product, which category). If legitimate, analyse this segment separately to get reliable metrics for each group.",
        },
        "es": {
            "label":       "Segmento de Valores Altos Detectado — '{col}'",
            "explication": "{n} valor(es) superan el rango normal ({pct_data} % de las filas), todos concentrados alrededor de {top_val}. El rango habitual de esta columna es {normal_range}.",
            "impact":      "Probablemente no es un error: representa un grupo distinto (ej. producto premium, cuenta enterprise) que eleva sus promedios y distorsiona las comparaciones globales.",
            "conseil":     "Identifique a qué corresponde este valor (ej. qué producto, qué categoría). Si es legítimo, analice este segmento por separado para obtener métricas fiables.",
        },
        "de": {
            "label":       "Hochwertsegment Erkannt — '{col}'",
            "explication": "{n} Wert(e) überschreiten den Normalbereich ({pct_data} % der Zeilen), alle konzentriert um {top_val}. Der übliche Bereich dieser Spalte ist {normal_range}.",
            "impact":      "Dies ist wahrscheinlich kein Fehler: Es handelt sich um eine eigenständige Gruppe (z.B. Premiumprodukt, Enterprise-Kunde), die Ihre Durchschnittswerte nach oben zieht.",
            "conseil":     "Identifizieren Sie, was diesem Wert entspricht. Falls legitim, analysieren Sie dieses Segment separat für zuverlässige Kennzahlen.",
        },
        "ar": {
            "label":       "تم اكتشاف شريحة ذات قيم عالية — '{col}'",
            "explication": "{n} قيمة(قيم) تتجاوز النطاق الطبيعي ({pct_data}٪ من الصفوف)، جميعها مركّزة حول {top_val}. النطاق المعتاد لهذا العمود هو {normal_range}.",
            "impact":      "على الأرجح ليست خطأ: تمثّل مجموعة متميزة (مثل منتج فاخر، حساب مؤسسي) ترفع متوسطاتك وتُشوّه المقارنات العامة.",
            "conseil":     "حدّد ما تمثّله هذه القيمة. إذا كانت مشروعة، حلّل هذه الشريحة بشكل منفصل للحصول على مقاييس موثوقة لكل مجموعة.",
        },
    },

    # ── 4b. Outliers dispersés — erreurs potentielles ─────────────────────────
    "outliers_scattered": {
        "fr": {
            "label":       "Valeurs suspectes à vérifier — « {col} »",
            "explication": "{n} valeur(s) sont anormalement élevées ou basses ({pct_data} % des lignes), sans motif cohérent : {val_sample}. La plage habituelle est {normal_range}.",
            "impact":      "Des valeurs isolées et incohérentes signalent souvent des erreurs de saisie, des problèmes d'import ou des données corrompues. Elles peuvent fortement biaiser vos calculs.",
            "conseil":     "Exportez et examinez ces {n} lignes une par une. Corrigez les erreurs identifiées. Si certaines valeurs sont légitimes (cas exceptionnels réels), isolez-les et documentez-les.",
        },
        "en": {
            "label":       "Suspicious Values to Review — '{col}'",
            "explication": "{n} value(s) are abnormally high or low ({pct_data}% of rows), with no consistent pattern: {val_sample}. The usual range is {normal_range}.",
            "impact":      "Isolated, inconsistent values typically signal data entry errors, import issues, or corrupted data. They can heavily bias your calculations.",
            "conseil":     "Export and review these {n} rows one by one. Fix identified errors. If some values are genuinely exceptional, isolate and document them.",
        },
        "es": {
            "label":       "Valores Sospechosos a Revisar — '{col}'",
            "explication": "{n} valor(es) son anormalmente altos o bajos ({pct_data} % de las filas), sin un patrón coherente: {val_sample}. El rango habitual es {normal_range}.",
            "impact":      "Los valores aislados e inconsistentes suelen indicar errores de entrada, problemas de importación o datos corruptos. Pueden sesgar fuertemente sus cálculos.",
            "conseil":     "Exporte y revise estas {n} filas una por una. Corrija los errores. Si algunos valores son genuinamente excepcionales, aíslelos y documéntelos.",
        },
        "de": {
            "label":       "Verdächtige Werte zur Überprüfung — '{col}'",
            "explication": "{n} Wert(e) sind ungewöhnlich hoch oder niedrig ({pct_data} % der Zeilen), ohne konsistentes Muster: {val_sample}. Der übliche Bereich ist {normal_range}.",
            "impact":      "Isolierte, inkonsistente Werte signalisieren häufig Eingabefehler, Importprobleme oder beschädigte Daten. Sie können Ihre Berechnungen stark verzerren.",
            "conseil":     "Exportieren und überprüfen Sie diese {n} Zeilen einzeln. Korrigieren Sie Fehler. Legitime Ausnahmen isolieren und dokumentieren.",
        },
        "ar": {
            "label":       "قيم مشبوهة تحتاج مراجعة — '{col}'",
            "explication": "{n} قيمة(قيم) مرتفعة أو منخفضة بشكل غير طبيعي ({pct_data}٪ من الصفوف)، دون نمط متسق: {val_sample}. النطاق المعتاد هو {normal_range}.",
            "impact":      "القيم المعزولة وغير المتسقة تشير عادةً إلى أخطاء الإدخال أو مشاكل الاستيراد أو البيانات التالفة. يمكنها أن تُحيز حساباتك بشدة.",
            "conseil":     "صدّر وراجع هذه الصفوف {n} واحدًا تلو الآخر. صحّح الأخطاء. إذا كانت بعض القيم استثنائية حقيقية، فعزلها ووثّقها.",
        },
    },

    # ── 4c. Outliers mixtes ────────────────────────────────────────────────────
    "outliers_mixed": {
        "fr": {
            "label":       "Valeurs inhabituelles — vérification recommandée — « {col} »",
            "explication": "{n} valeur(s) s'écartent de la normale ({pct_data} % des lignes) : quelques valeurs reviennent souvent ({top_val} × {top_count} fois) mais d'autres sont isolées. La plage habituelle est {normal_range}.",
            "impact":      "Ce mélange peut indiquer à la fois un segment légitime et des erreurs de saisie. Sans vérification, vos moyennes et totaux risquent d'être biaisés des deux côtés.",
            "conseil":     "Examinez les valeurs répétées ({top_val}) : sont-elles liées à un produit, une catégorie ou un client spécifique ? Vérifiez ensuite les valeurs isolées pour détecter les erreurs.",
        },
        "en": {
            "label":       "Unusual Values — Review Recommended — '{col}'",
            "explication": "{n} value(s) deviate from the norm ({pct_data}% of rows): some values repeat frequently ({top_val} × {top_count} times) while others appear only once. The usual range is {normal_range}.",
            "impact":      "This mix may indicate both a legitimate segment and data entry errors. Without review, your averages and totals risk being biased from both sides.",
            "conseil":     "Examine the recurring values ({top_val}): are they linked to a product, category, or specific client? Then check the isolated values for errors.",
        },
        "es": {
            "label":       "Valores Inusuales — Revisión Recomendada — '{col}'",
            "explication": "{n} valor(es) se desvían de la norma ({pct_data} % de las filas): algunos valores se repiten frecuentemente ({top_val} × {top_count} veces) mientras otros aparecen solo una vez. El rango habitual es {normal_range}.",
            "impact":      "Esta mezcla puede indicar tanto un segmento legítimo como errores de entrada. Sin revisión, sus promedios y totales pueden estar sesgados por ambos lados.",
            "conseil":     "Examine los valores recurrentes ({top_val}): ¿están vinculados a un producto, categoría o cliente específico? Luego verifique los valores aislados en busca de errores.",
        },
        "de": {
            "label":       "Ungewöhnliche Werte — Überprüfung Empfohlen — '{col}'",
            "explication": "{n} Wert(e) weichen von der Norm ab ({pct_data} % der Zeilen): Einige Werte wiederholen sich häufig ({top_val} × {top_count} Mal), andere erscheinen nur einmal. Der übliche Bereich ist {normal_range}.",
            "impact":      "Diese Mischung kann sowohl ein legitimes Segment als auch Eingabefehler anzeigen. Ohne Überprüfung riskieren Ihre Durchschnittswerte Verzerrungen von beiden Seiten.",
            "conseil":     "Untersuchen Sie die wiederkehrenden Werte ({top_val}): Sind sie mit einem Produkt, einer Kategorie oder einem Kunden verknüpft? Prüfen Sie dann die isolierten Werte auf Fehler.",
        },
        "ar": {
            "label":       "قيم غير اعتيادية — يُنصح بالمراجعة — '{col}'",
            "explication": "{n} قيمة(قيم) تنحرف عن المعيار ({pct_data}٪ من الصفوف): بعض القيم تتكرر بكثرة ({top_val} × {top_count} مرة) بينما تظهر أخرى مرة واحدة فقط. النطاق المعتاد هو {normal_range}.",
            "impact":      "هذا الخليط قد يشير إلى شريحة مشروعة وأخطاء إدخال في آنٍ واحد. بدون مراجعة، قد تكون متوسطاتك ومجاميعك متحيزة من الجانبين.",
            "conseil":     "افحص القيم المتكررة ({top_val}): هل ترتبط بمنتج أو فئة أو عميل محدد؟ ثم تحقق من القيم المعزولة للكشف عن الأخطاء.",
        },
    },

    # ── Niveaux de score ──────────────────────────────────────────────────────
    "levels": {
        "fr": [(90,"Excellent","🟢","green"),(71,"Bon","🟡","orange"),(41,"Moyen","🟠","orange"),(0,"Critique","🔴","red")],
        "en": [(90,"Excellent","🟢","green"),(71,"Good","🟡","orange"),(41,"Fair","🟠","orange"),(0,"Critical","🔴","red")],
        "es": [(90,"Excelente","🟢","green"),(71,"Bueno","🟡","orange"),(41,"Regular","🟠","orange"),(0,"Crítico","🔴","red")],
        "de": [(90,"Ausgezeichnet","🟢","green"),(71,"Gut","🟡","orange"),(41,"Mittelmäßig","🟠","orange"),(0,"Kritisch","🔴","red")],
        "ar": [(90,"ممتاز","🟢","green"),(71,"جيد","🟡","orange"),(41,"متوسط","🟠","orange"),(0,"حرج","🔴","red")],
    },
}

_SUPPORTED_LANGS = {"fr", "en", "es", "de", "ar"}
_DEFAULT_LANG    = "fr"


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _resolve_lang(lang: str) -> str:
    lang = lang.lower().split("-")[0]
    return lang if lang in _SUPPORTED_LANGS else _DEFAULT_LANG


def _t(key: str, lang: str, **kwargs) -> dict:
    entry = _T[key].get(lang, _T[key][_DEFAULT_LANG])
    return {k: v.format(**kwargs) if isinstance(v, str) else v for k, v in entry.items()}


def _is_id_column(col_name: str, series: pd.Series) -> bool:
    """Détecte si une colonne est un identifiant technique à ignorer."""
    name_lower = col_name.lower()
    # Patterns de nommage id
    id_patterns = r"^(id|uid|uuid|ref|code|num|no|nr|key|pk|sk|hash)$|(_id|_uid|_ref|_code|_key|_no)$"
    if re.search(id_patterns, name_lower):
        return True
    # Séquence strictement croissante (auto-increment)
    if series.is_monotonic_increasing and series.nunique() == len(series):
        return True
    return False


def _format_range(min_val: float, max_val: float) -> str:
    """Formate un intervalle de valeurs de façon lisible."""
    fmt = lambda v: f"{v:,.0f}" if v == int(v) else f"{v:,.2f}".rstrip('0').rstrip('.')
    return f"{fmt(min_val)} – {fmt(max_val)}"


def _format_val(v: float) -> str:
    fmt = lambda x: f"{x:,.0f}" if x == int(x) else f"{x:,.2f}".rstrip('0').rstrip('.')
    return fmt(v)


def _classify_outliers(col: str, series: pd.Series, mask: pd.Series) -> dict:
    """
    Analyse intelligente des outliers d'une colonne.
    Retourne un dict avec le type détecté et toutes les variables
    nécessaires aux messages i18n.

    Types possibles :
        - "recurring"  : valeur(s) répétées → segment distinct (produit premium, etc.)
        - "scattered"  : valeurs aléatoires dispersées → erreurs potentielles
        - "mixed"      : mélange des deux
        - "skip"       : colonne à ignorer (id, variance nulle)
    """
    n         = int(mask.sum())
    vals      = series[mask]
    vc        = vals.value_counts()
    top_val   = float(vc.index[0])
    top_count = int(vc.iloc[0])
    n_unique  = len(vc)
    conc      = top_count / n          # concentration sur la valeur dominante
    pct_data  = round(n / len(series) * 100, 1)

    normal_series = series[~mask]
    normal_range  = _format_range(normal_series.min(), normal_series.max())

    # Échantillon lisible des valeurs aberrantes (max 5 valeurs uniques)
    sample_vals   = sorted(vc.index.tolist()[:5])
    val_sample    = ", ".join(_format_val(v) for v in sample_vals)
    if len(vc) > 5:
        val_sample += f" … (+{len(vc)-5} autres)"

    base = dict(
        col=col, n=n, pct_data=pct_data,
        top_val=_format_val(top_val), top_count=top_count,
        normal_range=normal_range, val_sample=val_sample,
    )

    # ── Classification ────────────────────────────────────────
    # Segment récurrent : ≥ 80 % des outliers = même valeur, ≥ 3 occurrences,
    # représente ≥ 3 % des données (pas un cas isolé)
    if conc >= 0.80 and top_count >= 3 and pct_data >= 3 and n_unique <= 4:
        return {"type": "recurring", **base}

    # Dispersé : nombreuses valeurs uniques ou forte dispersion aléatoire
    if n_unique >= max(5, n * 0.6) or conc < 0.40:
        return {"type": "scattered", **base}

    # Mixte : entre les deux
    return {"type": "mixed", **base}


# ══════════════════════════════════════════════════════════════════════════════
# SCORE DE SANTÉ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def compute_health_score(df: pd.DataFrame, lang: str = "fr") -> dict:
    """
    Calcule un score de qualité de données entre 0 et 100.
    Analyse intelligente et universelle de tout fichier CSV.

    Paramètre :
        lang : "fr" (défaut) | "en" | "es" | "de" | "ar"
    """
    lang    = _resolve_lang(lang)
    score   = 100
    details = []

    total_cells = df.shape[0] * df.shape[1]

    # ── 1. Valeurs manquantes (jusqu'à -30 pts) ──────────────────────
    total_nulls  = int(df.isnull().sum().sum())
    if total_cells > 0:
        null_pct    = total_nulls / total_cells
        null_penalty = round(min(null_pct * 100, 30))
        if null_penalty > 0:
            score -= null_penalty
            msg = _t("missing_values", lang,
                     total_nulls=total_nulls,
                     null_pct=round(null_pct * 100, 1))
            details.append({"critere": msg["label"], "penalite": null_penalty,
                             "explication": msg["explication"],
                             "impact": msg["impact"], "conseil": msg["conseil"]})

    # ── 2. Doublons (jusqu'à -20 pts) ───────────────────────────────
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        dup_pct    = dup_count / len(df)
        dup_penalty = round(min(dup_pct * 100, 20))
        score -= dup_penalty
        msg = _t("duplicates", lang,
                 dup_count=dup_count,
                 dup_pct=round(dup_pct * 100, 1))
        details.append({"critere": msg["label"], "penalite": dup_penalty,
                         "explication": msg["explication"],
                         "impact": msg["impact"], "conseil": msg["conseil"]})

    # ── 3. Colonnes quasi-vides > 50 % (jusqu'à -25 pts) ────────────
    high_null_cols = [c for c in df.columns if df[c].isnull().mean() > 0.5]
    if high_null_cols:
        cols_penalty  = min(len(high_null_cols) * 5, 25)
        score        -= cols_penalty
        readable_cols = ", ".join(
            c.replace("_", " ").replace("-", " ").title() for c in high_null_cols
        )
        msg = _t("empty_columns", lang,
                 nb_cols=len(high_null_cols), col_names=readable_cols)
        details.append({"critere": msg["label"], "penalite": cols_penalty,
                         "explication": msg["explication"],
                         "impact": msg["impact"], "conseil": msg["conseil"]})

    # ── 4. Outliers intelligents (jusqu'à -25 pts) ───────────────────
    numeric_cols    = df.select_dtypes(include=["int64", "float64"]).columns
    total_outliers  = 0
    outlier_details = []   # liste de (n_outliers, analyse)

    for col in numeric_cols:
        # Ignorer les colonnes identifiants techniques
        if _is_id_column(col, df[col]):
            continue

        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr    = q3 - q1

        # Ignorer les colonnes à variance nulle (constantes)
        if iqr == 0:
            continue

        mask = (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)
        n    = int(mask.sum())
        if n == 0:
            continue

        total_outliers += n
        analysis = _classify_outliers(col, df[col], mask)
        outlier_details.append((n, analysis))

    if total_outliers > 0:
        # Nombre de colonnes numériques non-id pour le calcul de pénalité
        eligible_cols  = [
            c for c in numeric_cols
            if not _is_id_column(c, df[c]) and df[c].nunique() > 1
        ]
        n_eligible     = max(len(eligible_cols), 1)
        outlier_pct    = total_outliers / (len(df) * n_eligible)
        outlier_penalty = round(min(outlier_pct * 100, 25))

        if outlier_penalty > 0:
            score -= outlier_penalty

            # Générer un message par colonne concernée
            for n_out, analysis in outlier_details:
                msg_key = f"outliers_{analysis['type']}"
                msg     = _t(msg_key, lang, **{
                    k: v for k, v in analysis.items() if k != "type"
                })
                details.append({
                    "critere":     msg["label"],
                    "penalite":    round(outlier_penalty / len(outlier_details)),
                    "explication": msg["explication"],
                    "impact":      msg["impact"],
                    "conseil":     msg["conseil"],
                })

    # ── Score final ──────────────────────────────────────────────────
    score  = max(score, 0)
    levels = _T["levels"].get(lang, _T["levels"][_DEFAULT_LANG])
    niveau, emoji, couleur = levels[-1][1], levels[-1][2], levels[-1][3]
    for threshold, lbl, em, col in levels:
        if score >= threshold:
            niveau, emoji, couleur = lbl, em, col
            break

    return {
        "score":       score,
        "niveau":      niveau,
        "emoji":       emoji,
        "couleur":     couleur,
        "details":     details,
        "nb_lignes":   df.shape[0],
        "nb_colonnes": df.shape[1],
        "lang":        lang,
    }
