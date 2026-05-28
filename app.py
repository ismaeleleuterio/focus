"""
Dashboard Financeiro - Streamlit
Aplicação completa em um único arquivo
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from pathlib import Path
import re
from datetime import datetime
from scipy import stats  # <-- NOVA IMPORTAÇÃO


# =========================================================
# CONFIGURAÇÕES DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Dash Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    /* Estilo dos cards */
    .stCard {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #2c3e50;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    /* Tabelas */
    .dataframe {
        font-size: 0.85rem;
    }
    
    /* Cards de métricas personalizados */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 8px;
    }
    
    /* Tabela DRE */
    .dre-table {
        width: 100%;
        border-collapse: collapse;
    }
    .dre-table th {
        background-color: #2c3e50;
        color: white;
        padding: 8px;
        position: sticky;
        top: 0;
    }
    .dre-table td {
        padding: 6px 8px;
        border-bottom: 1px solid #e0e0e0;
    }
    .dre-table tr:hover {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SISTEMA DE LOGIN
# =========================================================

# Usuários cadastrados

# Usuários cadastrados
USUARIOS_CADASTRO = {
    # Admin
    "ismael": {"nivel": "admin", "nome_completo": "Ismael", "area": "admin", "senha": "ismael@741"},
    
    # Sócias
    "katia": {"nivel": "socios1", "nome_completo": "Katia", "area": "socios", "senha": "katia#852"},
    "cleia": {"nivel": "socios", "nome_completo": "Cleia", "area": "socios", "senha": "cleia$963"},
    "ianca": {"nivel": "socios", "nome_completo": "Ianca", "area": "socios", "senha": "ianca%159"},
    "maysa": {"nivel": "socios", "nome_completo": "Maysa", "area": "socios", "senha": "maysa&357"},
    "karolyne": {"nivel": "socios", "nome_completo": "Karolyne", "area": "socios", "senha": "karolyne*246"},
    "joane": {"nivel": "socios", "nome_completo": "Joane", "area": "socios", "senha": "joane@468"},
    
    # Acesso especial
    "claytiane": {"nivel": "socios", "nome_completo": "Claytiane", "area": "financeiro", "senha": "claytiane#579"},
    "renata": {"nivel": "admfin", "nome_completo": "Renata", "area": "Administrativo Financeiro", "senha": "renata@123"},
    
    # Líderes
    "victor": {"nivel": "lideres", "nome_completo": "Victor", "area": "administrativo", "senha": "victor$681"},
    "marialuana": {"nivel": "lideres", "nome_completo": "Maria Luana", "area": "rh", "senha": "marialuana%792"},
    "pedro": {"nivel": "lideres", "nome_completo": "Pedro", "area": "comercial", "senha": "pedro&913"},
    "tainah": {"nivel": "lideres", "nome_completo": "Tainah", "area": "marketing", "senha": "tainah*124"},
}

# Todas as páginas do sistema
TODAS_PAGINAS = [
    {"id": "painel", "nome": "Painel Geral", "href": "/", "icon": "house-door"},
    {"id": "financeiro", "nome": "Financeiro", "href": "/financeiro", "icon": "coin"},
    {"id": "tecnica", "nome": "Área Técnica", "href": "/area-tecnica", "icon": "gear"},
    {"id": "administrativo", "nome": "Administrativo", "href": "/administrativo", "icon": "briefcase"},
    {"id": "clientes", "nome": "Clientes", "href": "/clientes", "icon": "people"},
    {"id": "consultoria", "nome": "Consultoria", "href": "/consultoria", "icon": "graph-up"},
    {"id": "rh", "nome": "Recursos Humanos", "href": "/rh", "icon": "person-badge"},
    {"id": "comercial", "nome": "Comercial", "href": "/comercial", "icon": "cart"},
    {"id": "marketing", "nome": "Marketing", "href": "/marketing", "icon": "megaphone"},
    {"id": "configuracoes", "nome": "Configurações", "href": "/configuracoes", "icon": "sliders"},
]

def validar_login(usuario, senha_digitada):
    """Valida o login do usuário"""
    if usuario in USUARIOS_CADASTRO:
        dados_usuario = USUARIOS_CADASTRO[usuario]
        if senha_digitada == dados_usuario["senha"]:
            return True, dados_usuario["nivel"], dados_usuario["nome_completo"], dados_usuario["area"]
    return False, None, None, None

def get_paginas_por_usuario(nivel, area):
    """Retorna as páginas que o usuário pode acessar"""
    if nivel == "admin":
        return TODAS_PAGINAS
    elif nivel == "socios1":
        return [p for p in TODAS_PAGINAS if p["id"] != "configuracoes"]
    elif nivel == "admfin":
        return [p for p in TODAS_PAGINAS if p["id"] not in ["configuracoes", "rh", "marketing", "comercial"]]
    elif nivel == "socios":
        return [p for p in TODAS_PAGINAS if p["id"] not in ["configuracoes", "financeiro", "consultoria"]]
    elif nivel == "lideres":
        paginas_permitidas = [{"id": "painel", "nome": "Painel Geral", "href": "/", "icon": "house-door"}]
        
        area_pagina = {
            "financeiro": {"id": "financeiro", "nome": "Financeiro", "href": "/financeiro", "icon": "coin"},
            "administrativo": {"id": "administrativo", "nome": "Administrativo", "href": "/administrativo", "icon": "briefcase"},
            "rh": {"id": "rh", "nome": "Recursos Humanos", "href": "/rh", "icon": "person-badge"},
            "comercial": {"id": "comercial", "nome": "Comercial", "href": "/comercial", "icon": "cart"},
            "marketing": {"id": "marketing", "nome": "Marketing", "href": "/marketing", "icon": "megaphone"},
        }
        
        if area in area_pagina:
            paginas_permitidas.append(area_pagina[area])
        
        return paginas_permitidas
    return []

# =========================================================
# CARREGAMENTO DE DADOS
# =========================================================

# Configurações dos arquivos
ARQUIVOS_CONFIG = {
    "Rel_Titulo_Cfin_Analitico_AD_Des.xlsx": {"empresa": "Focus AD", "tipo": "Despesa"},
    "Rel_Titulo_Cfin_Analitico_AD_Rec.xlsx": {"empresa": "Focus AD", "tipo": "Receita"},
    "Rel_Titulo_Cfin_Analitico_IC_Des.xlsx": {"empresa": "Focus IC", "tipo": "Despesa"},
    "Rel_Titulo_Cfin_Analitico_IC_Rec.xlsx": {"empresa": "Focus IC", "tipo": "Receita"},
}

MAPA_GRUPOS_DRE = {
    "3.1.1.01 RECEITA DE PRESTAÇÃO DE SERVIÇOS": "Receita Bruta",
    "3.1.1.01 RECEITAS DE PRESTAÇÃO DE SERVIÇO": "Receita Bruta",
    "3.1.1.02 RECEITA CURSOS": "Receita Bruta",
    "3.1.1.03 RECEITA FINANCEIRA": "Receita Bruta",
    "3.2.1.01. IMPOSTOS SOBRE RECEITA": "Deduções",
    "3.2.1.02. DESCONTOS SOBRE VENDA": "Deduções",
    "4.1.1.01 CUSTOS MATERIAIS DIRETOS": "Custos Variáveis",
    "4.1.1.02 CUSTOS COM PESSOAL - TÉCNICOS": "Custos Variáveis",
    "4.1.1.03 CUSTOS COM ATENDIMENTO EXTERNO": "Custos Variáveis",
    "4.2.1.01 DESPESAS COM PESSOAL": "Custos Fixos",
    "4.2.1.02 DESPESAS ADMINISTRATIVAS": "Custos Fixos",
    "4.2.2.01 DESPESAS TRIBUTÁRIAS": "Custos Fixos",
    "4.2.3.01 DESPESAS FINANCEIRAS": "Custos Fixos",
    "5.1.01 MOVIMENTAÇÃO BANCÁRIA": "Movimentação Bancária",
    "6.1.1.01 DESPESAS NÃO DEDUTÍVEIS": "Antecipações e Retiradas de Lucros",
    "7.1.1.01 INVESTIMENTOS EM ESTRUTURA CLÍNICA": "Investimentos",
}

GRUPOS_NEGATIVOS = [
    "Deduções",
    "Custos Variáveis",
    "Custos Fixos",
    "Antecipações e Retiradas de Lucros",
    "Investimentos"
]

LINHA_RECEITA_BASE_AV = "Receita Bruta"

def encontrar_linha_inicio_dados(file_path):
    """Encontra a linha onde os dados realmente começam"""
    try:
        preview = pd.read_excel(file_path, header=None, nrows=20)
        for i, row in preview.iterrows():
            first_cell = str(row.iloc[0]) if len(row) > 0 else ""
            if 'Grupo' in first_cell or re.match(r'^\d+\.\d+\.\d+\.\d+', first_cell):
                return i
        return 7
    except Exception:
        return 7

def ler_arquivo_excel(file_path, sheet_name=0):
    """Lê um arquivo Excel tratando células mescladas"""
    start_row = encontrar_linha_inicio_dados(file_path)
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=start_row)
    df = df.rename(columns={df.columns[0]: "Grupo"})
    
    current_group = None
    for idx in range(len(df)):
        if pd.notna(df.loc[idx, "Grupo"]):
            current_group = df.loc[idx, "Grupo"]
        else:
            df.loc[idx, "Grupo"] = current_group
    
    df = df[df["Grupo"].notna()]
    df = df[df["Grupo"] != ""]
    df = df[~df["Grupo"].str.contains("Total", case=False, na=False)]
    
    col_map = {}
    for col in df.columns:
        col_str = str(col).strip()
        if "Conta Financeira" in col_str or col_str == "Conta":
            col_map[col] = "Conta Financeira"
        elif "Cliente" in col_str or "Fornecedor" in col_str:
            col_map[col] = "Cliente / Fornecedor"
        elif "Nº" in col_str or "Documento" in col_str:
            col_map[col] = "Nº Documento"
        elif "Dt. Vencto" in col_str or "Vencimento" in col_str:
            col_map[col] = "Dt. Vencto"
        elif "Dt. Pagto" in col_str or "Pagamento" in col_str:
            col_map[col] = "Dt. Pagamento"
        elif "Vl. Título" in col_str or "Título" in col_str:
            col_map[col] = "Vl. Título"
        elif "Vl. Juros" in col_str:
            col_map[col] = "Vl. Juros"
        elif "Vl. Desc." in col_str or "Desconto" in col_str:
            col_map[col] = "Vl. Desc."
        elif "Vl. Pago" in col_str or "Pago" in col_str:
            col_map[col] = "Vl. Pago"
    
    df = df.rename(columns=col_map)
    
    required_cols = ["Grupo", "Conta Financeira", "Dt. Pagamento", "Vl. Pago"]
    available_cols = [c for c in required_cols if c in df.columns]
    df = df[available_cols]
    
    df = df[df["Vl. Pago"].notna()]
    df = df[df["Vl. Pago"] != 0]
    
    return df

def carregar_todas_as_bases(diretorio_base="."):
    """Carrega todos os arquivos do diretório"""
    all_dfs = []
    diretorio = Path(diretorio_base)
    
    for arquivo, config in ARQUIVOS_CONFIG.items():
        file_path = diretorio / arquivo
        if not file_path.exists():
            continue
        
        try:
            df = ler_arquivo_excel(file_path)
            df["Empresa"] = config["empresa"]
            df["Natureza"] = config["tipo"]
            all_dfs.append(df)
        except Exception as e:
            pass
    
    if not all_dfs:
        return pd.DataFrame()
    
    return pd.concat(all_dfs, ignore_index=True)

def padronizar_dados(df):
    """Padroniza o DataFrame consolidado para análise"""
    if df.empty:
        return df
    
    df = df.copy()
    
    df["data"] = pd.to_datetime(df["Dt. Pagamento"], errors="coerce")
    df = df[df["data"].notna()]
    
    if df.empty:
        return df
    
    df["ano_mes"] = df["data"].dt.to_period("M")
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    
    meses_pt = {
        1: "jan", 2: "fev", 3: "mar", 4: "abr",
        5: "mai", 6: "jun", 7: "jul", 8: "ago",
        9: "set", 10: "out", 11: "nov", 12: "dez"
    }
    df["mes_label"] = df["mes"].map(meses_pt) + "/" + df["ano"].astype(str)
    
    df["Grupo"] = df["Grupo"].astype(str).str.strip().str.upper()
    df["Conta Financeira"] = df["Conta Financeira"].astype(str).str.strip()
    
    df["categoria_dre"] = df["Grupo"].map(MAPA_GRUPOS_DRE)
    
    df["valor"] = pd.to_numeric(df["Vl. Pago"], errors="coerce")
    df = df[df["valor"].notna()]
    
    if df.empty:
        return df
    
    for categoria in GRUPOS_NEGATIVOS:
        mask_neg = df["categoria_dre"] == categoria
        df.loc[mask_neg, "valor"] = -df.loc[mask_neg, "valor"].abs()
    
    mask_receita = df["categoria_dre"] == LINHA_RECEITA_BASE_AV
    df.loc[mask_receita, "valor"] = df.loc[mask_receita, "valor"].abs()
    
    return df

@st.cache_data
def get_dados():
    """Função principal que retorna os dados processados (com cache)"""
    df_raw = carregar_todas_as_bases(".")
    
    if df_raw.empty:
        return pd.DataFrame()
    
    return padronizar_dados(df_raw)

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def formato_contabil(valor):
    """Formata valor no formato contábil brasileiro"""
    if pd.isna(valor) or valor is None:
        return "R$ 0,00"
    valor_abs = abs(valor)
    texto = f"{valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"({texto})" if valor < 0 else f"R$ {texto}"

def formato_percentual(valor):
    """Formata valor percentual"""
    if pd.isna(valor) or valor is None:
        return "0,0%"
    valor_abs = abs(valor)
    texto = f"{valor_abs:.1f}%".replace(".", ",")
    return f"({texto})" if valor < 0 else texto

def ordenar_meses(meses_labels):
    """Ordena meses cronologicamente"""
    meses_map = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
                 "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}
    
    def ordem(mes_label):
        try:
            m, a = mes_label.split("/")
            return int(a) * 12 + meses_map.get(m.lower(), 0)
        except:
            return 0
    return sorted(meses_labels, key=ordem)

# =========================================================
# GRÁFICOS E VISUALIZAÇÕES
# =========================================================

CORES = {
    "receita": "#4A90D9",
    "despesa": "#E57373",
    "resultado": "#FFB74D",
    "custos_var": "#81C784",
    "custos_fixos": "#4FC3F7",
    "linha": "#90A4AE",
}

def criar_cards_indicadores():
    """Cria os cards de indicadores financeiros"""
    df = get_dados()
    
    if df.empty:
        col1, col2, col3, col4 = st.columns(4)
        for col in [col1, col2, col3, col4]:
            with col:
                st.metric("---", "R$ 0,00")
        return
    
    receita = df[df["categoria_dre"] == "Receita Bruta"]["valor"].sum()
    custos_var = df[df["categoria_dre"] == "Custos Variáveis"]["valor"].sum()
    custos_fixos = df[df["categoria_dre"] == "Custos Fixos"]["valor"].sum()
    resultado_op = receita + custos_var + custos_fixos
    resultado_liq = resultado_op + df[df["categoria_dre"] == "Antecipações e Retiradas de Lucros"]["valor"].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Receita Bruta", formato_contabil(receita))
    
    with col2:
        st.metric("Custos Variáveis", formato_contabil(abs(custos_var)))
    
    with col3:
        st.metric("Custos Fixos", formato_contabil(abs(custos_fixos)))
    
    with col4:
        st.metric("Resultado Líquido", formato_contabil(resultado_liq))

def criar_tabela_dre():
    """Cria a tabela DRE completa"""
    df = get_dados()
    
    if df.empty:
        st.warning("Sem dados disponíveis para gerar a DRE.")
        return
    
    dre_mensal = df.groupby(["mes_label", "categoria_dre"])["valor"].sum().unstack(fill_value=0)
    
    if dre_mensal.empty:
        st.warning("Sem dados mensais disponíveis.")
        return
    
    categorias = ["Receita Bruta", "Deduções", "Custos Variáveis", "Custos Fixos", "Antecipações e Retiradas de Lucros"]
    for cat in categorias:
        if cat not in dre_mensal.columns:
            dre_mensal[cat] = 0
    
    dre_mensal = dre_mensal[categorias]
    dre_mensal["Margem de Contribuição"] = dre_mensal["Receita Bruta"] + dre_mensal["Custos Variáveis"]
    dre_mensal["Resultado Operacional"] = dre_mensal["Margem de Contribuição"] + dre_mensal["Custos Fixos"]
    dre_mensal["Resultado Líquido"] = dre_mensal["Resultado Operacional"] + dre_mensal["Antecipações e Retiradas de Lucros"]
    
    meses_ordenados = ordenar_meses(dre_mensal.index.tolist())
    dre_mensal = dre_mensal.reindex(meses_ordenados)
    
    totais = dre_mensal.sum()
    
    # Construir tabela HTML
    html_table = '<table class="dre-table" style="width:100%; border-collapse: collapse;">'
    html_table += '<thead><tr style="background-color: #2c3e50; color: white;">'
    html_table += '<th style="padding: 8px; text-align: left;">Descrição</th>'
    for mes in meses_ordenados:
        html_table += f'<th style="padding: 8px; text-align: right;">{mes}</th>'
    html_table += '<th style="padding: 8px; text-align: right;">TOTAL PERÍODO</th>'
    html_table += '</td></thead><tbody>'
    
    linhas = [
        ("Receita Bruta", "Receita Bruta"),
        ("(-) Deduções", "Deduções"),
        ("(-) Custos Variáveis", "Custos Variáveis"),
        ("═" * 30, None),
        ("Margem de Contribuição", "Margem de Contribuição"),
        ("(-) Custos Fixos", "Custos Fixos"),
        ("═" * 30, None),
        ("Resultado Operacional", "Resultado Operacional"),
        ("(-) Antecipações e Retiradas de Lucros", "Antecipações e Retiradas de Lucros"),
        ("═" * 30, None),
        ("Resultado Líquido", "Resultado Líquido"),
    ]
    
    for desc, coluna in linhas:
        html_table += '<tr>'
        if desc.startswith("═"):
            html_table += f'<td style="padding: 6px 8px; text-align: center; background-color: #f0f0f0;">{desc}</td>'
            for _ in meses_ordenados:
                html_table += '<td style="padding: 6px 8px;"></td>'
            html_table += '<td style="padding: 6px 8px;"></td>'
        else:
            is_bold = desc in ["Margem de Contribuição", "Resultado Operacional", "Resultado Líquido"]
            style = 'font-weight: bold;' if is_bold else ''
            html_table += f'<td style="padding: 6px 8px; {style}">{desc}</td>'
            
            for mes in meses_ordenados:
                valor = dre_mensal.loc[mes, coluna] if coluna else 0
                html_table += f'<td style="padding: 6px 8px; text-align: right; font-family: monospace;">{formato_contabil(valor)}</td>'
            
            total = totais[coluna] if coluna else 0
            html_table += f'<td style="padding: 6px 8px; text-align: right; font-weight: bold; font-family: monospace;">{formato_contabil(total)}</td>'
        
        html_table += '</tr>'
    
    html_table += '</tbody><table>'
    
    st.markdown(html_table, unsafe_allow_html=True)

def criar_grafico_combinado():
    """Gráfico combinado de receita, despesas e resultado com média móvel e projeção"""
    df = get_dados()
    
    if df.empty:
        st.info("Sem dados disponíveis para este gráfico.")
        return None
    
    meses = ordenar_meses(df["mes_label"].unique())
    
    categorias_despesa = ["Custos Variáveis", "Custos Fixos", "Deduções", "Antecipações e Retiradas de Lucros", "Investimentos"]
    
    receita_mensal = []
    despesas_mensal = []
    resultado_mensal = []
    
    for mes in meses:
        df_mes = df[df["mes_label"] == mes]
        receita = df_mes[df_mes["categoria_dre"] == "Receita Bruta"]["valor"].sum()
        despesas = df_mes[df_mes["categoria_dre"].isin(categorias_despesa)]["valor"].sum()
        receita_mensal.append(receita)
        despesas_mensal.append(despesas)
        resultado_mensal.append(receita + despesas)
    
    # Calcular média móvel de 12 meses para o resultado (dados históricos)
    resultado_mm12 = []
    for i in range(len(resultado_mensal)):
        inicio = max(0, i - 11)  # últimos 12 meses (incluindo o atual)
        janela = resultado_mensal[inicio:i+1]
        media = sum(janela) / len(janela)
        resultado_mm12.append(media)
    
    # ===== PROJEÇÃO PARA 12 MESES À FRENTE =====
    from scipy import stats
    
    # Criar índice numérico para os meses históricos
    x_historico = list(range(len(resultado_mensal)))
    y_historico = resultado_mensal
    
    # Calcular regressão linear
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_historico, y_historico)
    
    # Projetar para os próximos 12 meses
    meses_futuros = []
    projecao_resultado = []
    
    # Último mês existente
    ultimo_mes = meses[-1]
    ultimo_ano = int(ultimo_mes.split("/")[1])
    ultimo_mes_num = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
                      "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}[ultimo_mes.split("/")[0]]
    
    # Gerar próximos 12 meses
    meses_pt_lista = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    
    for i in range(1, 13):
        novo_mes_num = ultimo_mes_num + i
        novo_ano = ultimo_ano + (novo_mes_num - 1) // 12
        novo_mes_idx = (novo_mes_num - 1) % 12
        mes_label = f"{meses_pt_lista[novo_mes_idx]}/{novo_ano}"
        meses_futuros.append(mes_label)
        
        # Valor projetado pela regressão
        x_futuro = len(resultado_mensal) + i - 1
        valor_projetado = slope * x_futuro + intercept
        projecao_resultado.append(valor_projetado)
    
    # Todos os meses (histórico + projeção)
    todos_meses = meses + meses_futuros
    todos_resultado = resultado_mensal + [None] * len(meses_futuros)
    todos_projecao = [None] * len(meses) + projecao_resultado
    
    fig = go.Figure()
    
    # Barras de Receita
    fig.add_trace(go.Bar(
        x=meses,
        y=receita_mensal,
        name="Receita Bruta",
        marker_color=CORES["receita"],
        marker_opacity=0.85,
        text=[formato_contabil(v) for v in receita_mensal],
        textposition="outside",
        textfont={"size": 9}
    ))
    
    # Barras de Despesas
    fig.add_trace(go.Bar(
        x=meses,
        y=despesas_mensal,
        name="Despesas",
        marker_color=CORES["despesa"],
        marker_opacity=0.85,
        text=[formato_contabil(v) for v in despesas_mensal],
        textposition="outside",
        textfont={"size": 9}
    ))
    
    # Linha do Resultado Histórico
    fig.add_trace(go.Scatter(
        x=meses,
        y=resultado_mensal,
        name="Resultado Líquido (Histórico)",
        mode="lines+markers",
        line=dict(color=CORES["resultado"], width=2.5),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor=f"rgba(255, 183, 77, 0.15)",
        text=[formato_contabil(v) for v in resultado_mensal],
        textposition="top center"
    ))
    
    # Linha da Média Móvel Histórica
    fig.add_trace(go.Scatter(
        x=meses,
        y=resultado_mm12,
        name="Média Móvel (12 meses)",
        mode="lines",
        line=dict(color="#7E57C2", width=2, dash="dot"),
        opacity=0.9
    ))
    
    # Linha de Projeção (tracejada)
    fig.add_trace(go.Scatter(
        x=todos_meses,
        y=todos_projecao,
        name="Projeção (12 meses)",
        mode="lines+markers",
        line=dict(color="#E91E63", width=2.5, dash="dash"),
        marker=dict(size=5, symbol="diamond"),
        text=[formato_contabil(v) if v is not None else "" for v in todos_projecao],
        textposition="top center"
    ))
    
    # Área de confiança/sombra para a projeção
    # Adicionar intervalo de confiança aproximado (baseado no erro padrão)
    projecao_superior = []
    projecao_inferior = []
    for i, val in enumerate(projecao_resultado):
        projecao_superior.append(val + (std_err * 1.96 * (i + 1) ** 0.5))
        projecao_inferior.append(val - (std_err * 1.96 * (i + 1) ** 0.5))
    
    todos_superior = [None] * len(meses) + projecao_superior
    todos_inferior = [None] * len(meses) + projecao_inferior
    
    fig.add_trace(go.Scatter(
        x=todos_meses,
        y=todos_superior,
        name="Intervalo de Confiança (95%)",
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))
    
    fig.add_trace(go.Scatter(
        x=todos_meses,
        y=todos_inferior,
        name="Intervalo de Confiança (95%)",
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(233, 30, 99, 0.1)",
        showlegend=True
    ))
    
    fig.update_layout(
        title="📊 Evolução Financeira - Série Histórica com Média Móvel e Projeção 12M",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500,
        barmode="group",
        bargap=0.25,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_yaxes(tickformat=",.0f", tickprefix="R$ ", gridcolor="#E0E0E0")
    fig.update_xaxes(gridcolor="#E0E0E0")
    
    # Adicionar anotação com a tendência
    tendencia_texto = f"Tendência: {'📈 Crescente' if slope > 0 else '📉 Decrescente'} (R$ {abs(slope):,.2f}/mês)".replace(",", "X").replace(".", ",").replace("X", ".")
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=tendencia_texto,
        showarrow=False,
        font=dict(size=10, color="#666666"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#cccccc",
        borderwidth=1,
        borderpad=4
    )
    
    return fig

def criar_grafico_custos_variaveis():
    """Gráfico de evolução dos custos variáveis"""
    df = get_dados()
    
    if df.empty:
        return None
    
    custos_var = df[df["categoria_dre"] == "Custos Variáveis"].copy()
    
    if custos_var.empty:
        return None
    
    evolucao = custos_var.groupby("mes_label")["valor"].sum().reset_index()
    meses_ordenados = ordenar_meses(evolucao["mes_label"].tolist())
    evolucao = evolucao.set_index("mes_label").reindex(meses_ordenados).reset_index()
    evolucao.columns = ["mes_label", "valor"]
    evolucao["valor_abs"] = evolucao["valor"].abs()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=evolucao["mes_label"],
        y=evolucao["valor_abs"],
        name="Custos Variáveis",
        mode="lines",
        line=dict(color=CORES["custos_var"], width=2.5),
        fill="tozeroy",
        fillcolor=f"rgba(129, 199, 132, 0.15)",
        text=[formato_contabil(v) for v in evolucao["valor"]],
        textposition="top center"
    ))
    
    fig.update_layout(
        title="📈 Evolução dos Custos Variáveis",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=350
    )
    fig.update_yaxes(tickformat=",.0f", tickprefix="R$ ", gridcolor="#E0E0E0")
    
    return fig

def criar_grafico_top5_custos_variaveis():
    """Gráfico top 5 contas de custos variáveis"""
    df = get_dados()
    
    if df.empty:
        return None
    
    custos_var = df[df["categoria_dre"] == "Custos Variáveis"].copy()
    
    if custos_var.empty:
        return None
    
    total_por_conta = custos_var.groupby("Conta Financeira")["valor"].sum().abs().sort_values(ascending=False)
    top5_contas = total_por_conta.head(5).index.tolist()
    
    evolucao_contas = custos_var.groupby(["mes_label", "Conta Financeira"])["valor"].sum().reset_index()
    evolucao_contas["valor_abs"] = evolucao_contas["valor"].abs()
    
    dados_plot = []
    for conta in top5_contas:
        df_conta = evolucao_contas[evolucao_contas["Conta Financeira"] == conta].copy()
        meses_ordenados = ordenar_meses(df_conta["mes_label"].tolist())
        df_conta = df_conta.set_index("mes_label").reindex(meses_ordenados).reset_index()
        df_conta.columns = ["mes_label", "Conta Financeira", "valor", "valor_abs"]
        df_conta["valor_abs"] = df_conta["valor_abs"].fillna(0)
        dados_plot.append((conta[:45], df_conta))
    
    outros = evolucao_contas[~evolucao_contas["Conta Financeira"].isin(top5_contas)].copy()
    if not outros.empty:
        outros_agrupado = outros.groupby("mes_label")["valor_abs"].sum().reset_index()
        meses_ordenados = ordenar_meses(outros_agrupado["mes_label"].tolist())
        outros_agrupado = outros_agrupado.set_index("mes_label").reindex(meses_ordenados).reset_index()
        outros_agrupado.columns = ["mes_label", "valor_abs"]
        outros_agrupado["valor_abs"] = outros_agrupado["valor_abs"].fillna(0)
        dados_plot.append(("Outros", outros_agrupado))
    
    cores_paleta = ["#4A90D9", "#50E3C2", "#F5A623", "#D0021B", "#8B572A", "#9B9B9B"]
    
    fig = go.Figure()
    
    for i, (nome, df_plot) in enumerate(dados_plot):
        if df_plot.empty:
            continue
        cor = cores_paleta[i % len(cores_paleta)]
        
        ultimo_valor = df_plot["valor_abs"].iloc[-1] if not df_plot.empty else 0
        ultimo_mes = df_plot["mes_label"].iloc[-1] if not df_plot.empty else ""
        
        fig.add_trace(go.Scatter(
            x=df_plot["mes_label"],
            y=df_plot["valor_abs"],
            name=nome,
            mode="lines",
            line=dict(color=cor, width=2),
            opacity=0.8,
            showlegend=False
        ))
        
        fig.add_annotation(
            x=ultimo_mes,
            y=ultimo_valor,
            text=nome,
            showarrow=False,
            font=dict(size=9, color=cor),
            xanchor="left",
            xshift=5,
            yanchor="middle"
        )
    
    fig.update_layout(
        title="📊 Top 5 Contas - Custos Variáveis",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=420,
        showlegend=False,
        margin=dict(r=150)
    )
    fig.update_yaxes(tickformat=",.0f", tickprefix="R$ ", gridcolor="#E0E0E0")
    
    return fig

def criar_grafico_custos_fixos():
    """Gráfico de evolução dos custos fixos"""
    df = get_dados()
    
    if df.empty:
        return None
    
    custos_fixos = df[df["categoria_dre"] == "Custos Fixos"].copy()
    
    if custos_fixos.empty:
        return None
    
    evolucao = custos_fixos.groupby("mes_label")["valor"].sum().reset_index()
    meses_ordenados = ordenar_meses(evolucao["mes_label"].tolist())
    evolucao = evolucao.set_index("mes_label").reindex(meses_ordenados).reset_index()
    evolucao.columns = ["mes_label", "valor"]
    evolucao["valor_abs"] = evolucao["valor"].abs()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=evolucao["mes_label"],
        y=evolucao["valor_abs"],
        name="Custos Fixos",
        mode="lines",
        line=dict(color=CORES["custos_fixos"], width=2.5),
        fill="tozeroy",
        fillcolor=f"rgba(79, 195, 247, 0.15)",
        text=[formato_contabil(v) for v in evolucao["valor"]],
        textposition="top center"
    ))
    
    fig.update_layout(
        title="📈 Evolução dos Custos Fixos",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=350
    )
    fig.update_yaxes(tickformat=",.0f", tickprefix="R$ ", gridcolor="#E0E0E0")
    
    return fig

def criar_grafico_top5_custos_fixos():
    """Gráfico top 5 contas de custos fixos"""
    df = get_dados()
    
    if df.empty:
        return None
    
    custos_fixos = df[df["categoria_dre"] == "Custos Fixos"].copy()
    
    if custos_fixos.empty:
        return None
    
    total_por_conta = custos_fixos.groupby("Conta Financeira")["valor"].sum().abs().sort_values(ascending=False)
    top5_contas = total_por_conta.head(5).index.tolist()
    
    evolucao_contas = custos_fixos.groupby(["mes_label", "Conta Financeira"])["valor"].sum().reset_index()
    evolucao_contas["valor_abs"] = evolucao_contas["valor"].abs()
    
    dados_plot = []
    for conta in top5_contas:
        df_conta = evolucao_contas[evolucao_contas["Conta Financeira"] == conta].copy()
        meses_ordenados = ordenar_meses(df_conta["mes_label"].tolist())
        df_conta = df_conta.set_index("mes_label").reindex(meses_ordenados).reset_index()
        df_conta.columns = ["mes_label", "Conta Financeira", "valor", "valor_abs"]
        df_conta["valor_abs"] = df_conta["valor_abs"].fillna(0)
        dados_plot.append((conta[:45], df_conta))
    
    outros = evolucao_contas[~evolucao_contas["Conta Financeira"].isin(top5_contas)].copy()
    if not outros.empty:
        outros_agrupado = outros.groupby("mes_label")["valor_abs"].sum().reset_index()
        meses_ordenados = ordenar_meses(outros_agrupado["mes_label"].tolist())
        outros_agrupado = outros_agrupado.set_index("mes_label").reindex(meses_ordenados).reset_index()
        outros_agrupado.columns = ["mes_label", "valor_abs"]
        outros_agrupado["valor_abs"] = outros_agrupado["valor_abs"].fillna(0)
        dados_plot.append(("Outros", outros_agrupado))
    
    cores_paleta = ["#4A90D9", "#50E3C2", "#F5A623", "#D0021B", "#8B572A", "#9B9B9B"]
    
    fig = go.Figure()
    
    for i, (nome, df_plot) in enumerate(dados_plot):
        if df_plot.empty:
            continue
        cor = cores_paleta[i % len(cores_paleta)]
        
        ultimo_valor = df_plot["valor_abs"].iloc[-1] if not df_plot.empty else 0
        ultimo_mes = df_plot["mes_label"].iloc[-1] if not df_plot.empty else ""
        
        fig.add_trace(go.Scatter(
            x=df_plot["mes_label"],
            y=df_plot["valor_abs"],
            name=nome,
            mode="lines",
            line=dict(color=cor, width=2),
            opacity=0.8,
            showlegend=False
        ))
        
        fig.add_annotation(
            x=ultimo_mes,
            y=ultimo_valor,
            text=nome,
            showarrow=False,
            font=dict(size=9, color=cor),
            xanchor="left",
            xshift=5,
            yanchor="middle"
        )
    
    fig.update_layout(
        title="📊 Top 5 Contas - Custos Fixos",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=420,
        showlegend=False,
        margin=dict(r=150)
    )
    fig.update_yaxes(tickformat=",.0f", tickprefix="R$ ", gridcolor="#E0E0E0")
    
    return fig

def criar_tabela_historico_custos():
    """Cria tabela com histórico de custos e sparklines"""
    df = get_dados()
    
    if df.empty:
        st.info("Sem dados de custos disponíveis.")
        return
    
    custos = df[df["categoria_dre"].isin(["Custos Variáveis", "Custos Fixos"])].copy()
    
    if custos.empty:
        st.info("Nenhum dado de custos encontrado.")
        return
    
    meses_ordenados = ordenar_meses(custos["mes_label"].unique())
    
    dados_agrupados = custos.groupby(["Conta Financeira", "mes_label"])["valor"].sum().abs().reset_index()
    pivot = dados_agrupados.pivot(index="Conta Financeira", columns="mes_label", values="valor").fillna(0)
    pivot = pivot[meses_ordenados] if all(m in pivot.columns for m in meses_ordenados) else pivot
    
    pivot["ACUMULADO_12M"] = pivot.sum(axis=1)
    
    categorias = custos[["Conta Financeira", "categoria_dre"]].drop_duplicates().set_index("Conta Financeira")
    pivot["Categoria"] = pivot.index.map(lambda x: categorias.loc[x, "categoria_dre"] if x in categorias.index else "-")
    
    total_geral = pivot["ACUMULADO_12M"].sum()
    pivot["PERCENTUAL"] = (pivot["ACUMULADO_12M"] / total_geral * 100) if total_geral > 0 else 0
    
    pivot = pivot.sort_values("ACUMULADO_12M", ascending=False)
    
    # Exibir tabela
    st.markdown("### 📋 Histórico de Custos (Variáveis e Fixos)")
    st.caption("Evolução mensal, acumulado do período e participação percentual")
    
    # Preparar dados para exibição
    tabela_dados = []
    for idx, row in pivot.head(20).iterrows():
        tabela_dados.append({
            "Conta Financeira": idx,
            "Categoria": row["Categoria"],
            "Acumulado (12 meses)": formato_contabil(row["ACUMULADO_12M"]),
            "% do Total": formato_percentual(row["PERCENTUAL"])
        })
    
    st.dataframe(
        pd.DataFrame(tabela_dados),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Conta Financeira": st.column_config.TextColumn("Conta Financeira", width="large"),
            "Categoria": st.column_config.TextColumn("Categoria", width="medium"),
            "Acumulado (12 meses)": st.column_config.TextColumn("Acumulado (12 meses)", width="medium"),
            "% do Total": st.column_config.TextColumn("% do Total", width="small"),
        }
    )
    
    st.caption(f"Total geral de custos: {formato_contabil(total_geral)}")

# =========================================================
# PÁGINAS DO SISTEMA
# =========================================================

def pagina_painel_geral():
    """Página Painel Geral"""
    st.title(f"Olá, {st.session_state.nome}!")
    st.header("Painel Geral")
    st.markdown("---")
    
    st.markdown("""
    Selecione uma das opções no menu lateral para acessar os dashboards.
    As informações consolidadas estão disponíveis na seção **Consultoria**.
    """)
    
    st.markdown("---")
    st.subheader("📌 Módulos disponíveis:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - 📊 **Consultoria** - Dashboard financeiro completo
        - 💰 **Financeiro** - Análises financeiras detalhadas
        - 🔧 **Área Técnica** - Métricas operacionais
        - 📋 **Administrativo** - Gestão administrativa
        """)
    with col2:
        st.markdown("""
        - 👥 **Clientes** - Base de clientes
        - 👥 **Recursos Humanos** - Gestão de pessoas
        - 🛒 **Comercial** - Vendas e negociações
        - 📢 **Marketing** - Campanhas e resultados
        """)

def pagina_consultoria():
    """Página de Consultoria com dashboard completo"""
    st.title("Consultoria Financeira")
    st.markdown("Dashboard consolidado das empresas Focus AD e Focus IC.")
    st.markdown("---")
    
    # Cards de indicadores
    criar_cards_indicadores()
    
    st.markdown("---")
    
    # DRE
    st.subheader("📋 Demonstração do Resultado (DRE)")
    criar_tabela_dre()
    
    st.markdown("---")
    
    # Gráfico combinado
    st.subheader("📊 Evolução Financeira")
    fig_combinado = criar_grafico_combinado()
    if fig_combinado:
        st.plotly_chart(fig_combinado, use_container_width=True)
    
    st.markdown("---")
    
    # Gráficos de custos em sequência (um embaixo do outro)
    st.subheader("📈 Análise de Custos Variáveis")
    fig_custos_var = criar_grafico_custos_variaveis()
    if fig_custos_var:
        st.plotly_chart(fig_custos_var, use_container_width=True)
    
    fig_top5_var = criar_grafico_top5_custos_variaveis()
    if fig_top5_var:
        st.plotly_chart(fig_top5_var, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("📈 Análise de Custos Fixos")
    fig_custos_fixos = criar_grafico_custos_fixos()
    if fig_custos_fixos:
        st.plotly_chart(fig_custos_fixos, use_container_width=True)
    
    fig_top5_fixos = criar_grafico_top5_custos_fixos()
    if fig_top5_fixos:
        st.plotly_chart(fig_top5_fixos, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela histórica
    criar_tabela_historico_custos()

def pagina_padrao(titulo):
    """Páginas padrão para módulos não implementados"""
    st.title(titulo)
    st.markdown("---")
    st.info("🚧 Esta página está em desenvolvimento. Em breve mais funcionalidades!")

# Mapeamento de páginas
PAGINAS = {
    "painel": pagina_painel_geral,
    "financeiro": lambda: pagina_padrao("Financeiro"),
    "tecnica": lambda: pagina_padrao("Área Técnica"),
    "administrativo": lambda: pagina_padrao("Administrativo"),
    "clientes": lambda: pagina_padrao("Clientes"),
    "consultoria": pagina_consultoria,
    "rh": lambda: pagina_padrao("Recursos Humanos"),
    "comercial": lambda: pagina_padrao("Comercial"),
    "marketing": lambda: pagina_padrao("Marketing"),
    "configuracoes": lambda: pagina_padrao("Configurações"),
}

# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def fazer_login():
    """Tela de login"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: #2c3e50;">Painel de Controladoria</h2>
                <hr>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        usuario = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            if usuario and senha:
                sucesso, nivel, nome, area = validar_login(usuario, senha)
                if sucesso:
                    st.session_state.logado = True
                    st.session_state.usuario = usuario
                    st.session_state.nivel = nivel
                    st.session_state.nome = nome
                    st.session_state.area = area
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")
            else:
                st.warning("Preencha usuário e senha!")

def fazer_logout():
    """Faz logout do usuário"""
    for key in ['logado', 'usuario', 'nivel', 'nome', 'area']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def main():
    """Função principal do aplicativo"""
    
    if not st.session_state.get('logado', False):
        fazer_login()
        return
    
    # Sidebar com menu
    with st.sidebar:
        st.image("FocusLogo.png")
        st.markdown("---")
        
        paginas = get_paginas_por_usuario(st.session_state.nivel, st.session_state.area)
        
        # Criar menu
        menu_options = [p["nome"] for p in paginas]
        menu_icons = [p["icon"] for p in paginas]
        
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=menu_icons,
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#2c3e50", "border-radius": "8px"},
                "icon": {"color": "white", "font-size": "1.2rem"},
                "nav-link": {
                    "color": "white",
                    "font-size": "0.9rem",
                    "text-align": "left",
                    "margin": "0.2rem 0",
                    "border-radius": "8px",
                    "padding": "0.6rem 1rem",
                },
                "nav-link-selected": {"background-color": "#1a6dd4"},
                "nav-link-hover": {"background-color": "#3a5a7a"},
            }
        )
        
        st.markdown("---")
        
        # Informações do usuário
        st.markdown(f"""
        <div style="padding: 0.5rem; background-color: #34495e; border-radius: 8px; margin-bottom: 1rem;">
            <small style="color: #bdc3c7;">👤 Usuário</small><br>
            <strong style="color: white;">{st.session_state.nome}</strong><br>
            <small style="color: #bdc3c7;">{st.session_state.nivel} | {st.session_state.area}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()
    
    # Executar página selecionada
    pagina_id = None
    for p in paginas:
        if p["nome"] == selected:
            pagina_id = p["id"]
            break
    
    if pagina_id and pagina_id in PAGINAS:
        PAGINAS[pagina_id]()
    else:
        pagina_painel_geral()

if __name__ == "__main__":
    main()

