from typing import Dict, Optional

import pandas as pd
import plotly.graph_objects as go

from data_models import COLOR_MAP, MODEL_COLUMNS, MODEL_TITLES


def format_currency(value: float) -> str:
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def format_decimal(value: float, decimals: int = 1) -> str:
    formatted = f"{value:.{decimals}f}"
    return formatted.replace(".", ",")


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formata um valor decimal (0.12) para string percentual com sufixo.
    """
    formatted = f"{value * 100:.{decimals}f}"
    return f"{formatted.replace('.', ',')}%"


def calcular_esforco(df: pd.DataFrame) -> pd.DataFrame:
    efforts = df[MODEL_COLUMNS].div(df["salario_minimo"], axis=0)
    efforts.index = df.index
    return efforts


def apply_dark_theme(fig: go.Figure, y_title: Optional[str] = None) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="#0c101b",
        plot_bgcolor="#141a2a",
        font=dict(family="Inter, sans-serif", color="#f1f5f9"),
        margin=dict(t=60, r=40, b=60, l=60),
        legend=dict(
            font=dict(size=13, color="#f1f5f9"),
            bgcolor="rgba(12,16,27,0.6)",
            borderwidth=0,
        ),
        hoverlabel=dict(bgcolor="#1e293b", font=dict(color="#f1f5f9")),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#334155",
        tickfont=dict(color="#e2e8f0"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.2)",
        zeroline=False,
        tickfont=dict(color="#e2e8f0"),
    )
    if y_title:
        fig.update_yaxes(
            title=dict(text=y_title, font=dict(color="#e2e8f0", family="Inter, sans-serif"))
        )
    return fig


def create_effort_line_chart(df: pd.DataFrame) -> go.Figure:
    effort_df = calcular_esforco(df)
    fig = go.Figure()
    for column in MODEL_COLUMNS:
        fig.add_trace(
            go.Scatter(
                x=df["ano"],
                y=effort_df[column],
                mode="lines+markers",
                name=MODEL_TITLES[column],
                line=dict(color=COLOR_MAP[column], width=4),
                marker=dict(size=8),
                hovertemplate=(
                    "%{x}<br>Esforco: %{y:.1f} salarios<extra>"
                    f"{MODEL_TITLES[column]}</extra>"
                ),
            )
        )
    fig.add_trace(
        go.Scatter(
            x=df["ano"],
            y=df["salario_minimo"],
            mode="lines+markers",
            name="Salario minimo",
            line=dict(color=COLOR_MAP["salario_minimo"], width=3, dash="dot"),
            marker=dict(size=7),
            customdata=df["salario_minimo"].map(format_currency),
            hovertemplate=(
                "%{x}<br>Salario minimo: %{customdata}<extra></extra>"
            ),
            yaxis="y2",
        )
    )
    fig = apply_dark_theme(fig, "Numero de salarios minimos")
    fig.update_layout(
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis2=dict(
            title=dict(text="Salario minimo (R$)", font=dict(color="#e2e8f0", family="Inter, sans-serif")),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#e2e8f0"),
        ),
        yaxis=dict(tickformat=".1f"),
    )
    return fig


def create_price_line_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for column in MODEL_COLUMNS:
        fig.add_trace(
            go.Scatter(
                x=df["ano"],
                y=df[column],
                mode="lines+markers",
                name=MODEL_TITLES[column],
                line=dict(color=COLOR_MAP[column], width=4),
                marker=dict(size=8),
                hovertemplate=(
                    "%{x}<br>Preco: R$ %{y:,.0f}<extra>"
                    f"{MODEL_TITLES[column]}</extra>"
                ),
            )
        )
    fig = apply_dark_theme(fig, "Preco (R$)")
    fig.update_layout(height=420, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return fig


def _extract_year(label: str) -> Optional[int]:
    if "(" in label and label.endswith(")"):
        try:
            return int(label.split("(")[-1].strip(")"))
        except ValueError:
            return None
    try:
        return int(label)
    except ValueError:
        return None


def calculate_percentage_change(
    df: pd.DataFrame,
    base_label: str,
    compare_label: str,
    columns: Optional[list] = None,
) -> pd.Series:
    """
    Calcula a variacao percentual entre dois anos (base vs comparado).
    Retorna serie com valores decimais (0.15 == 15%).
    """
    if columns is None:
        columns = ["salario_minimo", *MODEL_COLUMNS]

    base_row = df.loc[df["ano"] == base_label]
    compare_row = df.loc[df["ano"] == compare_label]
    if base_row.empty or compare_row.empty:
        raise ValueError("Nao foi possivel localizar os anos selecionados para comparacao.")

    base_values = base_row[columns].iloc[0].astype(float)
    compare_values = compare_row[columns].iloc[0].astype(float)
    return (compare_values / base_values) - 1


def calculate_cagr(
    df: pd.DataFrame,
    columns: Optional[list] = None,
) -> Dict[str, float]:
    """
    Calcula o CAGR (taxa de crescimento anual composta) para as colunas desejadas.
    """
    if columns is None:
        columns = ["salario_minimo", *MODEL_COLUMNS]

    years = df["ano"].apply(_extract_year).dropna()
    if years.empty:
        periods = len(df) - 1 if len(df) > 1 else 1
    else:
        periods = years.iloc[-1] - years.iloc[0]
        if periods <= 0:
            periods = len(df) - 1 if len(df) > 1 else 1

    if periods == 0:
        periods = 1

    growth: Dict[str, float] = {}
    for column in columns:
        initial = float(df.iloc[0][column])
        final = float(df.iloc[-1][column])
        if initial == 0:
            growth[column] = 0.0
            continue
        growth[column] = (final / initial) ** (1 / periods) - 1
    return growth


def compute_projection(df: pd.DataFrame) -> Dict[str, object]:
    """
    Retorna informacoes para projecao: label futuro, valores estimados e CAGR.
    """
    cagr = calculate_cagr(df)
    last_year = _extract_year(df["ano"].iloc[-1]) or 0
    next_year = last_year + 1 if last_year else None
    next_label = f"Projecao ({next_year})" if next_year else "Projecao"

    projected_values = {}
    for column in ["salario_minimo", *MODEL_COLUMNS]:
        projected_values[column] = float(df.iloc[-1][column]) * (1 + cagr[column])

    return {
        "label": next_label,
        "values": projected_values,
        "cagr": cagr,
        "next_year": next_year,
    }


def create_projection_chart(df: pd.DataFrame) -> go.Figure:
    """
    Cria um grafico com estimativa de preco e salario minimo para o proximo ano.
    """
    projection = compute_projection(df)
    next_label = projection["label"]
    projection_values = projection["values"]

    fig = go.Figure()
    for column in MODEL_COLUMNS:
        fig.add_trace(
            go.Scatter(
                x=df["ano"],
                y=df[column],
                mode="lines+markers",
                name=MODEL_TITLES[column],
                line=dict(color=COLOR_MAP[column], width=4),
                marker=dict(size=8),
                hovertemplate=(
                    "%{x}<br>Preco: R$ %{y:,.0f}<extra>"
                    f"{MODEL_TITLES[column]}</extra>"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
            x=[df["ano"].iloc[-1], next_label],
            y=[df[column].iloc[-1], projection_values[column]],
            mode="lines+markers",
            name=f"{MODEL_TITLES[column]} (proj.)",
            line=dict(color=COLOR_MAP[column], width=3, dash="dot"),
                marker=dict(size=9, symbol="diamond"),
                hovertemplate=(
                    "%{x}<br>Preco proj.: R$ %{y:,.0f}<extra>"
                    f"{MODEL_TITLES[column]} (proj.)</extra>"
                ),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df["ano"],
            y=df["salario_minimo"],
            mode="lines+markers",
            name="Salario minimo",
            line=dict(color=COLOR_MAP["salario_minimo"], width=3),
            marker=dict(size=8),
            yaxis="y2",
            hovertemplate="%{x}<br>Salario minimo: R$ %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df["ano"].iloc[-1], next_label],
            y=[df["salario_minimo"].iloc[-1], projection_values["salario_minimo"]],
            mode="lines+markers",
            name="Salario minimo (proj.)",
            line=dict(color=COLOR_MAP["salario_minimo"], width=3, dash="dot"),
            marker=dict(size=9, symbol="diamond"),
            yaxis="y2",
            hovertemplate="%{x}<br>Salario minimo proj.: R$ %{y:,.0f}<extra></extra>",
        )
    )

    fig = apply_dark_theme(fig, "Preco (R$)")
    fig.update_layout(
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis2=dict(
            title=dict(
                text="Salario minimo (R$)",
                font=dict(color="#e2e8f0", family="Inter, sans-serif"),
            ),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#e2e8f0"),
        ),
    )
    return fig


def create_percentage_change_chart(
    df: pd.DataFrame, base_label: str, compare_label: str
) -> go.Figure:
    """
    Cria um grafico de barras com a variacao percentual entre dois anos.
    """
    variation = calculate_percentage_change(df, base_label, compare_label)
    categories = ["Salario minimo", "iPhone (Base)", "iPhone Pro", "iPhone Pro Max"]
    keys = ["salario_minimo", *MODEL_COLUMNS]
    colors = [
        COLOR_MAP["salario_minimo"],
        COLOR_MAP["preco_base"],
        COLOR_MAP["preco_pro"],
        COLOR_MAP["preco_pro_max"],
    ]
    values = [variation[key] for key in keys]
    fig = go.Figure(
        go.Bar(
            x=categories,
            y=[value * 100 for value in values],
            marker=dict(color=colors),
            text=[format_percentage(value, 1) for value in values],
            textposition="outside",
            hovertemplate=(
                f"{compare_label} vs {base_label}<br>%{{x}}: %{{y:.1f}}%%<extra></extra>"
            ),
        )
    )
    fig = apply_dark_theme(fig, "Variacao percentual (%)")
    fig.update_layout(
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, r=40, b=80, l=60),
    )
    fig.update_yaxes(tickformat=".0f")
    return fig


def create_bar_chart(df: pd.DataFrame) -> go.Figure:
    precos_2021 = df.iloc[0][MODEL_COLUMNS]
    precos_2025 = df.iloc[-1][MODEL_COLUMNS]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Base", "Pro", "Pro Max"],
            y=precos_2021,
            name="Preco 2021",
            marker=dict(color=COLOR_MAP["comparativo_2021"]),
            offsetgroup="2021",
            text=[f"R${valor / 1000:.1f}k" for valor in precos_2021],
            textposition="outside",
            hovertemplate="2021<br>%{x}: R$ %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=["Base", "Pro", "Pro Max"],
            y=precos_2025,
            name="Preco 2025",
            marker=dict(color=COLOR_MAP["comparativo_2025"]),
            offsetgroup="2025",
            text=[f"R${valor / 1000:.1f}k" for valor in precos_2025],
            textposition="outside",
            hovertemplate="2025<br>%{x}: R$ %{y:,.0f}<extra></extra>",
        )
    )
    fig = apply_dark_theme(fig, "Preco (R$)")
    fig.update_layout(
        height=380,
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def create_donut_chart(df: pd.DataFrame) -> go.Figure:
    valores = df.iloc[-1][MODEL_COLUMNS]
    fig = go.Figure(
        go.Pie(
            labels=[MODEL_TITLES[col] for col in MODEL_COLUMNS],
            values=valores,
            hole=0.6,
            marker=dict(colors=[COLOR_MAP[col] for col in MODEL_COLUMNS]),
            textinfo="percent",
            insidetextorientation="horizontal",
            hovertemplate="%{label}<br>R$ %{value:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=380,
        paper_bgcolor="#0c101b",
        font=dict(color="#f1f5f9", family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.05, x=0.5, xanchor="center"),
    )
    fig.update_traces(textfont_size=16)
    return fig
