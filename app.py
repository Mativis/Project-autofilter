import streamlit as st
import pandas as pd
import io
import numpy as np
from datetime import datetime
import calendar
from collections import defaultdict

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Confecção",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
    <style>
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
        
        /* Cards de cliente */
        .client-card {
            background: white;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            overflow: hidden;
        }
        .client-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        .client-card.prioridade {
            border: 2px solid #f44336;
            background: linear-gradient(135deg, #fff5f5 0%, white 100%);
        }
        .client-card.atencao {
            border: 2px solid #ff9800;
            background: linear-gradient(135deg, #fff9f0 0%, white 100%);
        }
        .client-card.ok {
            border: 2px solid #4caf50;
            background: linear-gradient(135deg, #f1f8e9 0%, white 100%);
        }
        
        .client-header {
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .client-info {
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        .client-name {
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
        }
        .client-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
        }
        .client-badge.prioridade {
            background-color: #f44336;
            color: white;
        }
        .client-badge.atencao {
            background-color: #ff9800;
            color: white;
        }
        .client-badge.ok {
            background-color: #4caf50;
            color: white;
        }
        .client-stats {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .stat-item {
            background: rgba(0,0,0,0.05);
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 13px;
        }
        
        /* Cards de pedido */
        .order-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: white;
            transition: all 0.2s ease;
        }
        .order-card:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        .order-card.prioridade {
            border-left: 5px solid #f44336;
            background: linear-gradient(90deg, #fff5f5 0%, white 100%);
        }
        .order-card.atencao {
            border-left: 5px solid #ff9800;
            background: linear-gradient(90deg, #fff9f0 0%, white 100%);
        }
        .order-card.ok {
            border-left: 5px solid #4caf50;
        }
        
        /* Tabela de detalhes */
        .detail-table-container {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .detail-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            color: #333;
        }
        .filter-info {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 13px;
        }
        
        /* Métricas */
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
        
        /* Progress bar */
        .progress-bar {
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }
        .progress-fill {
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            padding: 3px 8px;
            font-size: 11px;
            text-align: right;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 11px;
        }
        .status-badge.prioridade {
            background-color: #f44336;
            color: white;
        }
        .status-badge.atencao {
            background-color: #ff9800;
            color: white;
        }
        .status-badge.ok {
            background-color: #4caf50;
            color: white;
        }
        
        /* Abas personalizadas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8f9fa;
            padding: 5px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
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
        
        /* Botões de ação */
        .action-button {
            margin-top: 10px;
        }
        
        /* Info box */
        .info-box {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #2196f3;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================
def safe_str(value):
    """Converte qualquer valor para string de forma segura"""
    if pd.isna(value):
        return ""
    if isinstance(value, (np.int64, np.int32, np.float64, np.float32)):
        return str(int(value)) if value == int(value) else str(value)
    return str(value)

def safe_hash(*args):
    """Gera hash seguro"""
    str_args = [safe_str(arg) for arg in args]
    combined = "_".join(str_args)
    return combined.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("|", "_").replace(":", "_")

def get_status(qtd, saldo_atual, saldo_calculado):
    """Determina o status do pedido"""
    try:
        qtd = float(qtd) if pd.notna(qtd) else 0
        saldo_atual = float(saldo_atual) if pd.notna(saldo_atual) else 0
        saldo_calculado = float(saldo_calculado) if pd.notna(saldo_calculado) else 0
        
        if qtd > saldo_calculado:
            return "PRIORIDADE", "prioridade", 3
        elif qtd > saldo_atual:
            return "ATENÇÃO", "atencao", 2
        else:
            return "OK", "ok", 1
    except:
        return "OK", "ok", 1

def get_client_status(pedidos_df):
    """Retorna o status mais alto entre os pedidos do cliente"""
    if 'Status' not in pedidos_df.columns or len(pedidos_df) == 0:
        return "OK", "ok", 1
    
    status_priority = {"PRIORIDADE": 3, "ATENÇÃO": 2, "OK": 1}
    pedidos_df['Status_priority'] = pedidos_df['Status'].map(status_priority).fillna(1)
    max_priority = pedidos_df['Status_priority'].max()
    
    for status, priority in status_priority.items():
        if priority == max_priority:
            if status == "PRIORIDADE":
                return "PRIORIDADE", "prioridade", 3
            elif status == "ATENÇÃO":
                return "ATENÇÃO", "atencao", 2
            else:
                return "OK", "ok", 1
    return "OK", "ok", 1

def filter_by_qtd_ret_percent(df, qtd_col='Qtd', qtd_ret_col='Qtd Ret', threshold=95):
    """Filtra linhas onde Qtd Ret é menor que threshold% da Qtd"""
    if qtd_col not in df.columns or qtd_ret_col not in df.columns:
        return df, 0
    
    df_filtered = df.copy()
    
    # Converter para numérico
    df_filtered[qtd_col] = pd.to_numeric(df_filtered[qtd_col], errors='coerce').fillna(0)
    df_filtered[qtd_ret_col] = pd.to_numeric(df_filtered[qtd_ret_col], errors='coerce').fillna(0)
    
    # Calcular percentual
    mask = df_filtered[qtd_col] > 0
    df_filtered['percentual_ret'] = 0.0
    df_filtered.loc[mask, 'percentual_ret'] = (df_filtered.loc[mask, qtd_ret_col] / df_filtered.loc[mask, qtd_col]) * 100
    
    # Filtrar (manter apenas linhas com percentual < threshold)
    linhas_antes = len(df_filtered)
    df_filtered = df_filtered[df_filtered['percentual_ret'] < threshold]
    linhas_removidas = linhas_antes - len(df_filtered)
    
    # Remover coluna auxiliar
    df_filtered = df_filtered.drop(columns=['percentual_ret'])
    
    return df_filtered, linhas_removidas

def validate_default_options(options, defaults):
    """Valida se os valores padrão existem nas opções"""
    if not defaults:
        return []
    if not options:
        return []
    return [d for d in defaults if d in options]

# ==================== FUNÇÃO DE TABELA DE DETALHES ====================
def show_detail_table(df_detalhes, title="📋 Detalhamento dos Pedidos", filter_info=None):
    """Exibe tabela detalhada com formatação profissional"""
    
    if df_detalhes.empty:
        st.info("Nenhum pedido encontrado para exibir.")
        return
    
    st.markdown(f"""
        <div class="detail-table-container">
            <div class="detail-title">{title}</div>
    """, unsafe_allow_html=True)
    
    if filter_info:
        st.markdown(f'<div class="filter-info">🔍 {filter_info}</div>', unsafe_allow_html=True)
    
    # Preparar dados para exibição
    display_cols = []
    column_config = {}
    
    if 'Pedido' in df_detalhes.columns:
        display_cols.append('Pedido')
        column_config['Pedido'] = st.column_config.TextColumn("Pedido", width="small")
    
    if 'Cliente' in df_detalhes.columns:
        display_cols.append('Cliente')
        column_config['Cliente'] = st.column_config.TextColumn("Cliente", width="medium")
    
    if 'Produto' in df_detalhes.columns:
        display_cols.append('Produto')
        column_config['Produto'] = st.column_config.TextColumn("Produto", width="large")
    
    if 'Cód Prod' in df_detalhes.columns:
        display_cols.append('Cód Prod')
        column_config['Cód Prod'] = st.column_config.TextColumn("Código", width="small")
    
    if 'Qtd' in df_detalhes.columns:
        display_cols.append('Qtd')
        column_config['Qtd'] = st.column_config.NumberColumn("Quantidade", format="%d")
    
    if 'Qtd Ret' in df_detalhes.columns:
        display_cols.append('Qtd Ret')
        column_config['Qtd Ret'] = st.column_config.NumberColumn("Qtd Retorno", format="%d")
    
    if 'Saldo Atual' in df_detalhes.columns:
        display_cols.append('Saldo Atual')
        column_config['Saldo Atual'] = st.column_config.NumberColumn("Saldo Atual", format="%d")
    
    if 'Saldo Calc.' in df_detalhes.columns:
        display_cols.append('Saldo Calc.')
        column_config['Saldo Calc.'] = st.column_config.NumberColumn("Saldo Projetado", format="%d")
    
    if 'R$ Total Calc.' in df_detalhes.columns:
        display_cols.append('R$ Total Calc.')
        column_config['R$ Total Calc.'] = st.column_config.NumberColumn("Valor Total", format="R$ %.2f")
    
    if 'Operação Produtiva' in df_detalhes.columns:
        display_cols.append('Operação Produtiva')
        column_config['Operação Produtiva'] = st.column_config.TextColumn("Operação", width="small")
    
    if 'Segmento' in df_detalhes.columns:
        display_cols.append('Segmento')
        column_config['Segmento'] = st.column_config.TextColumn("Segmento", width="small")
    
    if 'Coleção' in df_detalhes.columns:
        display_cols.append('Coleção')
        column_config['Coleção'] = st.column_config.TextColumn("Coleção", width="small")
    
    if 'Dt. Agendamento' in df_detalhes.columns:
        display_cols.append('Dt. Agendamento')
        column_config['Dt. Agendamento'] = st.column_config.DateColumn("Data Agendamento", format="DD/MM/YYYY")
    
    if 'Status' in df_detalhes.columns:
        display_cols.append('Status')
        column_config['Status'] = st.column_config.TextColumn("Status", width="small")
    
    # Criar dataframe para exibição
    df_display = df_detalhes[display_cols].copy()
    
    # Formatar datas
    if 'Dt. Agendamento' in df_display.columns:
        df_display['Dt. Agendamento'] = pd.to_datetime(df_display['Dt. Agendamento'], errors='coerce')
    
    # Exibir tabela
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config=column_config
    )
    
    # Estatísticas da tabela
    st.markdown(f"""
        <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
            <div style="display: flex; gap: 20px; flex-wrap: wrap; font-size: 13px;">
                <span>📊 Total de registros: <b>{len(df_detalhes)}</b></span>
    """, unsafe_allow_html=True)
    
    if 'Status' in df_detalhes.columns:
        prioridades = len(df_detalhes[df_detalhes['Status'] == 'PRIORIDADE'])
        atencoes = len(df_detalhes[df_detalhes['Status'] == 'ATENÇÃO'])
        oks = len(df_detalhes[df_detalhes['Status'] == 'OK'])
        st.markdown(f"""
                <span>🔴 Prioridades: <b>{prioridades}</b></span>
                <span>🟠 Atenções: <b>{atencoes}</b></span>
                <span>🟢 OK: <b>{oks}</b></span>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== FUNÇÃO DE CARDS COM TABELA INTEGRADA ====================
def create_enhanced_client_cards(df_filtered, status_filter=None):
    """Cria cards de clientes com tabela de detalhes integrada"""
    
    if 'Cliente' not in df_filtered.columns:
        st.warning("Coluna 'Cliente' não encontrada no arquivo.")
        return
    
    # Converter e preparar dados
    df_filtered = df_filtered.copy()
    df_filtered['Cliente_str'] = df_filtered['Cliente'].fillna("Desconhecido").astype(str)
    
    # Adicionar status aos pedidos se não existir
    if 'Status' not in df_filtered.columns:
        df_filtered['Status'] = df_filtered.apply(
            lambda row: get_status(row.get('Qtd', 0), row.get('Saldo Atual', 0), row.get('Saldo Calc.', 0))[0],
            axis=1
        )
    
    # Calcular status do cliente e agregar dados
    clientes_data = []
    clients = sorted(df_filtered['Cliente_str'].unique(), key=str)
    
    for client in clients:
        df_client = df_filtered[df_filtered['Cliente_str'] == client].copy()
        
        # Calcular estatísticas
        total_pedidos = len(df_client)
        total_prioridade = len(df_client[df_client['Status'] == 'PRIORIDADE']) if 'Status' in df_client.columns else 0
        total_atencao = len(df_client[df_client['Status'] == 'ATENÇÃO']) if 'Status' in df_client.columns else 0
        total_ok = len(df_client[df_client['Status'] == 'OK']) if 'Status' in df_client.columns else 0
        
        # Status do cliente (mais alto)
        client_status_text, client_status_class, client_priority = get_client_status(df_client)
        
        # Calcular percentual de conclusão
        percent_ok = (total_ok / total_pedidos * 100) if total_pedidos > 0 else 0
        
        # Aplicar filtro de status do cliente
        if status_filter:
            if status_filter == "PRIORIDADE" and client_priority != 3:
                continue
            elif status_filter == "ATENÇÃO" and client_priority != 2:
                continue
            elif status_filter == "OK" and client_priority != 1:
                continue
        
        clientes_data.append({
            'client': client,
            'df_client': df_client,
            'total_pedidos': total_pedidos,
            'total_prioridade': total_prioridade,
            'total_atencao': total_atencao,
            'total_ok': total_ok,
            'client_status_text': client_status_text,
            'client_status_class': client_status_class,
            'percent_ok': percent_ok
        })
    
    # Inicializar estados
    if 'expanded_clients' not in st.session_state:
        st.session_state.expanded_clients = {}
    if 'selected_client_for_table' not in st.session_state:
        st.session_state.selected_client_for_table = None
    
    # Renderizar cards
    for client_data in clientes_data:
        client = client_data['client']
        df_client = client_data['df_client']
        total_pedidos = client_data['total_pedidos']
        total_prioridade = client_data['total_prioridade']
        total_atencao = client_data['total_atencao']
        total_ok = client_data['total_ok']
        client_status_text = client_data['client_status_text']
        client_status_class = client_data['client_status_class']
        percent_ok = client_data['percent_ok']
        
        # Estado do card
        client_key = safe_hash("client", client)
        is_client_expanded = st.session_state.expanded_clients.get(client_key, False)
        
        # Card do cliente
        st.markdown(f"""
            <div class="client-card {client_status_class}">
                <div class="client-header">
                    <div class="client-info">
                        <span class="client-name">👤 {client}</span>
                        <span class="client-badge {client_status_class}">{client_status_text}</span>
                    </div>
                    <div class="client-stats">
                        <div class="stat-item">📦 {total_pedidos} pedido(s)</div>
                        <div class="stat-item">🔴 {total_prioridade}</div>
                        <div class="stat-item">🟠 {total_atencao}</div>
                        <div class="stat-item">🟢 {total_ok}</div>
                    </div>
                </div>
        """, unsafe_allow_html=True) 
        
        # Botões
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            button_label = "🔽 Ver Pedidos" if not is_client_expanded else "🔼 Fechar"
            if st.button(button_label, key=f"btn_{client_key}", use_container_width=True):
                st.session_state.expanded_clients[client_key] = not is_client_expanded
                st.rerun()
        
        with col2:
            if st.button(f"📋 Ver Tabela", key=f"table_{client_key}", use_container_width=True):
                st.session_state.selected_client_for_table = client
                st.rerun()
        
        # Conteúdo expandido (cards)
        if is_client_expanded:
            st.markdown('<div style="padding: 0 20px 20px 20px;">', unsafe_allow_html=True)
            
            if len(df_client) == 0:
                st.info("Nenhum pedido encontrado para este cliente.")
            else:
                # Grid de pedidos em cards
                cols = st.columns(2)
                
                for idx, (_, row) in enumerate(df_client.iterrows()):
                    col_idx = idx % 2
                    
                    with cols[col_idx]:
                        pedido_id = safe_str(row.get('Pedido', 'N/A'))
                        produto = row.get('Produto', 'N/A')
                        
                        try:
                            qtd = float(row.get('Qtd', 0)) if pd.notna(row.get('Qtd')) else 0
                            saldo_atual = float(row.get('Saldo Atual', 0)) if pd.notna(row.get('Saldo Atual')) else 0
                            saldo_calc = float(row.get('Saldo Calc.', 0)) if pd.notna(row.get('Saldo Calc.')) else 0
                        except:
                            qtd = 0
                            saldo_atual = 0
                            saldo_calc = 0
                        
                        status_text, status_class, _ = get_status(qtd, saldo_atual, saldo_calc)
                        
                        # Calcular percentual de estoque
                        percent_estoque = (saldo_atual / qtd * 100) if qtd > 0 else 0
                        estoque_color = "#f44336" if percent_estoque < 30 else "#ff9800" if percent_estoque < 70 else "#4caf50"
                        
                        # Formatar data
                        data_str = "N/A"
                        if 'Dt. Agendamento' in row and pd.notna(row['Dt. Agendamento']):
                            try:
                                if hasattr(row['Dt. Agendamento'], 'strftime'):
                                    data_str = row['Dt. Agendamento'].strftime('%d/%m/%Y')
                            except:
                                data_str = str(row['Dt. Agendamento'])
                        
                        # Formatar valor
                        valor_str = "N/A"
                        if 'R$ Total Calc.' in row and pd.notna(row['R$ Total Calc.']):
                            try:
                                valor = float(row['R$ Total Calc.'])
                                valor_str = f"R$ {valor:,.2f}"
                            except:
                                valor_str = str(row['R$ Total Calc.'])
                        
                        st.markdown(f"""
                            <div class="order-card {status_class}">
                                <div style="margin-bottom: 10px;">
                                    <div style="font-weight: bold;">Pedido #{pedido_id}</div>
                                    <div style="font-size: 12px; color: #666;">{safe_str(produto)[:60]}</div>
                                    <div style="font-size: 11px; color: #999;">📅 {data_str}</div>
                                </div>
                                <div style="display: flex; gap: 15px; font-size: 12px; margin: 10px 0; flex-wrap: wrap;">
                                    <span>📊 Qtd: {qtd:,.0f}</span>
                                    <span>📦 Saldo: {saldo_atual:,.0f}</span>
                                    <span>💰 {valor_str}</span>
                                </div>
                                <div>
                                    <div style="font-size: 11px;">Estoque: {percent_estoque:.0f}%</div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: {percent_estoque}%; background: {estoque_color};"></div>
                                    </div>
                                </div>
                                <div style="margin-top: 8px;">
                                    <span class="status-badge {status_class}">{status_text}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Tabela de detalhes do cliente selecionado
    if st.session_state.selected_client_for_table:
        client_selected = st.session_state.selected_client_for_table
        df_client_selected = next((c['df_client'] for c in clientes_data if c['client'] == client_selected), None)
        
        if df_client_selected is not None and not df_client_selected.empty:
            st.markdown("---")
            show_detail_table(
                df_client_selected, 
                title=f"📋 Detalhamento - Cliente: {client_selected}",
                filter_info=f"Mostrando {len(df_client_selected)} pedido(s) do cliente {client_selected}"
            )
            
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("🔒 Fechar Tabela", key="close_client_table"):
                    st.session_state.selected_client_for_table = None
                    st.rerun()

# ==================== FUNÇÃO DE CALENDÁRIO COM TABELA INTEGRADA ====================
def create_calendar_view(df_filtered):
    """Cria visualização de calendário com tabela de detalhes integrada"""
    
    if 'Dt. Agendamento' not in df_filtered.columns:
        st.warning("Coluna 'Dt. Agendamento' não encontrada no arquivo.")
        return
    
    df_filtered_clean = df_filtered.dropna(subset=['Dt. Agendamento']).copy()
    
    if df_filtered_clean.empty:
        st.warning("Nenhum pedido com data de agendamento disponível.")
        return
    
    # Converter para data
    df_filtered_clean['Data'] = pd.to_datetime(df_filtered_clean['Dt. Agendamento']).dt.date
    
    # Inicializar estado
    if 'selected_calendar_date' not in st.session_state:
        st.session_state.selected_calendar_date = None
    
    # Agrupar por data
    agendamentos = defaultdict(list)
    for _, row in df_filtered_clean.iterrows():
        data = row['Data']
        qtd = row.get('Qtd', 0)
        saldo_atual = row.get('Saldo Atual', 0)
        saldo_calc = row.get('Saldo Calc.', 0)
        status_text, status_class, _ = get_status(qtd, saldo_atual, saldo_calc)
        
        agendamentos[data].append({
            'pedido': safe_str(row.get('Pedido', 'N/A')),
            'produto': safe_str(row.get('Produto', 'N/A'))[:50],
            'cliente': safe_str(row.get('Cliente', 'N/A')),
            'qtd': qtd,
            'status': status_text,
            'status_class': status_class
        })
    
    st.subheader("📅 Calendário de Agendamentos")
    
    if agendamentos:
        primeiro_agendamento = min(agendamentos.keys())
        ultimo_agendamento = max(agendamentos.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            mes_selecionado = st.slider("Mês", value=primeiro_agendamento.month, min_value=1, max_value=12)
        with col2:
            ano_selecionado = st.number_input("Ano", value=primeiro_agendamento.year, 
                                              min_value=primeiro_agendamento.year, 
                                              max_value=ultimo_agendamento.year)
        
        st.markdown("---")
        
        cal = calendar.monthcalendar(ano_selecionado, mes_selecionado)
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        
        cols = st.columns(7)
        for col, dia in zip(cols, dias_semana):
            col.markdown(f"<div style='text-align: center; font-weight: bold; padding: 10px;'>{dia}</div>", unsafe_allow_html=True)
        
        for semana in cal:
            cols = st.columns(7)
            for col, dia in zip(cols, semana):
                if dia == 0:
                    col.markdown("")
                else:
                    data_dia = datetime(ano_selecionado, mes_selecionado, dia).date()
                    
                    if data_dia in agendamentos:
                        pedidos_dia = agendamentos[data_dia]
                        has_prioridade = any(p['status_class'] == 'prioridade' for p in pedidos_dia)
                        has_atencao = any(p['status_class'] == 'atencao' for p in pedidos_dia)
                        
                        if has_prioridade:
                            border_color = "#f44336"
                            bg_color = "#f8d7da"
                        elif has_atencao:
                            border_color = "#ff9800"
                            bg_color = "#fff3cd"
                        else:
                            border_color = "#4caf50"
                            bg_color = "#d4edda"
                        
                        with col:
                            # Botão para ver tabela da data
                            btn_key = f"date_table_{data_dia}"
                            if st.button(f"📌 {dia}\n({len(pedidos_dia)})", key=btn_key, use_container_width=True):
                                st.session_state.selected_calendar_date = data_dia
                                st.rerun()
                            
                            # Expander com resumo
                            with st.expander(f"Ver {len(pedidos_dia)} pedido(s)", expanded=False):
                                for pedido in pedidos_dia[:5]:
                                    st.markdown(f"""
                                        <div style="margin-bottom: 8px; padding: 6px; border-left: 3px solid {border_color}; background-color: #f5f5f5; font-size: 12px;">
                                            <b>Pedido #{pedido['pedido']}</b><br>
                                            {pedido['cliente'][:30]}<br>
                                            <span class="status-badge {pedido['status_class']}" style="font-size: 10px;">{pedido['status']}</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                if len(pedidos_dia) > 5:
                                    st.caption(f"... e mais {len(pedidos_dia) - 5} pedido(s)")
                    else:
                        col.markdown(f"<div style='text-align: center; padding: 10px; color: #ccc;'>{dia}</div>", unsafe_allow_html=True)
    
    # Tabela de detalhes da data selecionada
    if st.session_state.selected_calendar_date:
        data_selecionada = st.session_state.selected_calendar_date
        df_data = df_filtered_clean[df_filtered_clean['Data'] == data_selecionada].copy()
        
        if not df_data.empty:
            st.markdown("---")
            show_detail_table(
                df_data,
                title=f"📋 Detalhamento - Data: {data_selecionada.strftime('%d/%m/%Y')}",
                filter_info=f"Mostrando {len(df_data)} pedido(s) agendados para {data_selecionada.strftime('%d/%m/%Y')}"
            )
            
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("🔒 Fechar Tabela", key="close_calendar_table"):
                    st.session_state.selected_calendar_date = None
                    st.rerun()

# ==================== FUNÇÃO PRINCIPAL ====================
def main():
    # Cabeçalho
    st.markdown("""
        <div class="main-header">
            <h1>🏭 Sistema de Gestão de Confecção</h1>
            <p>Gerencie seus pedidos, agendamentos e estoque de forma inteligente</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Menu Principal")
        st.markdown("---")
        
        modulo = st.radio(
            "Selecione o módulo:",
            ["📋 Filtro de Confecção", "📅 Agendamento de Pedidos", "📊 Dashboard"],
            index=0
        )
        
        st.markdown("---")
        
        with st.expander("ℹ️ Sobre o Sistema"):
            st.markdown("""
                **Versão:** 5.1  
                **Desenvolvido para:** Gestão de Confecção  
                
                ### Funcionalidades:
                - ✅ Filtro avançado por código de confecção
                - ✅ Upload de lista em Excel para filtro
                - ✅ Agrupamento em abas por confecção
                - ✅ Ocultação automática (Qtd Ret > 95% da Qtd)
                - ✅ Cards com status do cliente
                - ✅ Calendário interativo
                - ✅ 3 abas organizadas
            """)
        
        st.markdown("---")
        st.markdown("### 📊 Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🟢 **Online**")
        with col2:
            st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    
    # Conteúdo
    if modulo == "📋 Filtro de Confecção":
        render_confeccao()
    elif modulo == "📅 Agendamento de Pedidos":
        render_agendamento()
    else:
        render_dashboard()

def render_confeccao():
    """Renderiza o módulo de filtro de confecção com filtro avançado e agrupamento em abas"""
    st.markdown("## 📋 Filtro de Dados de Confecção")
    st.markdown("Faça o upload do seu banco de dados em Excel para começar.")
    
    uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx", "xls"], key="confeccao_file")
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            
            st.success(f"✅ Arquivo carregado! {len(df)} registros encontrados.")
            
            # Colunas esperadas
            expected_columns = ['Compra', 'Cód Confec', 'Confeccionado', 'Qtd', 'Qtd Ret', 'Saldo', 'Confecção']
            available_cols = [col for col in expected_columns if col in df.columns]
            missing_cols = [col for col in expected_columns if col not in df.columns]
            
            if missing_cols:
                st.warning(f"⚠️ Colunas não encontradas: {', '.join(missing_cols)}")
            
            if not available_cols:
                st.error("Nenhuma coluna esperada encontrada no arquivo.")
                st.write("Colunas encontradas:", list(df.columns))
                return
            
            df_filtered = df[available_cols].copy()
            
            # Aplicar regra de Qtd Ret (ocultar linhas com Qtd Ret > 95% da Qtd)
            linhas_removidas = 0
            if 'Qtd' in df_filtered.columns and 'Qtd Ret' in df_filtered.columns:
                df_filtered, linhas_removidas = filter_by_qtd_ret_percent(df_filtered, 'Qtd', 'Qtd Ret', 95)
                if linhas_removidas > 0:
                    st.info(f"ℹ️ {linhas_removidas} linha(s) removida(s) por terem Qtd Ret ≥ 95% da Qtd.")
            
            # ==================== SIDEBAR FILTERS ====================
            st.sidebar.markdown("## 🔍 Filtros da Confecção")
            
            # Filtro 1: Por Confecção
            if 'Confecção' in df_filtered.columns:
                df_filtered['Confecção'] = df_filtered['Confecção'].fillna("Vazio").astype(str)
                confeccoes = sorted(df_filtered['Confecção'].unique())
                confeccoes_selecionadas = st.sidebar.multiselect(
                    "Filtrar por Confecção:", 
                    options=confeccoes, 
                    default=confeccoes
                )
                if confeccoes_selecionadas:
                    df_filtered = df_filtered[df_filtered['Confecção'].isin(confeccoes_selecionadas)]
            
            # Filtro 2: Contém no nome 'Confeccionado'
            if 'Confeccionado' in df_filtered.columns:
                termo_busca = st.sidebar.text_input("Contém no nome do produto:", value="")
                if termo_busca:
                    df_filtered['Confeccionado'] = df_filtered['Confeccionado'].fillna("").astype(str)
                    df_filtered = df_filtered[df_filtered['Confeccionado'].str.contains(termo_busca, case=False, na=False)]
            
            # Filtro 3: Filtro Avançado por Cód Confec (upload de lista em Excel)
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🎯 Filtro Avançado por Código")
            
            if 'Cód Confec' in df_filtered.columns:
                # Converter códigos para string padronizada
                df_filtered['Cód Confec'] = df_filtered['Cód Confec'].fillna("").astype(str)
                df_filtered['Cód Confec'] = df_filtered['Cód Confec'].str.replace(r'\.0$', '', regex=True).str.strip()
                
                # Lista de todos os códigos disponíveis
                todos_cods = sorted([c for c in df_filtered['Cód Confec'].unique() if c and c != ''])
                
                # Upload de arquivo com lista de códigos
                arquivo_cods = st.sidebar.file_uploader(
                    "Upload Excel com lista de códigos", 
                    type=["xlsx", "xls"], 
                    key="upload_cods_confeccao",
                    help="Arquivo deve conter uma coluna 'Cód Confec' ou usar a primeira coluna"
                )
                
                codigos_do_arquivo = []
                if arquivo_cods is not None:
                    try:
                        df_cods = pd.read_excel(arquivo_cods)
                        df_cods.columns = df_cods.columns.str.strip()
                        
                        # Procurar coluna 'Cód Confec' ou usar primeira coluna
                        if 'Cód Confec' in df_cods.columns:
                            serie_cods = df_cods['Cód Confec']
                        else:
                            serie_cods = df_cods.iloc[:, 0]
                        
                        # Converter para string e limpar
                        serie_cods = serie_cods.fillna("").astype(str)
                        serie_cods = serie_cods.str.replace(r'\.0$', '', regex=True).str.strip()
                        codigos_do_arquivo = [c for c in serie_cods.tolist() if c and c.lower() != 'nan']
                        
                        # Filtrar apenas códigos que existem no banco
                        codigos_validos = [c for c in codigos_do_arquivo if c in todos_cods]
                        
                        if codigos_validos:
                            st.sidebar.success(f"✅ {len(codigos_validos)} código(s) válido(s) encontrado(s)")
                            codigos_do_arquivo = codigos_validos
                        else:
                            st.sidebar.warning("⚠️ Nenhum código correspondente encontrado")
                            codigos_do_arquivo = []
                            
                    except Exception as e:
                        st.sidebar.error(f"Erro ao ler arquivo: {e}")
                        codigos_do_arquivo = []
                
                # Validar valores padrão antes de passar para o multiselect
                default_cods = validate_default_options(todos_cods, codigos_do_arquivo)
                
                # Multiselect para selecionar códigos
                selecionados_cods = st.sidebar.multiselect(
                    "Códigos do Produto:", 
                    options=todos_cods, 
                    default=default_cods
                )
                
                if selecionados_cods:
                    df_filtered = df_filtered[df_filtered['Cód Confec'].isin(selecionados_cods)]
                    st.sidebar.info(f"📊 {len(selecionados_cods)} código(s) selecionado(s)")
            
            # Métricas
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            # Processamento numérico para métricas
            cols_numericas = [col for col in ['Qtd', 'Qtd Ret', 'Saldo'] if col in df_filtered.columns]
            for col in cols_numericas:
                df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0)
            
            col1.metric("Total de Registros", len(df_filtered))
            if 'Qtd' in cols_numericas:
                col2.metric("Soma de Qtd", f"{df_filtered['Qtd'].sum():.0f}")
            if 'Qtd Ret' in cols_numericas:
                col3.metric("Soma de Qtd Ret", f"{df_filtered['Qtd Ret'].sum():.0f}")
            if 'Saldo' in cols_numericas:
                col4.metric("Soma de Saldo", f"{df_filtered['Saldo'].sum():.0f}")
            
            st.markdown("---")
            
            # ==================== EXIBIÇÃO COM ABAS POR CONFECÇÃO ====================
            if 'Confecção' in df_filtered.columns:
                df_filtered['Confecção'] = df_filtered['Confecção'].astype(str)
                confeccoes_unicas = [c for c in df_filtered['Confecção'].dropna().unique().tolist() if c and c != 'nan' and c != '']
                confeccoes_unicas.sort()
                
                # Criar abas: Visão Geral + cada confecção
                nomes_abas = ["📋 Visão Geral", "📊 Resumo Agrupado"] + [f"🏭 {conf[:30]}" for conf in confeccoes_unicas]
                abas = st.tabs(nomes_abas)
                
                # ABA 0: Visão Geral - Tabela completa
                with abas[0]:
                    st.markdown("### 📋 Tabela Completa")
                    st.markdown(f"Mostrando {len(df_filtered)} registros após aplicação dos filtros")
                    
                    # Preparar colunas para exibição
                    display_cols = [col for col in ['Compra', 'Cód Confec', 'Confeccionado', 'Qtd', 'Qtd Ret', 'Saldo', 'Confecção'] if col in df_filtered.columns]
                    if display_cols:
                        st.dataframe(df_filtered[display_cols], use_container_width=True, hide_index=True)
                
                # ABA 1: Resumo Agrupado
                with abas[1]:
                    st.markdown("### 📊 Resumo por Confecção")
                    
                    if cols_numericas:
                        # Agrupar por confecção
                        df_agrupado = df_filtered.groupby('Confecção')[cols_numericas].sum().reset_index()
                        
                        # Ordenar por quantidade total
                        if 'Qtd' in df_agrupado.columns:
                            df_agrupado = df_agrupado.sort_values('Qtd', ascending=False)
                        
                        st.dataframe(df_agrupado, use_container_width=True, hide_index=True)
                        
                        # Gráfico de barras simples
                        st.markdown("#### 📊 Distribuição por Confecção")
                        if 'Qtd' in df_agrupado.columns:
                            chart_data = df_agrupado.set_index('Confecção')[['Qtd']]
                            st.bar_chart(chart_data)
                    else:
                        st.info("Não há colunas numéricas para realizar o agrupamento.")
                
                # ABAS para cada confecção
                for i, conf in enumerate(confeccoes_unicas):
                    with abas[i+2]:
                        df_aba = df_filtered[df_filtered['Confecção'] == conf]
                        
                        # Métricas da confecção
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de Registros", len(df_aba))
                        if 'Qtd' in df_aba.columns:
                            with col2:
                                st.metric("Soma de Qtd", f"{df_aba['Qtd'].sum():.0f}")
                        if 'Saldo' in df_aba.columns:
                            with col3:
                                st.metric("Soma de Saldo", f"{df_aba['Saldo'].sum():.0f}")
                        
                        st.markdown("---")
                        
                        # Tabela da confecção
                        display_cols = [col for col in ['Compra', 'Cód Confec', 'Confeccionado', 'Qtd', 'Qtd Ret', 'Saldo'] if col in df_aba.columns]
                        if display_cols:
                            st.dataframe(df_aba[display_cols], use_container_width=True, hide_index=True)
            else:
                # Se não tem coluna Confecção, mostra apenas a tabela
                st.dataframe(df_filtered, use_container_width=True, hide_index=True)
            
            # ==================== EXPORTAÇÃO ====================
            st.markdown("---")
            st.subheader("📥 Exportar Relatórios")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Exportar dados filtrados
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_filtered.to_excel(writer, sheet_name='Filtrado', index=False)
                    
                    # Adicionar aba de resumo
                    if 'Confecção' in df_filtered.columns and cols_numericas:
                        df_agrupado = df_filtered.groupby('Confecção')[cols_numericas].sum().reset_index()
                        df_agrupado.to_excel(writer, sheet_name='Resumo_Confecções', index=False)
                
                st.download_button(
                    label="⬇️ Baixar Excel",
                    data=buffer.getvalue(),
                    file_name=f"relatorio_confeccao_{datetime.now().strftime('%d_%m_%Y_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                # Exportar CSV
                csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Baixar CSV",
                    data=csv,
                    file_name=f"relatorio_confeccao_{datetime.now().strftime('%d_%m_%Y_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
            st.exception(e)
    else:
        st.info("👆 Faça o upload de um arquivo Excel para começar.")
        with st.expander("📝 Ver formato esperado"):
            st.markdown("""
                ### Colunas esperadas:
                - **Compra** - Número da compra
                - **Cód Confec** - Código do produto confeccionado
                - **Confeccionado** - Nome do produto
                - **Qtd** - Quantidade total
                - **Qtd Ret** - Quantidade retornada
                - **Saldo** - Saldo atual
                - **Confecção** - Nome da confecção (para agrupamento)
                
                ### Regras aplicadas:
                - 🚫 Linhas com **Qtd Ret ≥ 95% da Qtd** são automaticamente ocultadas
                - 📁 Dados são agrupados em abas por confecção
                - 🎯 Filtro avançado permite upload de lista de códigos em Excel
            """)

def render_agendamento():
    """Renderiza o módulo de agendamento de pedidos com abas organizadas"""
    st.markdown("## 📅 Agendamento de Pedidos")
    
    uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=['xlsx', 'xls'], key="agendamento_file")
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            
            st.success(f"✅ Arquivo carregado! {len(df)} registros encontrados.")
            
            if 'Dt. Agendamento' in df.columns:
                df['Dt. Agendamento'] = pd.to_datetime(df['Dt. Agendamento'], errors='coerce')
            
            # Sidebar filters
            st.sidebar.markdown("## 🔍 Filtros")
            
            df_filtered = df.copy()
            
            # Filtros básicos
            if 'Operação Produtiva' in df.columns:
                ops = st.sidebar.multiselect("Operação", options=df['Operação Produtiva'].unique())
                if ops:
                    df_filtered = df_filtered[df_filtered['Operação Produtiva'].isin(ops)]
            
            if 'Segmento' in df.columns:
                segs = st.sidebar.multiselect("Segmento", options=df['Segmento'].unique())
                if segs:
                    df_filtered = df_filtered[df_filtered['Segmento'].isin(segs)]
            
            if 'Coleção' in df.columns:
                cols_filter = st.sidebar.multiselect("Coleção", options=df['Coleção'].unique())
                if cols_filter:
                    df_filtered = df_filtered[df_filtered['Coleção'].isin(cols_filter)]
            
            if 'Cliente' in df.columns:
                clients = st.sidebar.multiselect("Cliente", options=df['Cliente'].unique())
                if clients:
                    df_filtered = df_filtered[df_filtered['Cliente'].isin(clients)]
            
            # Adicionar status
            if all(col in df_filtered.columns for col in ['Qtd', 'Saldo Atual', 'Saldo Calc.']):
                df_filtered['Status'] = df_filtered.apply(
                    lambda row: get_status(row['Qtd'], row['Saldo Atual'], row['Saldo Calc.'])[0],
                    axis=1
                )
            
            # Filtro por status do cliente
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🎯 Filtro por Status do Cliente")
            client_status_filter = st.sidebar.selectbox(
                "Status do Cliente",
                options=["Todos", "PRIORIDADE", "ATENÇÃO", "OK"],
                index=0
            )
            
            # Métricas
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Pedidos", len(df_filtered))
            if 'Status' in df_filtered.columns:
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
            
            # ==================== ABAS ORGANIZADAS ====================
            if not df_filtered.empty:
                status_map = {"Todos": None, "PRIORIDADE": "PRIORIDADE", "ATENÇÃO": "ATENÇÃO", "OK": "OK"}
                
                # Criar abas principais
                tab1, tab2, tab3 = st.tabs([
                    "🎯 Cards por Cliente", 
                    "📅 Visualização em Calendário", 
                    "📋 Tabela Geral Completa"
                ])
                
                # ABA 1: Cards por Cliente
                with tab1:
                    st.markdown("### 🎯 Visualização por Cliente")
                    st.markdown("Cards organizados por cliente com status e detalhamento")
                    st.markdown("💡 **Dica:** Clique em 'Ver Tabela' para ver todos os pedidos do cliente em formato de tabela")
                    create_enhanced_client_cards(df_filtered, status_map[client_status_filter])
                
                # ABA 2: Calendário
                with tab2:
                    st.markdown("### 📅 Visualização em Calendário")
                    st.markdown("Pedidos organizados por data de agendamento")
                    st.markdown("💡 **Dica:** Clique no botão da data para ver todos os pedidos daquela data em formato de tabela")
                    create_calendar_view(df_filtered)
                
                # ABA 3: Tabela Geral
                with tab3:
                    st.markdown("### 📋 Tabela Geral Completa")
                    st.markdown("Visualização tabular de todos os pedidos com filtros aplicados")
                    
                    # Sub-abas para diferentes visualizações da tabela
                    sub_tab1, sub_tab2 = st.tabs(["📊 Visualização Completa", "📥 Exportar Dados"])
                    
                    with sub_tab1:
                        show_detail_table(df_filtered, title="📋 Todos os Pedidos", filter_info=f"Total de {len(df_filtered)} pedidos encontrados")
                    
                    with sub_tab2:
                        st.markdown("#### Opções de Exportação")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Exportar CSV
                            csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                "📥 Baixar CSV", 
                                data=csv, 
                                file_name=f"pedidos_{datetime.now().strftime('%d_%m_%Y_%H%M')}.csv", 
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Exportar Excel
                            buffer = io.BytesIO()
                            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                df_filtered.to_excel(writer, sheet_name='Pedidos', index=False)
                                
                                # Adicionar aba de resumo se tiver status
                                if 'Status' in df_filtered.columns:
                                    resumo = df_filtered.groupby('Status').size().reset_index(name='Quantidade')
                                    resumo.to_excel(writer, sheet_name='Resumo_Status', index=False)
                                
                                # Adicionar aba de clientes se tiver cliente
                                if 'Cliente' in df_filtered.columns:
                                    clientes_resumo = df_filtered.groupby('Cliente').size().reset_index(name='Total_Pedidos')
                                    clientes_resumo = clientes_resumo.sort_values('Total_Pedidos', ascending=False)
                                    clientes_resumo.to_excel(writer, sheet_name='Resumo_Clientes', index=False)
                            
                            st.download_button(
                                "📥 Baixar Excel", 
                                data=buffer.getvalue(), 
                                file_name=f"pedidos_{datetime.now().strftime('%d_%m_%Y_%H%M')}.xlsx", 
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        
                        st.markdown("---")
                        st.markdown("#### 📊 Estatísticas Rápidas")
                        
                        # Estatísticas adicionais
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de Pedidos", len(df_filtered))
                        with col2:
                            if 'Cliente' in df_filtered.columns:
                                st.metric("Total de Clientes", df_filtered['Cliente'].nunique())
                        with col3:
                            if 'Qtd' in df_filtered.columns:
                                st.metric("Quantidade Total", f"{df_filtered['Qtd'].sum():,.0f}")
            else:
                st.warning("Nenhum pedido encontrado com os filtros selecionados.")
            
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
            st.exception(e)
    else:
        st.info("👆 Faça o upload de um arquivo Excel para começar.")
        with st.expander("📝 Ver formato esperado"):
            st.markdown("""
                ### Colunas necessárias:
                - **Pedido** - ID do pedido
                - **Cliente** - Nome do cliente
                - **Produto** - Nome do produto
                - **Qtd** - Quantidade
                - **Saldo Atual** - Estoque atual
                - **Saldo Calc.** - Estoque calculado
                - **Dt. Agendamento** - Data (opcional)
                
                ### Funcionalidades por Aba:
                
                **🎯 Cards por Cliente**
                - Visualização por cliente com status
                - Cards expansíveis com detalhes
                - Botão "Ver Tabela" para detalhamento completo
                
                **📅 Visualização em Calendário**
                - Calendário interativo
                - Botão na data para ver tabela detalhada
                - Cores indicativas por prioridade
                
                **📋 Tabela Geral Completa**
                - Tabela completa com todos os dados
                - Exportação para CSV e Excel
                - Resumos automáticos por status e cliente
            """)

def render_dashboard():
    """Renderiza dashboard"""
    st.markdown("## 📊 Dashboard de Gestão")
    st.markdown("Visão geral do sistema de gestão de confecção")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📋 Módulo 1</div>
                <div class="metric-label">Filtro de Confecção</div>
            </div>
            <br>
            <div style="padding: 10px;">
                <b>Funcionalidades:</b><br>
                ✅ Upload de arquivos Excel<br>
                ✅ Filtro avançado por código<br>
                ✅ Upload de lista em Excel<br>
                ✅ Agrupamento em abas por confecção<br>
                ✅ Ocultação automática (Qtd Ret > 95%)<br>
                ✅ Exportação de relatórios
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📅 Módulo 2</div>
                <div class="metric-label">Agendamento de Pedidos</div>
            </div>
            <br>
            <div style="padding: 10px;">
                <b>Funcionalidades:</b><br>
                ✅ Cards por cliente com status<br>
                ✅ Tabela detalhada por cliente<br>
                ✅ Calendário com tabela por data<br>
                ✅ 3 abas organizadas<br>
                ✅ Exportação CSV/Excel
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">⚡ Diferenciais</div>
                <div class="metric-label">Funcionalidades</div>
            </div>
            <br>
            <div style="padding: 10px;">
                <b>Destaques:</b><br>
                ✅ Filtro dinâmico por cliente<br>
                ✅ Filtro dinâmico por data<br>
                ✅ Organização por abas<br>
                ✅ Interface responsiva<br>
                ✅ Regras automáticas de negócio
            </div>
        """, unsafe_allow_html=True)

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    main()
