import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Estilização personalizada
page_bg_img = '''
<style>
body {
background-image: url("https://images.unsplash.com/photo-1568605114967-8130f3a36994");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
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
    "VGV Médio", "Endereço", "Bairro/Cidade", "Atualização google earth "
])
df.columns = ["nome", "construtora", "status", "segmento", "vgv", "endereco", "bairro", "link"]

# ✅ Correção do VGV com tratamento condicional
if df["vgv"].dtype == "object":
    df["vgv"] = (
        df["vgv"].astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)   # remove milhar
        .str.replace(",", ".", regex=False)  # converte decimal
        .str.strip()
    )

df["vgv"] = pd.to_numeric(df["vgv"], errors="coerce").fillna(0)

# Título
st.title("\U0001F4C8 Painel de Empreendimentos")

# Filtros principais
col1, col2, col3, col4 = st.columns(4)
with col1:
    enderecos = st.multiselect("Endereço", sorted(df["endereco"].dropna().unique().tolist()))
with col2:
    empreendimento = st.text_input("Nome do Empreendimento")
with col3:
    construtora = st.selectbox("Construtora", [""] + sorted(df["construtora"].dropna().unique().tolist()))
with col4:
    segmento = st.selectbox("Segmento", [""] + sorted(df["segmento"].dropna().unique().tolist()))

# Filtro de VGV manual com 2 campos
st.markdown("### Filtro por faixa de VGV")
col_min, col_max = st.columns(2)
with col_min:
    vgv_min = st.number_input("VGV mínimo (R$)", min_value=0, value=int(df["vgv"].min()), step=50000)
with col_max:
    vgv_max = st.number_input("VGV máximo (R$)", min_value=0, value=int(df["vgv"].max()), step=50000)

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

# Mostrar resultados
for _, row in filtrado.iterrows():
    link_html = f"<a href='{row.link}' target='_blank' title='Ver Book' style='color: #00ccff; text-decoration: none;'>🔗</a>" if pd.notna(row.link) else ""
    with st.container():
        st.markdown(f"""
            <div style='background-color: rgba(255,255,255,0.15); padding: 15px; margin-bottom: 10px; border-radius: 10px;'>
                <h4 style='margin-bottom:5px;'>🏢 <b>{row.nome}</b> {link_html}</h4>
                <ul style='list-style: none; padding-left: 0;'>
                    <li><b>Construtora:</b> {row.construtora}</li>
                    <li><b>Status:</b> {row.status}</li>
                    <li><b>Segmento:</b> {row.segmento}</li>
                    <li><b>VGV:</b> R$ {row.vgv:,.2f}</li>
                    <li><b>Bairro/Cidade:</b> {row.bairro}</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

# Gráfico de VGV por bairro
if not filtrado.empty:
    st.markdown("## 📊 Distribuição de VGV por Bairro")
    grafico_dados = filtrado.groupby("bairro")["vgv"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(grafico_dados["bairro"], grafico_dados["vgv"])
    ax.set_title(f"Distribuição de VGV por Bairro (R$ {vgv_min:,} a R$ {vgv_max:,})")
    ax.set_xlabel("Bairro")
    ax.set_ylabel("VGV Total (R$)")
    plt.xticks(rotation=45)
    plt.grid(axis="y")
    st.pyplot(fig)
