from typing import Optional

import pandas as pd
import streamlit as st

from charts import (
    calcular_esforco,
    calculate_percentage_change,
    compute_projection,
    create_bar_chart,
    create_donut_chart,
    create_effort_line_chart,
    create_price_line_chart,
    create_percentage_change_chart,
    create_projection_chart,
    format_currency,
    format_decimal,
    format_percentage,
)
from data_models import (
    COLUMN_DISPLAY_NAMES,
    DISPLAY_TO_COLUMN,
    MODEL_COLUMNS,
    MODEL_LABELS,
    MODEL_TITLES,
)


def render_kpi_card(
    container,
    df: pd.DataFrame,
    efforts: pd.DataFrame,
    model_key: str,
    index: int,
    reference_value: Optional[float] = None,
) -> None:
    label = df["ano"].iloc[index]
    year = label.split("(")[-1].strip(")")
    suffix = year[-2:]
    model_label = MODEL_LABELS[MODEL_COLUMNS.index(model_key)]
    effort_value = efforts.iloc[index][model_key]
    preco = df.iloc[index][model_key]
    salario = df.iloc[index]["salario_minimo"]

    container.markdown(f"##### Esforco ({model_label} '{suffix})")
    container.markdown(
        f"<div style='font-size:1.8rem;font-weight:700;color:#f8fafc;'>"
        f"{format_decimal(effort_value)} salarios"
        "</div>",
        unsafe_allow_html=True,
    )

    expander = container.expander("Detalhes do calculo")
    expander.markdown(
        f"- Mede quantos salarios minimos eram necessarios para comprar **{MODEL_TITLES[model_key]}** no lancamento de **{label}**."
    )
    expander.markdown(
        f"- **Formula:** preco do {MODEL_TITLES[model_key]} em {year} / salario minimo de {year}."
    )
    expander.markdown(
        f"- **Calculo:** {format_currency(preco)} / {format_currency(salario)} = {format_decimal(effort_value)} salarios."
    )
    if reference_value is not None:
        diff = effort_value - reference_value
        if diff < 0:
            insight = (
                f"O esforco caiu {format_decimal(abs(diff))} salario(s) em relacao a 2021."
            )
        elif diff > 0:
            insight = (
                f"O esforco subiu {format_decimal(diff)} salario(s) em relacao a 2021."
            )
        else:
            insight = "O esforco ficou igual ao observado em 2021."
        expander.markdown(f"- **Insight:** {insight}")


def render_dashboard(df: pd.DataFrame) -> None:
    efforts = calcular_esforco(df)
    years_options = df["ano"].tolist()
    base_effort_2021 = efforts.iloc[0]["preco_base"]
    pro_max_effort_2021 = efforts.iloc[0]["preco_pro_max"]

    st.title("Analise de Precos: Lancamento iPhone (Brasil)")
    st.caption(
        "Objetivo: analisar a evolucao e a divergencia de precos (Base, Pro, Pro Max) "
        "entre 2021 e 2025, bem como o esforco de compra em salarios minimos."
    )

    kpi_cols = st.columns(4)
    render_kpi_card(kpi_cols[0], df, efforts, "preco_base", 0)
    render_kpi_card(kpi_cols[1], df, efforts, "preco_base", len(df) - 1, base_effort_2021)
    render_kpi_card(kpi_cols[2], df, efforts, "preco_pro_max", 0)
    render_kpi_card(
        kpi_cols[3],
        df,
        efforts,
        "preco_pro_max",
        len(df) - 1,
        pro_max_effort_2021,
    )

    st.divider()

    st.subheader("Comparacoes Percentuais Flexiveis")
    st.caption(
        "Escolha os anos para visualizar o aumento percentual de precos e do salario minimo."
    )
    comparison_cols = st.columns(2)
    base_year = comparison_cols[0].selectbox(
        "Ano base",
        years_options,
        index=0,
        key="comparison_base_year",
    )
    compare_year = comparison_cols[1].selectbox(
        "Ano comparado",
        years_options,
        index=len(years_options) - 1,
        key="comparison_target_year",
    )
    variation = calculate_percentage_change(df, base_year, compare_year)
    base_row = df.loc[df["ano"] == base_year].iloc[0]
    compare_row = df.loc[df["ano"] == compare_year].iloc[0]

    metrics_cols = st.columns(4)
    metric_map = [
        ("Salario minimo", "salario_minimo"),
        ("iPhone (Base)", "preco_base"),
        ("iPhone Pro", "preco_pro"),
        ("iPhone Pro Max", "preco_pro_max"),
    ]
    for col_component, (label, key) in zip(metrics_cols, metric_map):
        col_component.metric(
            label=label,
            value=format_currency(compare_row[key]),
            delta=format_percentage(variation[key]),
        )
        col_component.caption(
            f"{base_year}: {format_currency(base_row[key])} -> {compare_year}: {format_currency(compare_row[key])}"
        )

    st.plotly_chart(
        create_percentage_change_chart(df, base_year, compare_year),
        width="stretch",
    )

    st.divider()

    charts_row_1 = st.columns(2)
    with charts_row_1[0]:
        st.subheader("Evolucao do Esforco de Compra (salarios minimos)")
        st.caption("Normaliza o preco, mostrando o custo real em numero de salarios minimos.")
        st.plotly_chart(create_effort_line_chart(df), width="stretch")

    with charts_row_1[1]:
        st.subheader("Evolucao do Preco Nominal (R$) por Modelo")
        st.caption("Mostra a trajetoria do preco de lancamento de cada modelo no Brasil.")
        st.plotly_chart(create_price_line_chart(df), width="stretch")

    charts_row_2 = st.columns(2)
    with charts_row_2[0]:
        st.subheader("Comparativo de Preco Nominal: 2021 vs 2025")
        st.caption("Compara o primeiro e o ultimo ano da serie para cada modelo.")
        st.plotly_chart(create_bar_chart(df), width="stretch")

    with charts_row_2[1]:
        st.subheader("Distribuicao de Custo (Linha 17 / 2025)")
        st.caption("Representa a participacao de cada modelo no desembolso total em 2025.")
        st.plotly_chart(create_donut_chart(df), width="stretch")

    st.divider()

    st.subheader("Projecao estimada (CAGR)")
    st.caption(
        "Aplica o crescimento medio anual composto observado na serie para estimar valores do proximo ano."
    )
    projection = compute_projection(df)
    proj_cols = st.columns((1, 2))
    with proj_cols[0]:
        st.markdown("##### Crescimento medio anual")
        cagr = projection["cagr"]
        st.metric("Salario minimo", format_percentage(cagr["salario_minimo"]))
        st.metric("iPhone (Base)", format_percentage(cagr["preco_base"]))
        st.metric("iPhone Pro", format_percentage(cagr["preco_pro"]))
        st.metric("iPhone Pro Max", format_percentage(cagr["preco_pro_max"]))
        st.markdown("##### Estimativa para o proximo ano")
        next_label = projection["label"]
        projected_values = projection["values"]
        st.markdown(
            "\n".join(
                [
                    f"- **Salario minimo ({next_label})**: {format_currency(projected_values['salario_minimo'])}",
                    f"- **iPhone (Base)**: {format_currency(projected_values['preco_base'])}",
                    f"- **iPhone Pro**: {format_currency(projected_values['preco_pro'])}",
                    f"- **iPhone Pro Max**: {format_currency(projected_values['preco_pro_max'])}",
                ]
            )
        )
        st.info(
            "A projecao assume uma taxa de crescimento constante (CAGR)."
        )
    with proj_cols[1]:
        st.plotly_chart(create_projection_chart(df), width="stretch")


def render_editor(df: pd.DataFrame) -> None:
    st.title("Editor de Dados")
    st.caption("Altere os valores de preco e salario minimo e atualize o dashboard.")

    display_df = df.rename(columns=COLUMN_DISPLAY_NAMES).set_index("Ano")
    edited_df = st.data_editor(
        display_df,
        width="stretch",
        num_rows="fixed",
        key="editor",
    )

    if st.button("Atualizar Dashboard", type="primary"):
        restored = edited_df.reset_index().rename(columns=DISPLAY_TO_COLUMN)
        try:
            for column in ["salario_minimo", *MODEL_COLUMNS]:
                restored[column] = pd.to_numeric(restored[column], errors="coerce")
        except Exception:
            st.error("Nao foi possivel converter os valores. Verifique se todos os campos sao numericos.")
            return

        if restored[["salario_minimo", *MODEL_COLUMNS]].isnull().any().any():
            st.error("Preencha todos os campos com numeros validos.")
            return

        st.session_state["dataset"] = restored[list(COLUMN_DISPLAY_NAMES.keys())]
        st.success("Dados atualizados. Volte ao dashboard para visualizar os graficos.")
