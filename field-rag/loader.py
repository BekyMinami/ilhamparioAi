"""Read the ticket spreadsheet into a DataFrame. Nothing else."""
from pathlib import Path

import pandas as pd


def load_tickets(path: str | Path) -> pd.DataFrame:
    """Load tickets from an .xlsx or .csv file."""
    path = Path(path)
    if path.suffix == ".xlsx":
        return pd.read_excel(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")