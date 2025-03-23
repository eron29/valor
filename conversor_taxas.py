import streamlit as st
import math
import pandas as pd
import plotly.express as px

# ---------------- FUNÇÕES PRINCIPAIS ---------------- #

def calcular_valores(vp, vf, taxa_anual, dias_uteis):
    taxa_dia = None
    taxa_mensal = None

    if taxa_anual is not None:
        taxa_anual = taxa_anual / 100
        taxa_dia = (1 + taxa_anual) ** (1 / 252) - 1
        taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1

    if vp is None and taxa_dia is not None and vf is not None and dias_uteis is not None:
        vp = vf / ((1 + taxa_dia) ** dias_uteis)

    elif vf is None and taxa_dia is not None and vp is not None and dias_uteis is not None:
        vf = vp * ((1 + taxa_dia) ** dias_uteis)

    elif dias_uteis is None and taxa_dia is not None and vp is not None and vf is not None:
        dias_uteis = math.log(vf / vp) / math.log(1 + taxa_dia)

    elif taxa_anual is None and vp is not None and vf is not None and dias_uteis is not None:
        taxa_dia = (vf / vp) ** (1 / dias_uteis) - 1
        taxa_anual = (1 + taxa_dia) ** 252 - 1
        taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1

    return {
        "Valor Presente (VP)": vp,
        "Valor Futuro (VF)": vf,
        "Taxa Anual (%)": taxa_anual * 100 if taxa_anual is not None else None,
        "Taxa Mensal (%)": taxa_mensal * 100 if taxa_mensal is not None else None,
        "Taxa Diária (%)": taxa_dia * 100 if taxa_dia is not None else None,
        "Dias Úteis": dias_uteis
    }

def converter_taxa(taxa_base, de, para):
    fatores = {
        "Anual": 1,
        "Semestral": 2,
        "Mensal": 12,
        "Diária": 252
    }
    base_de = fatores[de]
    base_para = fatores[para]
    taxa_base_decimal = taxa_base / 100
    taxa_convertida = (1 + taxa_base_decimal) ** (base_de / base_para) - 1
    return taxa_convertida * 100

def gerar_tabela_valores(vp, taxa_dia, dias_uteis):
    valores = []
    for dia in range(dias_uteis + 1):
        valor = vp * ((1 + taxa_dia) ** dia)
        valores.append((dia, valor))
    df = pd.DataFrame(valores, columns=["Dia Útil", "Valor Acumulado"])
    return df

# ---------------- INTERFACE STREAMLIT ---------------- #

st.set_page_config(page_title="Calculadora Tesouro IPCA", layout="centered")
st.title("💰 Calculadora Financeira - Tesouro IPCA e Conversor de Taxas")

aba = st.tabs([
    "🧮 Calculadora de Investimento",
    "🔁 Conversor de Taxas",
    "📊 Carteira de Investimentos"
])

# ----------- ABA 1: CALCULADORA DE INVESTIMENTO ----------- #

with aba[0]:
    st.markdown("Preencha os campos que você souber e **deixe em branco o que deseja calcular**.")

    with st.form("formulario"):
        col1, col2 = st.columns(2)

        with col1:
            vp = st.text_input("Valor Presente (VP) [R$]", placeholder="ex: 13000")
            taxa_anual = st.text_input("Taxa Anual (%)", placeholder="ex: 7.33")

        with col2:
            vf = st.text_input("Valor Futuro (VF) [R$]", placeholder="ex: 15000")
            dias_uteis = st.text_input("Dias Úteis", placeholder="ex: 252")

        submitted = st.form_submit_button("Calcular")

    if submitted:
        def parse_valor(valor):
            try:
                return float(valor.replace(",", "."))
            except:
                return None

        resultado = calcular_valores(
            parse_valor(vp),
            parse_valor(vf),
            parse_valor(taxa_anual),
            parse_valor(dias_uteis)
        )

        st.subheader("📊 Resultado")
        for chave, valor in resultado.items():
            if valor is not None:
                if "R$" in chave or "VP" in chave or "VF" in chave:
                    st.write(f"**{chave}:** R$ {valor:,.2f}")
                elif "%" in chave:
                    st.write(f"**{chave}:** {valor:.5f} %")
                else:
                    st.write(f"**{chave}:** {valor:.2f}")
            else:
                st.write(f"**{chave}:** ❌ Não foi possível calcular.")

        if resultado["Valor Presente (VP)"] and resultado["Taxa Diária (%)"] and resultado["Dias Úteis"]:
            st.subheader("📋 Evolução do Investimento por Dia Útil")

            vp_calc = resultado["Valor Presente (VP)"]
            taxa_dia_calc = resultado["Taxa Diária (%)"] / 100
            dias_calc = int(resultado["Dias Úteis"])

            df_valores = gerar_tabela_valores(vp_calc, taxa_dia_calc, dias_calc)
            st.dataframe(df_valores, use_container_width=True)

            st.subheader("📈 Gráfico da Evolução do Investimento")
            fig = px.line(df_valores, x="Dia Útil", y="Valor Acumulado", title="Evolução do Valor Investido")
            st.plotly_chart(fig, use_container_width=True)

# ----------- ABA 2: CONVERSOR DE TAXAS ----------- #

with aba[1]:
    st.markdown("Converta taxas equivalentes entre períodos com capitalização composta.")

    col1, col2, col3 = st.columns(3)

    with col1:
        taxa_base = st.number_input("Informe a taxa base (%)", value=7.33, step=0.01)

    with col2:
        de_periodo = st.selectbox("Converter de:", ["Anual", "Semestral", "Mensal", "Diária"])

    with col3:
        para_periodo = st.selectbox("Para:", ["Anual", "Semestral", "Mensal", "Diária"])

    if st.button("Converter Taxa"):
        taxa_convertida = converter_taxa(taxa_base, de_periodo, para_periodo)
        st.success(f"📈 A taxa equivalente de {taxa_base:.4f}% ao {de_periodo.lower()} é **{taxa_convertida:.5f}% ao {para_periodo.lower()}**.")

# ----------- ABA 3: CARTEIRA DE INVESTIMENTOS ----------- #

with aba[2]:
    st.markdown("Monte sua carteira de investimentos definindo a alocação percentual em cada ativo.")

    valor_total = st.number_input("💰 Valor total a investir (R$)", min_value=0.0, value=10000.0, step=100.0)

    st.subheader("📁 Alocação por Ativo")

    ativos = {
        "Tesouro IPCA": 20,
        "Tesouro Selic": 20,
        "Ações": 20,
        "Fundos Imobiliários (FIIs)": 20,
        "Renda Fixa Bancária (CDB/LCI/LCA)": 15,
        "Caixa (Reserva)": 5
    }

    alocacoes = {}
    total_percentual = 0

    for ativo, default in ativos.items():
        pct = st.slider(f"{ativo} (%)", 0, 100, default)
        alocacoes[ativo] = pct
        total_percentual += pct

    if total_percentual != 100:
        st.error(f"A soma das alocações é {total_percentual}%. Por favor, ajuste para 100%.")
    else:
        st.subheader("📋 Tabela de Alocação")
        dados = []
        for ativo, pct in alocacoes.items():
            valor = valor_total * pct / 100
            dados.append({"Ativo": ativo, "Alocação (%)": pct, "Valor Alocado (R$)": valor})

        df_alocacao = pd.DataFrame(dados)
        st.dataframe(df_alocacao, use_container_width=True)

        st.subheader("📈 Gráfico de Alocação")
        df_pizza = pd.DataFrame(dados)
        fig = px.pie(df_pizza, values="Valor Alocado (R$)", names="Ativo", title="Distribuição da Carteira")
        st.plotly_chart(fig, use_container_width=True)
