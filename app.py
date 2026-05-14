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
        .order-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background-color: #f9f9f9;
            transition: all 0.2s ease;
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
def safe_str(value):
    """Converte qualquer valor para string de forma segura"""
    if pd.isna(value):
        return ""
    if isinstance(value, (np.int64, np.int32, np.float64, np.float32)):
        return str(int(value)) if value == int(value) else str(value)
    return str(value)

def safe_join(values, separator=' / ', max_items=3):
    """Junta valores de forma segura, convertendo todos para string"""
    if values is None or len(values) == 0:
        return 'N/A'
    str_values = [safe_str(v) for v in list(values)[:max_items] if safe_str(v)]
    return separator.join(str_values) if str_values else 'N/A'

def safe_hash(*args):
    """Gera hash seguro a partir de múltiplos argumentos"""
    str_args = [safe_str(arg) for arg in args]
    combined = "_".join(str_args)
    return combined.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("|", "_").replace(":", "_")

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

# ==================== FUNÇÃO DE CARDS CORRIGIDA ====================
def create_enhanced_client_cards(df_filtered):
    """Cria cards de clientes com menu interativo para detalhamento de pedidos"""
    
    if 'Cliente' not in df_filtered.columns:
        st.warning("Coluna 'Cliente' não encontrada no arquivo.")
        return
    
    # Converter Cliente para string
    df_filtered = df_filtered.copy()
    df_filtered['Cliente_str'] = df_filtered['Cliente'].fillna("Desconhecido").astype(str)
    clients = sorted(df_filtered['Cliente_str'].unique(), key=str)
    
    # Inicializar estados
    if 'expanded_clients' not in st.session_state:
        st.session_state.expanded_clients = {}
    if 'expanded_orders' not in st.session_state:
        st.session_state.expanded_orders = {}
    
    # Para cada cliente
    for client in clients:
        df_client = df_filtered[df_filtered['Cliente_str'] == client].copy()
        
        # Verificar se tem a coluna Pedido
        if 'Pedido' in df_client.columns:
            # Converter Pedido para string
            df_client['Pedido_str'] = df_client['Pedido'].apply(safe_str)
            
            # Agrupar por pedido com funções seguras
            try:
                pedidos_agrupados = df_client.groupby('Pedido_str', as_index=False).agg({
                    'Produto': lambda x: safe_join(x.unique(), ' / ', 3),
                    'Qtd': 'first',
                    'Saldo Atual': 'first',
                    'Saldo Calc.': 'first',
                    'R$ Total Calc.': 'first',
                    'Cód Prod': lambda x: safe_join(x.unique(), ' / ', 3),
                    'Operação Produtiva': 'first',
                    'Segmento': 'first',
                    'Coleção': 'first',
                    'Dt. Agendamento': 'first',
                    'Status': 'first'
                })
                pedidos_agrupados.rename(columns={'Pedido_str': 'Pedido'}, inplace=True)
                
                # Adicionar contagem de itens
                itens_por_pedido = df_client.groupby('Pedido_str').size()
                pedidos_agrupados['Qtd_Itens'] = pedidos_agrupados['Pedido'].map(itens_por_pedido)
                
            except Exception as e:
                st.error(f"Erro ao agrupar pedidos para o cliente {client}: {e}")
                continue
        else:
            pedidos_agrupados = df_client.copy()
            pedidos_agrupados['Pedido'] = 'N/A'
            pedidos_agrupados['Qtd_Itens'] = 1
        
        # Calcular estatísticas
        total_pedidos = len(pedidos_agrupados)
        total_prioridade = len(pedidos_agrupados[pedidos_agrupados['Status'] == 'PRIORIDADE']) if 'Status' in pedidos_agrupados.columns else 0
        total_atencao = len(pedidos_agrupados[pedidos_agrupados['Status'] == 'ATENÇÃO']) if 'Status' in pedidos_agrupados.columns else 0
        total_ok = len(pedidos_agrupados[pedidos_agrupados['Status'] == 'OK']) if 'Status' in pedidos_agrupados.columns else 0
        
        # Status do cliente
        if total_prioridade > 0:
            status_text = f"🔴 {total_prioridade} Prioridade(s)"
        elif total_atencao > 0:
            status_text = f"🟠 {total_atencao} Atenção(ões)"
        else:
            status_text = f"🟢 {total_ok} OK"
        
        # Estado do card
        client_key = safe_hash("client", client)
        is_client_expanded = st.session_state.expanded_clients.get(client_key, False)
        
        # Card do cliente
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"### 👤 {client}")
            
            with col2:
                st.markdown(f"""
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <span style="background: #f0f0f0; padding: 5px 10px; border-radius: 8px;">📦 {total_pedidos} pedido(s)</span>
                        <span style="background: #f0f0f0; padding: 5px 10px; border-radius: 8px;">{status_text}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                button_label = "🔽 Detalhes" if not is_client_expanded else "🔼 Fechar"
                if st.button(button_label, key=f"btn_{client_key}", use_container_width=True):
                    st.session_state.expanded_clients[client_key] = not is_client_expanded
                    st.rerun()
            
            st.markdown("---")
            
            # Conteúdo expandido
            if is_client_expanded:
                if len(pedidos_agrupados) == 0:
                    st.info("Nenhum pedido encontrado para este cliente.")
                else:
                    cols = st.columns(2)
                    
                    for idx, (_, row) in enumerate(pedidos_agrupados.iterrows()):
                        col_idx = idx % 2
                        
                        with cols[col_idx]:
                            pedido_id = safe_str(row.get('Pedido', 'N/A'))
                            produto = row.get('Produto', 'N/A')
                            
                            # Converter valores numéricos
                            try:
                                qtd = float(row.get('Qtd', 0)) if pd.notna(row.get('Qtd')) else 0
                                saldo_atual = float(row.get('Saldo Atual', 0)) if pd.notna(row.get('Saldo Atual')) else 0
                                saldo_calc = float(row.get('Saldo Calc.', 0)) if pd.notna(row.get('Saldo Calc.')) else 0
                            except:
                                qtd = 0
                                saldo_atual = 0
                                saldo_calc = 0
                            
                            qtd_itens = row.get('Qtd_Itens', 1)
                            if pd.isna(qtd_itens):
                                qtd_itens = 1
                            
                            status_text_pedido, status_class = get_status(qtd, saldo_atual, saldo_calc)
                            
                            # Formatar data
                            data_str = "N/A"
                            if 'Dt. Agendamento' in row and pd.notna(row['Dt. Agendamento']):
                                try:
                                    if hasattr(row['Dt. Agendamento'], 'strftime'):
                                        data_str = row['Dt. Agendamento'].strftime('%d/%m/%Y')
                                    else:
                                        data_str = str(row['Dt. Agendamento'])
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
                            
                            # Estado do pedido
                            order_key = safe_hash("order", client, pedido_id)
                            is_order_expanded = st.session_state.expanded_orders.get(order_key, False)
                            status_class_lower = status_class.lower()
                            
                            # Card do pedido
                            st.markdown(f"""
                                <div class="order-card {status_class_lower}">
                                    <div class="order-header">
                                        <div>
                                            <span class="order-number">Pedido #{pedido_id}</span>
                                            <div style="font-size: 12px; color: #666; margin-top: 4px;">
                                                {safe_str(produto)[:100]}{'...' if len(safe_str(produto)) > 100 else ''}
                                            </div>
                                            <div style="font-size: 11px; color: #999; margin-top: 2px;">
                                                📦 {qtd_itens} item(ns) no pedido
                                            </div>
                                        </div>
                                        <div>
                                            <span class="order-status status-{status_class_lower}">{status_text_pedido}</span>
                                        </div>
                                    </div>
                            """, unsafe_allow_html=True)
                            
                            btn_key = safe_hash("detail", order_key)
                            if st.button(f"📋 Ver Detalhes Completos", key=btn_key, use_container_width=True):
                                st.session_state.expanded_orders[order_key] = not is_order_expanded
                                st.rerun()
                            
                            if is_order_expanded:
                                cod_prod = row.get('Cód Prod', 'N/A')
                                if pd.isna(cod_prod):
                                    cod_prod = 'N/A'
                                
                                st.markdown(f"""
                                    <div class="order-details">
                                        <div class="detail-grid">
                                            <div class="detail-item">
                                                <div class="detail-label">📦 Produto(s)</div>
                                                <div class="detail-value">{safe_str(produto)}</div>
                                            </div>
                                            <div class="detail-item">
                                                <div class="detail-label">🔢 Código(s)</div>
                                                <div class="detail-value">{safe_str(cod_prod)}</div>
                                            </div>
                                            <div class="detail-item">
                                                <div class="detail-label">📅 Data Agendamento</div>
                                                <div class="detail-value">{data_str}</div>
                                            </div>
                                            <div class="detail-item">
                                                <div class="detail-label">🏭 Operação</div>
                                                <div class="detail-value">{safe_str(row.get('Operação Produtiva', 'N/A'))}</div>
                                            </div>
                                            <div class="detail-item">
                                                <div class="detail-label">📊 Segmento</div>
                                                <div class="detail-value">{safe_str(row.get('Segmento', 'N/A'))}</div>
                                            </div>
                                            <div class="detail-item">
                                                <div class="detail-label">🎨 Coleção</div>
                                                <div class="detail-value">{safe_str(row.get('Coleção', 'N/A'))}</div>
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
                
                # Rodapé do cliente
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 12px; border-radius: 8px; margin-top: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <span><strong>📊 Resumo do Cliente</strong></span>
                            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                                <span>📦 Total: {total_pedidos} pedido(s)</span>
                                <span>🔴 Prioridade: {total_prioridade}</span>
                                <span>🟠 Atenção: {total_atencao}</span>
                                <span>🟢 OK: {total_ok}</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
            else:
                # Resumo compacto
                if total_pedidos > 0:
                    st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 10px 0;">
                            <div style="display: flex; gap: 20px; font-size: 14px; flex-wrap: wrap;">
                                <span>📦 Total: {total_pedidos} pedido(s)</span>
                                <span>🔴 Prioridade: {total_prioridade}</span>
                                <span>🟠 Atenção: {total_atencao}</span>
                                <span>🟢 OK: {total_ok}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# ==================== FUNÇÃO DE CALENDÁRIO ====================
def create_calendar_view(df_filtered):
    """Cria visualização de calendário com pedidos agrupados por data"""
    
    if 'Dt. Agendamento' not in df_filtered.columns:
        st.warning("Coluna 'Dt. Agendamento' não encontrada no arquivo.")
        return
    
    df_filtered_clean = df_filtered.dropna(subset=['Dt. Agendamento'])
    
    if df_filtered_clean.empty:
        st.warning("Nenhum pedido com data de agendamento disponível.")
        return
    
    agendamentos = defaultdict(list)
    
    for _, row in df_filtered_clean.iterrows():
        try:
            data = row['Dt. Agendamento'].date()
        except:
            continue
            
        qtd = row.get('Qtd', 0)
        saldo_atual = row.get('Saldo Atual', 0)
        saldo_calc = row.get('Saldo Calc.', 0)
        status_text, _ = get_status(qtd, saldo_atual, saldo_calc)
        
        agendamentos[data].append({
            'pedido': safe_str(row.get('Pedido', 'N/A')),
            'produto': safe_str(row.get('Produto', 'N/A'))[:50],
            'cliente': safe_str(row.get('Cliente', 'N/A')),
            'qtd': qtd,
            'status': status_text
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
                        with col:
                            with st.expander(f"📌 **{dia}** ({len(pedidos_dia)} pedido(s))", expanded=False):
                                for pedido in pedidos_dia:
                                    st.markdown(f"""
                                        <div style="margin-bottom: 10px; padding: 8px; border-left: 3px solid #ddd; background-color: #f5f5f5;">
                                            <b>Pedido #{pedido['pedido']}</b><br>
                                            <b>Cliente:</b> {pedido['cliente']}<br>
                                            <b>Produto:</b> {pedido['produto']}<br>
                                            <b>Status:</b> {pedido['status']}
                                        </div>
                                    """, unsafe_allow_html=True)
                    else:
                        col.markdown(f"<div style='text-align: center; padding: 10px; color: #ccc;'>{dia}</div>", unsafe_allow_html=True)

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
            index=1  # Mudar para Agendamento como padrão para teste
        )
        
        st.markdown("---")
        
        with st.expander("ℹ️ Sobre o Sistema"):
            st.markdown("""
                **Versão:** 3.3  
                **Desenvolvido para:** Gestão de Confecção  
                
                ### Funcionalidades:
                - ✅ Filtro avançado de dados
                - ✅ Agendamento de pedidos
                - ✅ Cards interativos por cliente
                - ✅ Detalhamento expansível
                - ✅ Priorização automática
            """)
        
        st.markdown("---")
        st.markdown("### 📊 Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🟢 **Online**")
        with col2:
            st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    
    # Conteúdo baseado no módulo
    if modulo == "📋 Filtro de Confecção":
        render_Confecção()
    elif modulo == "📅 Agendamento de Pedidos":
        render_agendamento()
    else:
        render_dashboard()

def render_Confecção():
    """Renderiza o módulo de filtro de confecção"""
    st.markdown("## 📋 Filtro de Dados de Confecção")
    st.markdown("Faça o upload do seu banco de dados em Excel para começar.")
    
    uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx", "xls"], key="Confecção_file")
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            
            expected_columns = ['Compra', 'Cód Confec', 'Confeccionado', 'Qtd', 'Qtd Ret', 'Saldo', 'Confecção']
            available_cols = [col for col in expected_columns if col in df.columns]
            
            if not available_cols:
                st.error("Nenhuma coluna esperada encontrada no arquivo.")
                st.write("Colunas encontradas:", list(df.columns))
                return
            
            df_filtered = df[available_cols].copy()
            
            # Filtros
            st.sidebar.markdown("## 🔍 Filtros")
            
            if 'Confecção' in df_filtered.columns:
                df_filtered['Confecção'] = df_filtered['Confecção'].fillna("Vazio").astype(str)
                confeccoes = sorted(df_filtered['Confecção'].unique())
                selecionadas = st.sidebar.multiselect("Confecção:", options=confeccoes, default=confeccoes)
                if selecionadas:
                    df_filtered = df_filtered[df_filtered['Confecção'].isin(selecionadas)]
            
            # Processamento numérico
            cols_numericas = [col for col in ['Qtd', 'Qtd Ret', 'Saldo'] if col in df_filtered.columns]
            for col in cols_numericas:
                df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0)
            
            # Métricas
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Registros", len(df_filtered))
            if 'Qtd' in cols_numericas:
                col2.metric("Soma de Qtd", f"{df_filtered['Qtd'].sum():.0f}")
            if 'Qtd Ret' in cols_numericas:
                col3.metric("Soma de Qtd Ret", f"{df_filtered['Qtd Ret'].sum():.0f}")
            if 'Saldo' in cols_numericas:
                col4.metric("Soma de Saldo", f"{df_filtered['Saldo'].sum():.0f}")
            
            # Exibição
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)
            
            # Exportação
            st.markdown("---")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, sheet_name='Filtrado', index=False)
            
            st.download_button(
                label="⬇️ Baixar Excel",
                data=buffer.getvalue(),
                file_name="relatorio_Confecção.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Erro: {e}")
            st.exception(e)
    else:
        st.info("👆 Faça o upload de um arquivo Excel para começar.")

def render_agendamento():
    """Renderiza o módulo de agendamento de pedidos"""
    st.markdown("## 📅 Agendamento de Pedidos")
    
    uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=['xlsx', 'xls'], key="agendamento_file")
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            
            st.success(f"Arquivo carregado com sucesso! {len(df)} registros encontrados.")
            
            if 'Dt. Agendamento' in df.columns:
                df['Dt. Agendamento'] = pd.to_datetime(df['Dt. Agendamento'], errors='coerce')
            
            # Sidebar filters
            st.sidebar.markdown("## 🔍 Filtros")
            
            df_filtered = df.copy()
            
            if 'Operação Produtiva' in df.columns:
                ops = st.sidebar.multiselect("Operação", options=df['Operação Produtiva'].unique())
                if ops:
                    df_filtered = df_filtered[df_filtered['Operação Produtiva'].isin(ops)]
            
            if 'Segmento' in df.columns:
                segs = st.sidebar.multiselect("Segmento", options=df['Segmento'].unique())
                if segs:
                    df_filtered = df_filtered[df_filtered['Segmento'].isin(segs)]
            
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
                
                status_filter = st.sidebar.multiselect("Status", options=["PRIORIDADE", "ATENÇÃO", "OK"], default=["PRIORIDADE", "ATENÇÃO", "OK"])
                df_filtered = df_filtered[df_filtered['Status'].isin(status_filter)]
            
            # Métricas
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Pedidos", len(df_filtered))
            if 'Status' in df_filtered.columns:
                with col2:
                    st.metric("🔴 Prioridades", len(df_filtered[df_filtered['Status'] == 'PRIORIDADE']))
                with col3:
                    st.metric("🟠 Atenções", len(df_filtered[df_filtered['Status'] == 'ATENÇÃO']))
                with col4:
                    st.metric("🟢 OK", len(df_filtered[df_filtered['Status'] == 'OK']))
            
            st.markdown("---")
            
            # Visualizações
            if not df_filtered.empty:
                tab1, tab2 = st.tabs(["🎯 Cards por Cliente", "📅 Calendário"])
                
                with tab1:
                    create_enhanced_client_cards(df_filtered)
                
                with tab2:
                    create_calendar_view(df_filtered)
                
                # Tabela detalhada
                st.markdown("---")
                st.subheader("📋 Tabela Detalhada")
                
                display_cols = [col for col in ['Pedido', 'Cliente', 'Produto', 'Qtd', 'Status', 'Dt. Agendamento'] if col in df_filtered.columns]
                if display_cols:
                    df_display = df_filtered[display_cols].copy()
                    if 'Dt. Agendamento' in df_display.columns:
                        df_display['Dt. Agendamento'] = df_display['Dt. Agendamento'].dt.strftime('%d/%m/%Y')
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button("📥 Baixar CSV", data=csv, file_name=f"pedidos_{datetime.now().strftime('%d_%m_%Y')}.csv", mime="text/csv")
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
                
                ### Priorização:
                - 🔴 **PRIORIDADE**: Qtd > Saldo Calc.
                - 🟠 **ATENÇÃO**: Qtd > Saldo Atual
                - 🟢 **OK**: Estoque suficiente
            """)

def render_dashboard():
    """Renderiza dashboard"""
    st.markdown("## 📊 Dashboard de Gestão")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📋 Módulo 1</div>
                <div class="metric-label">Filtro de Confecção</div>
            </div>
            <br>
            - ✅ Upload de arquivos Excel<br>
            - ✅ Filtros avançados<br>
            - ✅ Exportação de relatórios
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📅 Módulo 2</div>
                <div class="metric-label">Agendamento de Pedidos</div>
            </div>
            <br>
            - ✅ Calendário interativo<br>
            - ✅ Cards por cliente<br>
            - ✅ Priorização automática
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">⚡ Diferenciais</div>
                <div class="metric-label">Funcionalidades</div>
            </div>
            <br>
            - ✅ Interface responsiva<br>
            - ✅ Cards interativos<br>
            - ✅ Download rápido
        """, unsafe_allow_html=True)

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    main()
