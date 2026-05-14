import streamlit as st
import pandas as pd
import io
import numpy as np
from datetime import datetime
import calendar
from collections import defaultdict

# Configuração da página (DEVE ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Ferramentas de Gestão de Confecção",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
    <style>
        /* Estilos globais */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2rem;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        /* Cards principais de cliente */
        .client-card {
            background: white;
            border-radius: 12px;
            padding: 0;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            overflow: hidden;
        }
        
        .client-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        .client-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .client-header h3 {
            margin: 0;
            font-size: 1.2rem;
        }
        
        .client-stats {
            display: flex;
            gap: 15px;
            font-size: 0.85rem;
        }
        
        .stat-badge {
            background: rgba(255,255,255,0.2);
            padding: 4px 8px;
            border-radius: 6px;
        }
        
        .client-content {
            padding: 20px;
            display: none;
        }
        
        .client-content.expanded {
            display: block;
        }
        
        /* Cards de pedido */
        .order-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background-color: #f9f9f9;
            transition: all 0.2s ease;
            position: relative;
        }
        
        .order-card:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .order-card.prioridade {
            border-left: 4px solid #f44336;
            background: linear-gradient(90deg, #fff5f5 0%, #f9f9f9 100%);
        }
        
        .order-card.atencao {
            border-left: 4px solid #ff9800;
            background: linear-gradient(90deg, #fff9f0 0%, #f9f9f9 100%);
        }
        
        .order-card.ok {
            border-left: 4px solid #4caf50;
        }
        
        .order-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            cursor: pointer;
        }
        
        .order-number {
            font-weight: bold;
            font-size: 16px;
            color: #333;
        }
        
        .order-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 11px;
        }
        
        .status-prioridade {
            background-color: #f44336;
            color: white;
        }
        
        .status-atencao {
            background-color: #ff9800;
            color: white;
        }
        
        .status-ok {
            background-color: #4caf50;
            color: white;
        }
        
        .order-details {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
            font-size: 13px;
            display: none;
        }
        
        .order-details.expanded {
            display: block;
        }
        
        .detail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        
        .detail-item {
            background: white;
            padding: 8px;
            border-radius: 6px;
        }
        
        .detail-label {
            font-weight: bold;
            color: #666;
            font-size: 11px;
            text-transform: uppercase;
        }
        
        .detail-value {
            color: #333;
            font-size: 14px;
            margin-top: 4px;
        }
        
        .btn-detalhe {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 5px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }
        
        .btn-detalhe:hover {
            transform: scale(1.05);
        }
        
        /* Métricas e badges */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        /* Tabs e navegação */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            background-color: #f8f9fa;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Botões */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: transform 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
    </style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================
@st.cache_resource
def get_session_state():
    """Gerenciador de estado da sessão"""
    return st.session_state

def show_header():
    """Exibe cabeçalho da aplicação"""
    st.markdown("""
        <div class="main-header">
            <h1>🛠️ Ferramentas de Gestão de Confecção</h1>
            <p>Gerencie seus pedidos, agendamentos e estoque de forma inteligente</p>
        </div>
    """, unsafe_allow_html=True)

def show_metrics_grid(metrics):
    """Exibe grid de métricas"""
    cols = st.columns(len(metrics))
    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{icon} {value}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)

# ==================== FUNÇÕES ORIGINAIS (PRESERVADAS) ====================
def get_status(qtd, saldo_atual, saldo_calculado):
    """Determina o status do pedido baseado nas quantidades"""
    try:
        qtd = float(qtd) if pd.notna(qtd) else 0
        saldo_atual = float(saldo_atual) if pd.notna(saldo_atual) else 0
        saldo_calculado = float(saldo_calculado) if pd.notna(saldo_calculado) else 0
        
        if qtd > saldo_calculado:
            return "PRIORIDADE", "prioridade"
        elif qtd > saldo_atual:
            return "ATENÇÃO", "atencao"
        else:
            return "OK", "ok"
    except:
        return "OK", "ok"

def create_calendar_view(df_filtered):
    """Cria visualização de calendário com pedidos agrupados por data"""
    
    # Verificar se coluna de data existe
    if 'Dt. Agendamento' not in df_filtered.columns:
        st.warning("Coluna 'Dt. Agendamento' não encontrada no arquivo.")
        return
    
    # Agrupar pedidos por data
    df_filtered_clean = df_filtered.dropna(subset=['Dt. Agendamento'])
    
    if df_filtered_clean.empty:
        st.warning("Nenhum pedido com data de agendamento disponível para exibir no calendário.")
        return
    
    # Criar estrutura de dados para o calendário
    agendamentos = defaultdict(list)
    
    for _, row in df_filtered_clean.iterrows():
        try:
            data = row['Dt. Agendamento'].date()
        except:
            continue
            
        qtd = row.get('Qtd', 0)
        saldo_atual = row.get('Saldo Atual', 0)
        saldo_calc = row.get('Saldo Calc.', 0)
        
        status_text, status_class = get_status(qtd, saldo_atual, saldo_calc)
        
        agendamentos[data].append({
            'pedido': row.get('Pedido', 'N/A'),
            'produto': row.get('Produto', 'N/A'),
            'cliente': row.get('Cliente', 'N/A'),
            'qtd': qtd,
            'saldo_atual': saldo_atual,
            'saldo_calculado': saldo_calc,
            'valor': row.get('R$ Total Calc.', 0),
            'status': status_text,
            'status_class': status_class,
            'colecao': row.get('Coleção', 'N/A'),
            'operacao': row.get('Operação Produtiva', 'N/A'),
            'segmento': row.get('Segmento', 'N/A')
        })
    
    # Criar visualização de calendário
    st.subheader("📅 Calendário de Agendamentos")
    
    # Selecionar mês
    if agendamentos:
        primeiro_agendamento = min(agendamentos.keys())
        ultimo_agendamento = max(agendamentos.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            mes_selecionado = st.slider(
                "Selecione o mês",
                value=primeiro_agendamento.month,
                min_value=1,
                max_value=12,
                format="Mês %d"
            )
        with col2:
            ano_selecionado = st.number_input(
                "Ano",
                value=primeiro_agendamento.year,
                min_value=primeiro_agendamento.year,
                max_value=ultimo_agendamento.year
            )
        
        # Criar calendário
        st.markdown("---")
        
        cal = calendar.monthcalendar(ano_selecionado, mes_selecionado)
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        
        # Header do calendário
        cols = st.columns(7)
        for col, dia in zip(cols, dias_semana):
            col.markdown(f"<div style='text-align: center; font-weight: bold; padding: 10px;'>{dia}</div>", 
                        unsafe_allow_html=True)
        
        # Dias do calendário
        for semana in cal:
            cols = st.columns(7)
            for col, dia in zip(cols, semana):
                if dia == 0:
                    col.markdown("")
                else:
                    data_dia = datetime(ano_selecionado, mes_selecionado, dia).date()
                    
                    if data_dia in agendamentos:
                        pedidos_dia = agendamentos[data_dia]
                        
                        with col:
                            with st.expander(f"📌 **{dia}** ({len(pedidos_dia)} pedido(s))", 
                                           expanded=False):
                                for pedido in pedidos_dia:
                                    st.markdown(f"""
                                        <div style="margin-bottom: 10px; padding: 8px; border-left: 3px solid #ddd; background-color: #f5f5f5;">
                                            <b>Pedido #{pedido['pedido']}</b><br>
                                            <b>Cliente:</b> {pedido['cliente']}<br>
                                            <b>Produto:</b> {pedido['produto']}<br>
                                            <b>Qtd:</b> {pedido['qtd']}
                                        </div>
                                    """, unsafe_allow_html=True)
                    else:
                        col.markdown(f"<div style='text-align: center; padding: 10px; color: #ccc;'>{dia}</div>", 
                                    unsafe_allow_html=True)

# ==================== NOVA FUNÇÃO DE CARDS MELHORADA ====================
def create_enhanced_client_cards(df_filtered):
    """Cria cards de clientes com menu interativo para detalhamento de pedidos"""
    
    if 'Cliente' not in df_filtered.columns:
        st.warning("Coluna 'Cliente' não encontrada no arquivo.")
        return
    
    # Converter Cliente para string e ordenar
    df_filtered['Cliente_str'] = df_filtered['Cliente'].fillna("Desconhecido").astype(str)
    clients = sorted(df_filtered['Cliente_str'].unique(), key=str)
    
    # Inicializar estados expandidos no session_state
    if 'expanded_clients' not in st.session_state:
        st.session_state.expanded_clients = {}
    if 'expanded_orders' not in st.session_state:
        st.session_state.expanded_orders = {}
    
    # Para cada cliente, criar um card principal
    for client in clients:
        df_client = df_filtered[df_filtered['Cliente_str'] == client].copy()
        
        # Calcular estatísticas do cliente
        total_pedidos = len(df_client)
        total_prioridade = len(df_client[df_client['Status'] == 'PRIORIDADE'])
        total_atencao = len(df_client[df_client['Status'] == 'ATENÇÃO'])
        total_ok = len(df_client[df_client['Status'] == 'OK'])
        
        # Determinar cor do card baseado nos status
        if total_prioridade > 0:
            card_status = "prioridade"
            status_text = f"🔴 {total_prioridade} Prioridade(s)"
        elif total_atencao > 0:
            card_status = "atencao"
            status_text = f"🟠 {total_atencao} Atenção(ões)"
        else:
            card_status = "ok"
            status_text = f"🟢 {total_ok} OK"
        
        # Estado atual do card do cliente
        client_key = f"client_{client}"
        is_client_expanded = st.session_state.expanded_clients.get(client_key, False)
        
        # Card principal do cliente
        with st.container():
            # Header do cliente clicável
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h3 style="margin: 0;">👤 {client}</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <span class="stat-badge" style="background: #f0f0f0; padding: 5px 10px; border-radius: 8px;">
                            📦 {total_pedidos} pedido(s)
                        </span>
                        <span class="stat-badge" style="background: #f0f0f0; padding: 5px 10px; border-radius: 8px;">
                            {status_text}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Botão para expandir/colapsar
                button_label = "🔽 Detalhes" if not is_client_expanded else "🔼 Fechar"
                if st.button(button_label, key=f"btn_{client_key}", use_container_width=True):
                    st.session_state.expanded_clients[client_key] = not is_client_expanded
                    st.rerun()
            
            st.markdown("---")
            
            # Conteúdo do cliente (expansível)
            if is_client_expanded:
                # Mostrar pedidos em grid
                cols = st.columns(2)
                
                for idx, (_, row) in enumerate(df_client.iterrows()):
                    col_idx = idx % 2
                    
                    with cols[col_idx]:
                        # Obter dados do pedido
                        pedido_id = row.get('Pedido', 'N/A')
                        produto = row.get('Produto', 'N/A')
                        qtd = row.get('Qtd', 0)
                        saldo_atual = row.get('Saldo Atual', 0)
                        saldo_calc = row.get('Saldo Calc.', 0)
                        status_text, status_class = get_status(qtd, saldo_atual, saldo_calc)
                        
                        # Formatar data
                        data_str = "N/A"
                        if 'Dt. Agendamento' in row and pd.notna(row['Dt. Agendamento']):
                            try:
                                data_str = row['Dt. Agendamento'].strftime('%d/%m/%Y')
                            except:
                                data_str = str(row['Dt. Agendamento'])
                        
                        # Formatar valor
                        valor_str = "N/A"
                        if 'R$ Total Calc.' in row and pd.notna(row['R$ Total Calc.']):
                            try:
                                valor_str = f"R$ {float(row['R$ Total Calc.']):.2f}"
                            except:
                                valor_str = str(row['R$ Total Calc.'])
                        
                        # Chave única para este pedido
                        order_key = f"order_{client}_{pedido_id}"
                        is_order_expanded = st.session_state.expanded_orders.get(order_key, False)
                        
                        # Card do pedido com status visual
                        status_class_lower = status_class.lower()
                        
                        # Header do pedido
                        st.markdown(f"""
                            <div class="order-card {status_class_lower}">
                                <div class="order-header" onclick="this.nextElementSibling.classList.toggle('expanded')">
                                    <div>
                                        <span class="order-number">Pedido #{pedido_id}</span>
                                        <div style="font-size: 12px; color: #666; margin-top: 4px;">
                                            {produto}
                                        </div>
                                    </div>
                                    <div>
                                        <span class="order-status status-{status_class_lower}">{status_text}</span>
                                    </div>
                                </div>
                        """, unsafe_allow_html=True)
                        
                        # Botão de detalhes
                        if st.button(f"📋 Detalhes do Pedido #{pedido_id}", key=f"detail_btn_{order_key}", use_container_width=True):
                            st.session_state.expanded_orders[order_key] = not is_order_expanded
                            st.rerun()
                        
                        # Detalhes expandidos do pedido
                        if is_order_expanded:
                            st.markdown(f"""
                                <div class="order-details expanded">
                                    <div class="detail-grid">
                                        <div class="detail-item">
                                            <div class="detail-label">📦 Produto</div>
                                            <div class="detail-value">{produto}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">🔢 Código</div>
                                            <div class="detail-value">{row.get('Cód Prod', 'N/A')}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">📅 Data Agendamento</div>
                                            <div class="detail-value">{data_str}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">🏭 Operação</div>
                                            <div class="detail-value">{row.get('Operação Produtiva', 'N/A')}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">📊 Segmento</div>
                                            <div class="detail-value">{row.get('Segmento', 'N/A')}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">🎨 Coleção</div>
                                            <div class="detail-value">{row.get('Coleção', 'N/A')}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">📊 Quantidade Pedida</div>
                                            <div class="detail-value">{qtd:,.0f}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">📦 Saldo Atual</div>
                                            <div class="detail-value">{saldo_atual:,.0f}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">📈 Saldo Calculado</div>
                                            <div class="detail-value">{saldo_calc:,.0f}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">💰 Valor Total</div>
                                            <div class="detail-value">{valor_str}</div>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Rodapé do cliente com resumo
                st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-top: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>📊 Resumo do Cliente</strong>
                            </div>
                            <div style="display: flex; gap: 15px;">
                                <span>🔴 Prioridade: {total_prioridade}</span>
                                <span>🟠 Atenção: {total_atencao}</span>
                                <span>🟢 OK: {total_ok}</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            else:
                # Resumo compacto quando colapsado
                st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 10px 0;">
                        <div style="display: flex; gap: 20px; font-size: 14px;">
                            <span>📦 Total: {total_pedidos} pedidos</span>
                            <span>🔴 Prioridade: {total_prioridade}</span>
                            <span>🟠 Atenção: {total_atencao}</span>
                            <span>🟢 OK: {total_ok}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# ==================== FUNÇÃO PRINCIPAL ====================
def main():
    # Inicializar estado da sessão
    if 'confeccao_df' not in st.session_state:
        st.session_state.confeccao_df = None
    if 'agendamento_df' not in st.session_state:
        st.session_state.agendamento_df = None
    
    # Exibir cabeçalho
    show_header()
    
    # Menu lateral dinâmico
    with st.sidebar:
        st.markdown("## 🎯 Menu Principal")
        st.markdown("---")
        
        # Seleção de módulo principal
        modulo = st.radio(
            "Selecione o módulo:",
            ["📋 Filtro de Confecção", "📅 Agendamento de Pedidos", "📊 Dashboard"],
            index=0,
            format_func=lambda x: x.split(" ")[1] if " " in x else x
        )
        
        st.markdown("---")
        
        # Informações do sistema
        with st.expander("ℹ️ Sobre o Sistema"):
            st.markdown("""
                **Versão:** 3.0  
                **Desenvolvido para:** Gestão de Confecção  
                
                ### Funcionalidades:
                - ✅ Filtro avançado de dados
                - ✅ Agendamento de pedidos
                - ✅ Cards interativos por cliente
                - ✅ Detalhamento expansível
                - ✅ Priorização automática
            """)
        
        st.markdown("---")
        
        # Status do sistema
        st.markdown("### 📊 Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🟢 **Online**")
        with col2:
            st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    
    # Conteúdo principal baseado no módulo selecionado
    if modulo == "📋 Filtro de Confecção":
        render_confeccao_tab()
    elif modulo == "📅 Agendamento de Pedidos":
        render_agendamento_tab()
    else:
        render_dashboard()

def render_confeccao_tab():
    """Renderiza a aba de filtro de confecção"""
    st.markdown("## 📋 Filtro de Dados de Confecção")
    st.markdown("Faça o upload do seu banco de dados em Excel para começar a filtrar e agrupar as informações.")
    
    uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx", "xls"], key="confeccao_file")
    
    if uploaded_file is not None:
        try:
            # Carregar a planilha
            df = pd.read_excel(uploaded_file)
            
            # Limpar os nomes das colunas (remover espaços em branco no início e ao fim)
            df.columns = df.columns.str.strip()
            
            # Colunas esperadas no relatório
            expected_columns = ['Compra', 'Cód Confec', 'Confeccionado', 'Qtd', 'Qtd Ret', 'Saldo', 'Confeccao']
            
            # Identificar quais colunas existem no dataframe carregado
            available_cols = [col for col in expected_columns if col in df.columns]
            missing_cols = [col for col in expected_columns if col not in df.columns]
            
            if missing_cols:
                st.warning(f"Atenção: A planilha carregada não contém as seguintes colunas esperadas: {', '.join(missing_cols)}. O aplicativo funcionará com as colunas disponíveis.")
            
            # Filtrar o DataFrame apenas com as colunas que existem
            df_filtered = df[available_cols].copy()
            
            # Menu de filtros na sidebar
            st.sidebar.markdown("## 🔍 Filtros da Confecção")
            
            # 1. Filtro: Agrupar/Filtrar por confecção
            if 'Confeccao' in df_filtered.columns:
                df_filtered['Confeccao'] = df_filtered['Confeccao'].fillna("Vazio").astype(str)
                confeccoes = df_filtered['Confeccao'].unique().tolist()
                confeccoes.sort(key=str)
                selecionadas_confeccoes = st.sidebar.multiselect("Filtrar por Confecção:", options=confeccoes, default=confeccoes)
                if selecionadas_confeccoes:
                    df_filtered = df_filtered[df_filtered['Confeccao'].isin(selecionadas_confeccoes)]
                    
            # 2. Filtro: Contém no 'confeccionado'
            if 'Confeccionado' in df_filtered.columns:
                termo_busca = st.sidebar.text_input("Contém no nome Confeccionado:", value="")
                if termo_busca:
                    df_filtered['Confeccionado'] = df_filtered['Confeccionado'].fillna("").astype(str)
                    df_filtered = df_filtered[df_filtered['Confeccionado'].str.contains(termo_busca, case=False, na=False)]
                    
            # 3. Filtro: Múltiplos Cód. Confeccionado
            if 'Cód Confec' in df_filtered.columns:
                df_filtered['Cód Confec'] = df_filtered['Cód Confec'].fillna("").astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                cods = [c for c in df_filtered['Cód Confec'].unique().tolist() if c and c != '']
                cods.sort()
                
                st.sidebar.markdown("---")
                st.sidebar.markdown("**Filtro Avançado: Cód. Confeccionado**")
                arquivo_cods = st.sidebar.file_uploader("Upload Excel com lista de códigos", type=["xlsx", "xls"], key="upload_cods")
                
                codigos_do_arquivo = []
                if arquivo_cods is not None:
                    try:
                        df_cods = pd.read_excel(arquivo_cods)
                        if 'Cód Confec' in df_cods.columns:
                            serie_cods = df_cods['Cód Confec']
                        else:
                            serie_cods = df_cods.iloc[:, 0]
                            
                        serie_cods = serie_cods.fillna("").astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                        codigos_do_arquivo = [c for c in serie_cods.tolist() if c and c.lower() != 'nan']
                        codigos_do_arquivo = [c for c in codigos_do_arquivo if c in cods]
                        
                        if codigos_do_arquivo:
                            st.sidebar.success(f"{len(codigos_do_arquivo)} código(s) válido(s) encontrado(s).")
                        else:
                            st.sidebar.warning("Nenhum código correspondente encontrado.")
                    except Exception as e:
                        st.sidebar.error(f"Erro ao ler o arquivo: {e}")
                
                selecionados_cods = st.sidebar.multiselect("Cód. Confeccionado:", options=cods, default=codigos_do_arquivo)
                if selecionados_cods:
                    df_filtered = df_filtered[df_filtered['Cód Confec'].isin(selecionados_cods)]
            
            st.markdown("---")
            
            cols_numericas = [col for col in ['Qtd', 'Qtd Ret', 'Saldo'] if col in df_filtered.columns]
            if cols_numericas:
                for col in cols_numericas:
                    df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0)
            
            if 'Qtd' in df_filtered.columns and 'Qtd Ret' in df_filtered.columns:
                mask = df_filtered['Qtd'] > 0
                df_filtered['Percentual_Ret'] = 0.0
                df_filtered.loc[mask, 'Percentual_Ret'] = (df_filtered.loc[mask, 'Qtd Ret'] / df_filtered.loc[mask, 'Qtd']) * 100
                linhas_before = len(df_filtered)
                df_filtered = df_filtered[df_filtered['Percentual_Ret'] < 95]
                df_filtered = df_filtered.drop(columns=['Percentual_Ret'])
                linhas_removidas = linhas_before - len(df_filtered)
                if linhas_removidas > 0:
                    st.info(f"ℹ️ {linhas_removidas} linha(s) removida(s) por terem Qtd Ret ≥ 95% da Qtd.")
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Registros", len(df_filtered))
            if 'Qtd' in cols_numericas:
                col2.metric("Soma de Qtd", f"{df_filtered['Qtd'].sum():.0f}")
            if 'Qtd Ret' in cols_numericas:
                col3.metric("Soma de Qtd Ret", f"{df_filtered['Qtd Ret'].sum():.0f}")
            if 'Saldo' in cols_numericas:
                col4.metric("Soma de Saldo", f"{df_filtered['Saldo'].sum():.0f}")
            
            # Exibição dos dados
            if 'Confeccao' in df_filtered.columns:
                df_filtered['Confeccao'] = df_filtered['Confeccao'].astype(str)
                confeccoes_unicas = [c for c in df_filtered['Confeccao'].dropna().unique().tolist() if c and c != 'nan' and c != '']
                confeccoes_unicas.sort()
                
                nomes_abas = ["📋 Visão Geral", "📊 Resumo Agrupado"] + [f"📁 {conf}" for conf in confeccoes_unicas]
                abas = st.tabs(nomes_abas)
                
                with abas[0]:
                    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
                
                with abas[1]:
                    if cols_numericas:
                        df_agrupado = df_filtered.groupby('Confeccao')[cols_numericas].sum().reset_index()
                        st.dataframe(df_agrupado, use_container_width=True, hide_index=True)
                    else:
                        st.info("Não há colunas numéricas para realizar o agrupamento.")
                        
                for i, conf in enumerate(confeccoes_unicas):
                    with abas[i+2]:
                        df_aba = df_filtered[df_filtered['Confeccao'] == conf]
                        st.dataframe(df_aba, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_filtered, use_container_width=True, hide_index=True)
            
            # Exportação
            st.markdown("---")
            st.subheader("Exportar Relatórios")
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, sheet_name='Filtrado', index=False)
                if 'Confeccao' in df_filtered.columns and cols_numericas:
                    if 'df_agrupado' in locals():
                        df_agrupado.to_excel(writer, sheet_name='Agrupado', index=False)
                    
            st.download_button(
                label="⬇️ Baixar Excel",
                data=buffer.getvalue(),
                file_name="relatorio_confeccao_filtrado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
    else:
        st.info("👆 Por favor, faça o upload de um arquivo Excel acima para iniciar.")

def render_agendamento_tab():
    """Renderiza a aba de agendamento de pedidos"""
    st.markdown("## 📅 Agendamento de Pedidos")
    
    uploaded_file_agendamento = st.file_uploader(
        "Carregue o arquivo Excel com os pedidos",
        type=['xlsx', 'xls'],
        key="agendamento_file",
        help="Arquivo deve conter as colunas: Pedido, Cliente, Cód Prod, Produto, Qtd, R$ Total Calc., Operação Produtiva, Segmento, Saldo Atual, Coleção, Saldo Calc., Dt. Agendamento"
    )
    
    if uploaded_file_agendamento:
        try:
            df = pd.read_excel(uploaded_file_agendamento)
            df.columns = df.columns.str.strip()
            if 'Dt. Agendamento' in df.columns:
                df['Dt. Agendamento'] = pd.to_datetime(df['Dt. Agendamento'], errors='coerce')
            
            if df is not None and not df.empty:
                # Filtros na sidebar
                st.sidebar.markdown("## 🔍 Filtros do Agendamento")
                
                # Filtro por Operação Produtiva
                if 'Operação Produtiva' in df.columns:
                    operacoes = st.sidebar.multiselect(
                        "Operação Produtiva",
                        options=df['Operação Produtiva'].unique(),
                        help="Selecione uma ou mais operações"
                    )
                else:
                    operacoes = []
                
                # Filtro por Segmento
                if 'Segmento' in df.columns:
                    segmentos = st.sidebar.multiselect(
                        "Segmento",
                        options=df['Segmento'].unique(),
                        help="Selecione um ou mais segmentos"
                    )
                else:
                    segmentos = []
                
                # Filtro por Coleção
                if 'Coleção' in df.columns:
                    colecoes = st.sidebar.multiselect(
                        "Coleção",
                        options=df['Coleção'].unique(),
                        help="Selecione uma ou mais coleções"
                    )
                else:
                    colecoes = []
                
                # Filtro por Cliente
                if 'Cliente' in df.columns:
                    clientes = st.sidebar.multiselect(
                        "Cliente",
                        options=df['Cliente'].unique(),
                        help="Selecione um ou mais clientes"
                    )
                else:
                    clientes = []
                
                # Filtro por Status
                status_filtro = st.sidebar.multiselect(
                    "Status",
                    options=["PRIORIDADE", "ATENÇÃO", "OK"],
                    default=["PRIORIDADE", "ATENÇÃO", "OK"],
                    help="Selecione os status que deseja visualizar"
                )
                
                # Aplicar filtros
                df_filtered = df.copy()
                
                if operacoes and 'Operação Produtiva' in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered['Operação Produtiva'].isin(operacoes)]
                
                if segmentos and 'Segmento' in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered['Segmento'].isin(segmentos)]
                
                if colecoes and 'Coleção' in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered['Coleção'].isin(colecoes)]
                
                if clientes and 'Cliente' in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered['Cliente'].isin(clientes)]
                
                # Adicionar coluna de status
                if 'Qtd' in df_filtered.columns and 'Saldo Atual' in df_filtered.columns and 'Saldo Calc.' in df_filtered.columns:
                    df_filtered['Status'] = df_filtered.apply(
                        lambda row: get_status(row['Qtd'], row['Saldo Atual'], row['Saldo Calc.'])[0],
                        axis=1
                    )
                    df_filtered = df_filtered[df_filtered['Status'].isin(status_filtro)]
                else:
                    st.error("❌ Colunas necessárias não encontradas: 'Qtd', 'Saldo Atual' ou 'Saldo Calc.'")
                    st.stop()
                
                # Métricas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total de Pedidos", len(df_filtered))
                with col2:
                    prioridades = len(df_filtered[df_filtered['Status'] == 'PRIORIDADE'])
                    st.metric("🔴 Prioridades", prioridades)
                with col3:
                    atencoes = len(df_filtered[df_filtered['Status'] == 'ATENÇÃO'])
                    st.metric("🟠 Atenções", atencoes)
                with col4:
                    oks = len(df_filtered[df_filtered['Status'] == 'OK'])
                    st.metric("🟢 OK", oks)
                
                st.markdown("---")
                
                # Escolher visualização
                tab1, tab2 = st.tabs(["🎯 Cards por Cliente", "📅 Calendário"])
                
                with tab1:
                    if not df_filtered.empty:
                        create_enhanced_client_cards(df_filtered)
                    else:
                        st.warning("Nenhum pedido encontrado com os filtros selecionados.")
                
                with tab2:
                    if not df_filtered.empty:
                        create_calendar_view(df_filtered)
                    else:
                        st.warning("Nenhum pedido encontrado com os filtros selecionados.")
                
                # Tabela detalhada
                st.markdown("---")
                st.subheader("📋 Tabela Detalhada")
                
                display_cols = [col for col in [
                    'Pedido', 'Cliente', 'Cód Prod', 'Produto', 'Qtd', 
                    'Saldo Atual', 'Saldo Calc.', 'R$ Total Calc.', 
                    'Operação Produtiva', 'Segmento', 'Coleção', 'Dt. Agendamento', 'Status'
                ] if col in df_filtered.columns]
                
                df_display = df_filtered[display_cols].copy()
                
                if 'Dt. Agendamento' in df_display.columns:
                    df_display['Dt. Agendamento'] = df_display['Dt. Agendamento'].dt.strftime('%d/%m/%Y')
                
                st.dataframe(
                    df_display.sort_values('Pedido') if 'Pedido' in df_display.columns else df_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download
                csv = df_display.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Baixar dados filtrados (CSV)",
                    data=csv,
                    file_name=f"pedidos_agendados_{datetime.now().strftime('%d_%m_%Y')}.csv",
                    mime="text/csv"
                )
        
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    
    else:
        st.info("👆 Por favor, carregue um arquivo Excel para começar.")
        st.markdown("""
            ### 📝 Formato esperado do arquivo Excel:
            
            O arquivo deve conter as seguintes colunas:
            - **Pedido** - Identificador único do pedido
            - **Cliente** - Nome do cliente
            - **Cód Prod** - Código do produto
            - **Produto** - Nome do produto
            - **Qtd** - Quantidade solicitada
            - **R$ Total Calc.** - Valor total do pedido
            - **Operação Produtiva** - Tipo de operação
            - **Segmento** - Segmento de mercado
            - **Saldo Atual** - Estoque atual disponível
            - **Coleção** - Coleção do produto
            - **Saldo Calc.** - Estoque calculado/projetado
            - **Dt. Agendamento** - Data do agendamento
        """)

def render_dashboard():
    """Renderiza dashboard com visão geral"""
    st.markdown("## 📊 Dashboard de Gestão")
    st.markdown("Visão geral dos indicadores e métricas do sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📋 Módulo 1</div>
                <div class="metric-label">Filtro de Confecção</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            - ✅ Upload de arquivos Excel
            - ✅ Filtros avançados
            - ✅ Agrupamento por confecção
            - ✅ Exportação de relatórios
        """)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📅 Módulo 2</div>
                <div class="metric-label">Agendamento de Pedidos</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            - ✅ Calendário interativo
            - ✅ Cards por cliente expansíveis
            - ✅ Detalhamento de pedidos
            - ✅ Filtros por status
        """)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">⚡ Diferenciais</div>
                <div class="metric-label">Funcionalidades</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            - ✅ Interface responsiva
            - ✅ Cards interativos
            - ✅ Performance otimizada
            - ✅ Download rápido
        """)

# ==================== EXECUÇÃO PRINCIPAL ====================
if __name__ == "__main__":
    main()
