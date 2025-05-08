import pandas as pd
import streamlit as st
import re

# Estilo visual
st.markdown('''
<style>
body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stAppViewContainer"] > .main {
    padding: 2rem;
}
h1, h2, h3, h4 {
    color: #0d47a1;
}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    df = pd.read_excel("empreendimentosfortaleza.xlsx", usecols=[
        "Nome do Empreendimento",        # nome
        "Construtora",                   # construtora
        "Status",                        # status
        "Previsão de Entrega",           # entrega (coluna E)
        "Segmento",                      # segmento (coluna F)
        "VGV Médio",                     # vgv (coluna G)
        "Média  m²",                     # media_m2 (coluna H)
        "Bairro/Cidade",                 # bairro (coluna J)
        "Endereço",                      # endereco (coluna K)
        "Tipologia",                     # tipologia
        "Atualização google earth "      # link
    ])

    # Mapeando corretamente cada coluna
    df.columns = [
        "nome", "construtora", "status", "entrega", "segmento", "vgv",
        "media_m2", "bairro", "endereco", "tipologia", "link"
    ]

    # Formatação da data (somente mês/ano)
    df["entrega"] = pd.to_datetime(df["entrega"], errors="coerce").dt.strftime('%b/%Y')

    # Limpeza e conversão do VGV
    if df["vgv"].dtype == "object":
        df["vgv"] = (
            df["vgv"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
    df["vgv"] = pd.to_numeric(df["vgv"], errors="coerce").fillna(0)

    # Padronização do texto de segmento
    df["segmento"] = df["segmento"].astype(str).str.strip().str.title()

    # Extrair múltiplas metragens da string
    def extrair_metragens(metragem_str):
        if pd.isna(metragem_str):
            return []
        return [float(x) for x in re.findall(r"\d+\.?\d*", str(metragem_str).replace(",", "."))]

    df["metragem_lista"] = df["media_m2"].apply(extrair_metragens)
    df["metragem_min"] = df["metragem_lista"].apply(lambda x: min(x) if x else 0)
    df["metragem_max"] = df["metragem_lista"].apply(lambda x: max(x) if x else 0)

    return df

df = carregar_dados()

# Sidebar com filtros
st.sidebar.header("🎯 Filtros de Busca")
enderecos = st.sidebar.multiselect("Bairro", sorted(df["bairro"].dropna().unique().tolist()), placeholder="")
empreendimento = st.sidebar.selectbox("Nome do Empreendimento", [""] + sorted(df["nome"].dropna().unique().tolist()))
construtora = st.sidebar.selectbox("Construtora", [""] + sorted(df["construtora"].dropna().unique().tolist()))
segmentos_unicos = df["segmento"].dropna().astype(str).unique().tolist()
segmento = st.sidebar.selectbox("Segmento", [""] + sorted(segmentos_unicos))

st.sidebar.markdown("### Faixa de VGV")
vgv_min = st.sidebar.number_input("VGV mínimo (R$)", min_value=0, value=int(df["vgv"].min()), step=50000)
vgv_max = st.sidebar.number_input("VGV máximo (R$)", min_value=0, value=int(df["vgv"].max()), step=50000)

st.sidebar.markdown("### Faixa de M²")
m2_min = st.sidebar.number_input("Mínimo M²", min_value=0, value=int(df["metragem_min"].min()), step=5)
m2_max = st.sidebar.number_input("Máximo M²", min_value=0, value=int(df["metragem_max"].max()), step=5)

if st.sidebar.button("🔄 Limpar filtros"):
    st.experimental_rerun()

# Título e logo
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("### Painel de Empreendimentos")
with col2:
    st.image("logo.png", width=70)

# Aplicar filtros
filtrado = df.copy()
if enderecos:
    filtrado = filtrado[filtrado["bairro"].isin(enderecos)]
if empreendimento:
    filtrado = filtrado[filtrado["nome"].str.contains(empreendimento, case=False, na=False)]
if construtora:
    filtrado = filtrado[filtrado["construtora"] == construtora]
if segmento:
    filtrado = filtrado[filtrado["segmento"] == segmento]

filtrado = filtrado[(filtrado["vgv"] >= vgv_min) & (filtrado["vgv"] <= vgv_max)]
filtrado = filtrado[(filtrado["metragem_max"] >= m2_min) & (filtrado["metragem_min"] <= m2_max)]

# Métrica principal
col1, _, _ = st.columns(3)
col1.metric("Empreendimentos", len(filtrado))

st.markdown("---")

# Exibir cards
for _, row in filtrado.iterrows():
    link_html = f"<a href='{row.link}' target='_blank' title='Link externo' style='text-decoration: none; color: #1565c0;'>🔗</a>" if pd.notna(row.link) else ""
    metragem_exibida = ", ".join(f"{m:.0f}m²" for m in row.metragem_lista) if row.metragem_lista else "N/D"
    vgv_formatado = f"R$ {row.vgv:,.0f}".replace(",", ".").replace(".", ",", 1)
    tipologia = row.tipologia if pd.notna(row.tipologia) else "N/D"
    entrega = row.entrega if pd.notna(row.entrega) else "N/D"
    segmento = row.segmento if pd.notna(row.segmento) else "N/D"

    with st.container():
        st.markdown(f"""
        <div style='background-color: #ffffff; padding: 15px 20px; margin-bottom: 15px; border-left: 6px solid #0d47a1; border-radius: 10px; box-shadow: 0px 1px 5px rgba(0,0,0,0.1);'>
            <div style='font-size: 18px; font-weight: bold;'>🏢 {row.nome} {link_html}</div>
            <div style='font-size: 14px; margin-top: 6px;'>
                <b>Construtora:</b> {row.construtora}<br>
                <b>Status:</b> {row.status}<br>
                <b>Segmento:</b> {segmento}<br>
                <b>Tipologia:</b> {tipologia}<br><br>
                <b>VGV Médio:</b> {vgv_formatado}<br>
                <b>Bairro:</b> {row.bairro}<br>
                <b>Endereço:</b> {row.endereco}<br>
                <b>Média  m²:</b> {metragem_exibida}<br>
                <b>Previsão de entrega:</b> {entrega}
            </div>
        </div>
        """, unsafe_allow_html=True)
