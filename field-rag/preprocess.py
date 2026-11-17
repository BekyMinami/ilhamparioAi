"""Clean and mask the ticket DataFrame."""
import re

import pandas as pd

PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+62|62|0)8\d{8,11}(?!\d)")
NAME_PATTERN = re.compile(r"\b(?:Pak|Bu|Bapak|Ibu)\s+[A-Z][a-z]+")


def _normalize_dates(series: pd.Series) -> pd.Series:
    """Accept YYYY-MM-DD or DD/MM/YYYY and return YYYY-MM-DD."""
    text = series.astype(str).str.strip().str[:10]
    iso = pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")
    dmy = pd.to_datetime(text, format="%d/%m/%Y", errors="coerce")
    return iso.fillna(dmy).dt.strftime("%Y-%m-%d")


def _mask(text: str) -> str:
    """Hide phone numbers and customer names inside free text."""
    text = PHONE_PATTERN.sub("[TELEPON]", text)
    return NAME_PATTERN.sub("[NAMA]", text)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Strip text, normalize dates, mask personal data, drop duplicates."""
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("").astype(str).str.strip()
    df["tanggal"] = _normalize_dates(df["tanggal"])
    df["catatan_teknisi"] = df["catatan_teknisi"].map(_mask)
    return df.drop_duplicates().reset_index(drop=True)