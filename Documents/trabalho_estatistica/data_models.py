from typing import Dict, List

import pandas as pd


ANOS_LABEL: List[str] = [
    "iPhone 13 (2021)",
    "iPhone 14 (2022)",
    "iPhone 15 (2023)",
    "iPhone 16 (2024)",
    "iPhone 17 (2025)",
]

MODEL_COLUMNS: List[str] = ["preco_base", "preco_pro", "preco_pro_max"]
MODEL_LABELS: List[str] = ["Base", "Pro", "Pro Max"]
MODEL_TITLES: Dict[str, str] = {
    "preco_base": "iPhone (Base)",
    "preco_pro": "iPhone Pro",
    "preco_pro_max": "iPhone Pro Max",
}

DEFAULT_DATA: pd.DataFrame = pd.DataFrame(
    {
        "ano": ANOS_LABEL,
        "salario_minimo": [1100.00, 1212.00, 1302.00, 1412.00, 1518.00],
        "preco_base": [7599, 7599, 7299, 7799, 7999],
        "preco_pro": [9499, 9499, 9299, 10499, 11499],
        "preco_pro_max": [10499, 10499, 10099, 12499, 12499],
    }
)

COLUMN_DISPLAY_NAMES: Dict[str, str] = {
    "ano": "Ano",
    "salario_minimo": "Salario minimo (R$)",
    "preco_base": "iPhone (Base)",
    "preco_pro": "iPhone Pro",
    "preco_pro_max": "iPhone Pro Max",
}

DISPLAY_TO_COLUMN: Dict[str, str] = {v: k for k, v in COLUMN_DISPLAY_NAMES.items()}

COLOR_MAP: Dict[str, str] = {
    "preco_base": "#38bdf8",
    "preco_pro": "#34d399",
    "preco_pro_max": "#f97316",
    "comparativo_2021": "#38bdf8",
    "comparativo_2025": "#f97316",
    "salario_minimo": "#a855f7",
    "projecao": "#facc15",
}
