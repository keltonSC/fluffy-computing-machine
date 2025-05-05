import pandas as pd
import streamlit as st

# Estilização personalizada
page_bg_img = '''
<style>
body {
background-image: url("https://images.unsplash.com/photo-1568605114967-8130f3a36994");
background-size: cover;
background-attachment: fixed;
color: #fff;
}

[data-testid="stAppViewContainer"] > .main {
background: rgba(0, 0, 0, 0.6);
padding: 2rem;
border-radius: 10px;
}

.stSelectbox, .stSlider, .stTextInput, .stMultiSelect {
background-color: white !important;
color: black !important;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Carrega a planilha
df = pd.read_excel("empreendimentosfortaleza.xlsx", usecols=[
    "Nome do Empreendimento", "Construtora", "Status", "Segmento",
    "VGV Médio", "Endereço", "Bairro/Cidade"
])
df.columns = ["nome", "construtora", "status", "segmento", "vgv", "endereco", "bairro"]

# Limpa VGV
df["vgv"] = (
    df["vgv"].astype(str)
    .str.replace("R$", "", regex=False)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
)
df["vgv"] = pd.to_numeric(df["vgv"], errors="coerce").fillna(0)

# Título
st.title("\U0001F4C8 Painel de Empreendimentos")

# Filtros lado a lado
col1, col2, col3, col4 = st.columns(4)
with col1:
    enderecos = st.multiselect("Endereço", sorted(df["endereco"].dropna().unique().tolist()))
with col2:
    empreendimento = st.text_input("Nome do Empreendimento")
with col3:
    construtora = st.selectbox("Construtora", [""] + sorted(df["construtora"].dropna().unique().tolist()))
with col4:
    segmento = st.selectbox("Segmento", [""] + sorted(df["segmento"].dropna().unique().tolist()))

# Filtro de VGV separado (removendo o format com R$ que causava erro)
col_min, col_max = st.columns(2)
with col_min:
    vgv_min = st.number_input("VGV mínimo (R$)", min_value=0, value=int(df.vgv.min()), step=100000)
with col_max:
    vgv_max = st.number_input("VGV máximo (R$)", min_value=0, value=int(df.vgv.max()), step=100000)

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

# Mostrar total encontrado
st.markdown(f"### {len(filtrado)} empreendimentos encontrados")

# Mostrar resultados em caixas personalizadas
for _, row in filtrado.iterrows():
    with st.container():
        st.markdown("""
            <div style='background-color: rgba(255,255,255,0.15); padding: 15px; margin-bottom: 10px; border-radius: 10px;'>
                <h4 style='margin-bottom:5px;'>🏢 <b>{}</b></h4>
                <ul style='list-style: none; padding-left: 0;'>
                    <li><b>Construtora:</b> {}</li>
                    <li><b>Status:</b> {}</li>
                    <li><b>Segmento:</b> {}</li>
                    <li><b>VGV:</b> R$ {:,.2f}</li>
                    <li><b>Endereço:</b> {}</li>
                    <li><b>Bairro:</b> {}</li>
                </ul>
            </div>
        """.format(
            row.nome, row.construtora, row.status, row.segmento, row.vgv, row.endereco, row.bairro
        ), unsafe_allow_html=True)
