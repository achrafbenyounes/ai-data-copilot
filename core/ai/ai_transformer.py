# -------------------------------
# core/ai/ai_transformer.py
# -------------------------------

import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS — labels & descriptions pour chaque transformation
# ══════════════════════════════════════════════════════════════════════════════

_T = {

    # ── 1. Doublons ────────────────────────────────────────────────────────────
    "dedup": {
        "fr": {
            "label": "Supprimer les doublons",
            "desc":  "Élimine les lignes identiques sur toutes les colonnes. Étape indispensable avant toute analyse.",
        },
        "en": {
            "label": "Remove duplicates",
            "desc":  "Drops exact duplicate rows across all columns. Essential step before any analysis.",
        },
        "ar": {
            "label": "إزالة التكرارات",
            "desc":  "حذف الصفوف المكررة تمامًا في جميع الأعمدة. خطوة أساسية قبل أي تحليل.",
        },
    },

    # ── 2. Colonnes trop vides ─────────────────────────────────────────────────
    "drop_high_null": {
        "fr": {
            "label": "Supprimer les colonnes trop vides (> 50 % de nulls)",
            "desc":  "Les colonnes {cols} ont plus de la moitié de leurs valeurs manquantes. "
                     "Elles apportent peu d'information et risquent de biaiser les modèles.",
        },
        "en": {
            "label": "Drop columns with too many nulls (> 50 %)",
            "desc":  "Columns {cols} have more than half their values missing. "
                     "They carry little information and may bias models.",
        },
        "ar": {
            "label": "حذف الأعمدة الفارغة كثيرًا (> 50 % قيم مفقودة)",
            "desc":  "الأعمدة {cols} تحتوي على أكثر من نصف قيمها مفقودة. "
                     "تُسهم بمعلومات ضئيلة وقد تُشوّه النماذج.",
        },
    },

    # ── 3. Nulls numériques ────────────────────────────────────────────────────
    "fill_numeric": {
        "fr": {
            "label": "Remplir les valeurs manquantes — {col}",
            "desc":  "La colonne « {col} » contient {n} valeur(s) nulle(s) ({pct} %). "
                     "Remplacées par la médiane ({median}), plus robuste que la moyenne face aux valeurs extrêmes.",
        },
        "en": {
            "label": "Fill missing values — {col}",
            "desc":  "Column '{col}' has {n} null value(s) ({pct} %). "
                     "Replaced by the median ({median}), more robust than the mean against outliers.",
        },
        "ar": {
            "label": "ملء القيم المفقودة — {col}",
            "desc":  "العمود '{col}' يحتوي على {n} قيمة فارغة ({pct}٪). "
                     "يُستبدل بالوسيط ({median})، وهو أكثر مقاومةً للقيم الشاذة من المتوسط.",
        },
    },

    # ── 4. Nulls texte ─────────────────────────────────────────────────────────
    "fill_text": {
        "fr": {
            "label": "Remplir les valeurs manquantes texte — {col}",
            "desc":  "La colonne « {col} » contient {n} valeur(s) nulle(s) ({pct} %). "
                     "Remplacées par 'Inconnu' pour éviter les erreurs de traitement.",
        },
        "en": {
            "label": "Fill missing text values — {col}",
            "desc":  "Column '{col}' has {n} null value(s) ({pct} %). "
                     "Replaced by 'Unknown' to avoid processing errors.",
        },
        "ar": {
            "label": "ملء القيم النصية المفقودة — {col}",
            "desc":  "العمود '{col}' يحتوي على {n} قيمة فارغة ({pct}٪). "
                     "يُستبدل بـ 'غير معروف' لتجنب أخطاء المعالجة.",
        },
    },

    # ── 5. Trim / casse ────────────────────────────────────────────────────────
    "trim_text": {
        "fr": {
            "label": "Nettoyer les espaces et harmoniser la casse",
            "desc":  "Supprime les espaces superflus et met en minuscules les colonnes texte ({cols}). "
                     "Évite les doublons invisibles comme 'Paris' vs ' paris'.",
        },
        "en": {
            "label": "Trim whitespace and normalize case",
            "desc":  "Removes extra spaces and lowercases text columns ({cols}). "
                     "Prevents invisible duplicates like 'Paris' vs ' paris'.",
        },
        "ar": {
            "label": "إزالة المسافات وتوحيد حالة الأحرف",
            "desc":  "يزيل المسافات الزائدة ويحوّل النصوص إلى أحرف صغيرة في الأعمدة ({cols}). "
                     "يمنع التكرارات غير المرئية مثل 'Paris' مقابل ' paris'.",
        },
    },

    # ── 6. Emails ──────────────────────────────────────────────────────────────
    "lower_email": {
        "fr": {
            "label": "Normaliser les adresses email",
            "desc":  "Met les emails en minuscules et supprime les espaces ({cols}). "
                     "Indispensable pour les jointures et la déduplication sur l'email.",
        },
        "en": {
            "label": "Normalize email addresses",
            "desc":  "Lowercases and trims email columns ({cols}). "
                     "Essential for joins and deduplication on email.",
        },
        "ar": {
            "label": "توحيد عناوين البريد الإلكتروني",
            "desc":  "تحويل البريد الإلكتروني إلى أحرف صغيرة وإزالة المسافات ({cols}). "
                     "ضروري للربط وإزالة التكرارات بناءً على البريد.",
        },
    },

    # ── 7. Dates ───────────────────────────────────────────────────────────────
    "parse_dates": {
        "fr": {
            "label": "Convertir les colonnes dates",
            "desc":  "Les colonnes {cols} contiennent des dates stockées en texte. "
                     "Les convertir en type DATE permet les tris, filtres et calculs d'intervalles.",
        },
        "en": {
            "label": "Parse date columns",
            "desc":  "Columns {cols} store dates as text. "
                     "Casting to DATE enables sorting, filtering and interval calculations.",
        },
        "ar": {
            "label": "تحويل أعمدة التواريخ",
            "desc":  "الأعمدة {cols} تخزّن التواريخ كنصوص. "
                     "تحويلها إلى نوع DATE يُتيح الفرز والتصفية وحساب الفترات الزمنية.",
        },
    },

    # ── 8. Extraction année/mois ───────────────────────────────────────────────
    "extract_date_parts": {
        "fr": {
            "label": "Extraire l'année et le mois depuis les dates",
            "desc":  "Crée de nouvelles colonnes année et mois à partir de {cols}. "
                     "Très utile pour les agrégations temporelles et les analyses de tendance.",
        },
        "en": {
            "label": "Extract year and month from dates",
            "desc":  "Creates new year and month columns from {cols}. "
                     "Very useful for time-based aggregations and trend analysis.",
        },
        "ar": {
            "label": "استخراج السنة والشهر من التواريخ",
            "desc":  "إنشاء أعمدة جديدة للسنة والشهر من {cols}. "
                     "مفيد جدًا للتجميعات الزمنية وتحليل الاتجاهات.",
        },
    },

    # ── 9. Normalisation min-max ───────────────────────────────────────────────
    "normalize": {
        "fr": {
            "label": "Normaliser les colonnes numériques (min-max 0→1)",
            "desc":  "Met les colonnes {cols} sur une échelle de 0 à 1. "
                     "Recommandé avant les algorithmes ML sensibles à l'échelle (KNN, SVM, réseaux de neurones).",
        },
        "en": {
            "label": "Normalize numeric columns (min-max 0→1)",
            "desc":  "Scales columns {cols} to a 0–1 range. "
                     "Recommended before scale-sensitive ML algorithms (KNN, SVM, neural networks).",
        },
        "ar": {
            "label": "تطبيع الأعمدة الرقمية (min-max 0→1)",
            "desc":  "ضبط نطاق الأعمدة {cols} بين 0 و1. "
                     "موصى به قبل خوارزميات تعلم الآلة الحساسة للمقياس (KNN, SVM, الشبكات العصبية).",
        },
    },

    # ── 10. Drop id avant ML ───────────────────────────────────────────────────
    "drop_id": {
        "fr": {
            "label": "Supprimer les colonnes identifiant avant modélisation ML",
            "desc":  "Les colonnes {cols} sont des identifiants techniques. "
                     "Les laisser dans un modèle ML introduit du bruit et des corrélations artificielles.",
        },
        "en": {
            "label": "Drop identifier columns before ML modeling",
            "desc":  "Columns {cols} are technical identifiers. "
                     "Keeping them in an ML model introduces noise and artificial correlations.",
        },
        "ar": {
            "label": "حذف أعمدة المعرّف قبل نمذجة تعلم الآلة",
            "desc":  "الأعمدة {cols} هي معرّفات تقنية. "
                     "إبقاؤها في نموذج تعلم الآلة يُدخل ضوضاء وترابطات اصطناعية.",
        },
    },
}


def _t(key: str, lang: str, **kwargs) -> tuple[str, str]:
    """
    Retourne (label, description) traduits et interpolés pour la clé donnée.
    Fallback sur 'fr' si la langue n'est pas disponible.
    """
    entry = _T[key].get(lang, _T[key]["fr"])
    label = entry["label"].format(**kwargs)
    desc  = entry["desc"].format(**kwargs)
    return label, desc


# ══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATEUR PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def generate_transformations(df: pd.DataFrame, engine: str, lang: str = "fr") -> list[dict]:
    """
    Génère une liste de transformations standards, lisibles et directement applicables.

    Paramètres
    ----------
    df      : le DataFrame analysé
    engine  : "duckdb" | "spark" | "spark_local"
    lang    : "fr" | "en" | "ar"  (défaut : "fr")

    Retour
    ------
    list[dict]  →  chaque élément = { label, description, code }
    """

    results  = []
    is_spark = engine.startswith("spark")

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    string_cols  = df.select_dtypes(include=["object"]).columns.tolist()
    date_cols    = _detect_date_cols(df, string_cols)
    email_cols   = [c for c in string_cols if "email" in c.lower() or "mail" in c.lower()]
    id_cols      = [c for c in df.columns if c.lower() in ("id", "uid", "uuid") or c.lower().endswith("_id")]

    # ── 1. Doublons ────────────────────────────────────────────────────────────
    label, desc = _t("dedup", lang)
    results.append({
        "label": label, "description": desc,
        "code": _code(
            duck=(
                "DELETE FROM dataset\n"
                "WHERE rowid NOT IN (\n"
                "  SELECT MIN(rowid)\n"
                "  FROM dataset\n"
                "  GROUP BY {cols}\n);".format(cols=", ".join(df.columns))
            ),
            spark="df = df.dropDuplicates()",
            is_spark=is_spark
        )
    })

    # ── 2. Colonnes trop vides ─────────────────────────────────────────────────
    high_null_cols = [c for c in df.columns if df[c].isnull().mean() > 0.5]
    if high_null_cols:
        label, desc = _t("drop_high_null", lang, cols=high_null_cols)
        results.append({
            "label": label, "description": desc,
            "code": _code(
                duck="\n".join(f"ALTER TABLE dataset DROP COLUMN \"{c}\";" for c in high_null_cols),
                spark=f"df = df.drop(*{high_null_cols})",
                is_spark=is_spark
            )
        })

    # ── 3. Nulls numériques ────────────────────────────────────────────────────
    for col in numeric_cols:
        n_null = int(df[col].isnull().sum())
        if n_null > 0:
            median_val = round(float(df[col].median()), 4)
            pct        = round(n_null / len(df) * 100, 1)
            label, desc = _t("fill_numeric", lang, col=col, n=n_null, pct=pct, median=median_val)
            results.append({
                "label": label, "description": desc,
                "code": _code(
                    duck=f"UPDATE dataset\nSET \"{col}\" = COALESCE(\"{col}\", {median_val});",
                    spark=(
                        f"from pyspark.ml.feature import Imputer\n\n"
                        f"imputer = Imputer(\n"
                        f"    inputCols=['{col}'],\n"
                        f"    outputCols=['{col}']\n"
                        f").setStrategy('median')\n\n"
                        f"df = imputer.fit(df).transform(df)"
                    ),
                    is_spark=is_spark
                )
            })

    # ── 4. Nulls texte ─────────────────────────────────────────────────────────
    fill_unknown = {"fr": "Inconnu", "en": "Unknown", "ar": "غير معروف"}.get(lang, "Unknown")
    for col in string_cols:
        n_null = int(df[col].isnull().sum())
        if n_null > 0 and col not in date_cols:
            pct = round(n_null / len(df) * 100, 1)
            label, desc = _t("fill_text", lang, col=col, n=n_null, pct=pct)
            results.append({
                "label": label, "description": desc,
                "code": _code(
                    duck=f"UPDATE dataset\nSET \"{col}\" = COALESCE(\"{col}\", '{fill_unknown}');",
                    spark=f"df = df.fillna({{'{col}': '{fill_unknown}'}})",
                    is_spark=is_spark
                )
            })

    # ── 5. Trim / casse ────────────────────────────────────────────────────────
    text_cols_to_clean = [c for c in string_cols if c not in date_cols and c not in email_cols]
    if text_cols_to_clean:
        label, desc = _t("trim_text", lang, cols=text_cols_to_clean)
        results.append({
            "label": label, "description": desc,
            "code": _code(
                duck="\n".join(
                    f"UPDATE dataset SET \"{c}\" = LOWER(TRIM(\"{c}\"));"
                    for c in text_cols_to_clean
                ),
                spark=(
                    "from pyspark.sql.functions import lower, trim\n\n"
                    + "\n".join(
                        f"df = df.withColumn('{c}', lower(trim(df['{c}'])))"
                        for c in text_cols_to_clean
                    )
                ),
                is_spark=is_spark
            )
        })

    # ── 6. Emails ──────────────────────────────────────────────────────────────
    if email_cols:
        label, desc = _t("lower_email", lang, cols=email_cols)
        results.append({
            "label": label, "description": desc,
            "code": _code(
                duck="\n".join(
                    f"UPDATE dataset SET \"{c}\" = LOWER(TRIM(\"{c}\"));"
                    for c in email_cols
                ),
                spark=(
                    "from pyspark.sql.functions import lower, trim\n\n"
                    + "\n".join(
                        f"df = df.withColumn('{c}', lower(trim(df['{c}'])))"
                        for c in email_cols
                    )
                ),
                is_spark=is_spark
            )
        })

    # ── 7. Dates ───────────────────────────────────────────────────────────────
    if date_cols:
        label, desc = _t("parse_dates", lang, cols=date_cols)
        results.append({
            "label": label, "description": desc,
            "code": _code(
                duck="\n".join(
                    f"ALTER TABLE dataset ALTER COLUMN \"{c}\" TYPE DATE USING CAST(\"{c}\" AS DATE);"
                    for c in date_cols
                ),
                spark=(
                    "from pyspark.sql.functions import to_date\n\n"
                    + "\n".join(
                        f"df = df.withColumn('{c}', to_date(df['{c}']))"
                        for c in date_cols
                    )
                ),
                is_spark=is_spark
            )
        })

    # ── 8. Extraction année/mois ───────────────────────────────────────────────
    if date_cols:
        label, desc = _t("extract_date_parts", lang, cols=date_cols)
        results.append({
            "label": label, "description": desc,
            "code": _code(
                duck="\n".join(
                    f"ALTER TABLE dataset ADD COLUMN \"{c}_year\" INT;\n"
                    f"ALTER TABLE dataset ADD COLUMN \"{c}_month\" INT;\n"
                    f"UPDATE dataset SET \"{c}_year\" = YEAR(\"{c}\"), \"{c}_month\" = MONTH(\"{c}\");"
                    for c in date_cols
                ),
                spark=(
                    "from pyspark.sql.functions import year, month\n\n"
                    + "\n".join(
                        f"df = df.withColumn('{c}_year', year(df['{c}']))\n"
                        f"df = df.withColumn('{c}_month', month(df['{c}']))"
                        for c in date_cols
                    )
                ),
                is_spark=is_spark
            )
        })

    # ── 9. Normalisation min-max ───────────────────────────────────────────────
    normalizable = [
        c for c in numeric_cols
        if c not in id_cols and df[c].max() != df[c].min()
    ]
    if normalizable:
        label, desc = _t("normalize", lang, cols=normalizable)
        results.append({
            "label": label, "description": desc,
            "code": _code(
                duck="\n".join(
                    f"UPDATE dataset\n"
                    f"SET \"{c}\" = (\"{c}\" - (SELECT MIN(\"{c}\") FROM dataset))\n"
                    f"           / ((SELECT MAX(\"{c}\") FROM dataset) - (SELECT MIN(\"{c}\") FROM dataset));"
                    for c in normalizable
                ),
                spark=(
                    "from pyspark.ml.feature import MinMaxScaler, VectorAssembler\n"
                    "from pyspark.ml import Pipeline\n\n"
                    + "\n".join(
                        f"assembler_{c} = VectorAssembler(inputCols=['{c}'], outputCols=['{c}_vec'])\n"
                        f"scaler_{c}    = MinMaxScaler(inputCol='{c}_vec', outputCol='{c}_scaled')"
                        for c in normalizable
                    )
                    + "\n\nstages = ["
                    + ", ".join(f"assembler_{c}, scaler_{c}" for c in normalizable)
                    + "]\ndf = Pipeline(stages=stages).fit(df).transform(df)"
                ),
                is_spark=is_spark
            )
        })

    # ── 10. Drop id avant ML ───────────────────────────────────────────────────
    if id_cols:
        label, desc = _t("drop_id", lang, cols=id_cols)
        results.append({
            "label": label, "description": desc,
            "code": _code(
                duck="\n".join(f"ALTER TABLE dataset DROP COLUMN \"{c}\";" for c in id_cols),
                spark=f"df = df.drop(*{id_cols})",
                is_spark=is_spark
            )
        })

    return results


# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES INTERNES
# ══════════════════════════════════════════════════════════════════════════════

def _code(duck: str, spark: str, is_spark: bool) -> str:
    return spark if is_spark else duck


def _detect_date_cols(df: pd.DataFrame, string_cols: list) -> list:
    date_cols = []
    for col in string_cols:
        if any(k in col.lower() for k in ("date", "time", "created", "updated", "inscription", "naissance")):
            date_cols.append(col)
            continue
        sample = df[col].dropna().head(5).astype(str)
        if sum(1 for v in sample if _is_date(v)) >= 3:
            date_cols.append(col)
    return date_cols


def _is_date(value: str) -> bool:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            pd.to_datetime(value, format=fmt)
            return True
        except Exception:
            pass
    return False
