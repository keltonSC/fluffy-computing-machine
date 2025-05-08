import pandas as pd
import streamlit as st

# Estilização moderna
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

# Carregamento com cache
@st.cache_data
def carregar_dados():
    df = pd.read_excel("empreendimentosfortaleza.xlsx", usecols=[
        "Nome do Empreendimento", "Construtora", "Status", "Segmento",
        "VGV Médio", "Endereço", "Bairro/Cidade", "Atualização google earth "
    ])
    df.columns = ["nome", "construtora", "status", "segmento", "vgv", "endereco", "bairro", "link"]

    if df["vgv"].dtype == "object":
        df["vgv"] = (
            df["vgv"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )

    df["vgv"] = pd.to_numeric(df["vgv"], errors="coerce").fillna(0)
    return df

df = carregar_dados()

# Sidebar com filtros
st.sidebar.header("🎯 Filtros de Busca")
enderecos = st.sidebar.multiselect("Bairro", sorted(df["endereco"].dropna().unique().tolist()), placeholder="")
empreendimento = st.sidebar.selectbox("Nome do Empreendimento", [""] + sorted(df["nome"].dropna().unique().tolist()))
construtora = st.sidebar.selectbox("Construtora", [""] + sorted(df["construtora"].dropna().unique().tolist()))
segmento = st.sidebar.selectbox("Segmento", [""] + sorted(df["segmento"].dropna().unique().tolist()))

st.sidebar.markdown("### Faixa de VGV")
vgv_min = st.sidebar.number_input("VGV mínimo (R$)", min_value=0, value=int(df["vgv"].min()), step=50000)
vgv_max = st.sidebar.number_input("VGV máximo (R$)", min_value=0, value=int(df["vgv"].max()), step=50000)

if st.sidebar.button("🔄 Limpar filtros"):
    st.experimental_rerun()

# Título principal com logo visível
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("### Painel de Empreendimentos")
with col2:
    st.image("logo.png", width=70)

# Aplicar filtros
filtrado = df.copy()
if enderecos:
    filtrado = filtrado[filtrado["endereco"].isin(enderecos)]
if empreendimento:
    filtrado = filtrado[filtrado["nome"].str.contains(empreendimento, case=False, na=False)]
if construtora:
    filtrado = filtrado[filtrado["construtora"] == construtora]
if segmento:
    filtrado = filtrado[filtrado["segmento"] == segmento]
filtrado = filtrado[(filtrado["vgv"] >= vgv_min) & (filtrado["vgv"] <= vgv_max)]

# Métricas principais
col1, _, _ = st.columns(3)
col1.metric("Empreendimentos", len(filtrado))

st.markdown("---")

# Mostrar resultados
for _, row in filtrado.iterrows():
    link_html = f"<a href='{row.link}' target='_blank' title='Link externo' style='text-decoration: none; color: #1565c0;'>🔗</a>" if pd.notna(row.link) else ""
    with st.container():
        st.markdown(f"""
            <div style='background-color: #ffffff; padding: 10px 15px; margin-bottom: 10px; border-left: 4px solid #0d47a1; border-radius: 6px;'>
                <strong style='font-size: 16px;'>🏢 {row.nome} {link_html}</strong><br>
<span style='font-size: 13px;'><b>Construtora:</b> {row.construtora} | <b>Status:</b> {row.status} | <b>Segmento:</b> {row.segmento} | <b>Bairro:</b> {row.bairro}</span>
</div>
        """, unsafe_allow_html=True)
