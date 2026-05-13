import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import calendar
from collections import defaultdict
import plotly.graph_objects as go

# Configurar página
st.set_page_config(
    page_title="Agendamento de Pedidos",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos customizados
st.markdown("""
    <style>
        .atencao { color: #ff9800; font-weight: bold; }
        .prioridade { color: #f44336; font-weight: bold; }
        .status-ok { color: #4caf50; font-weight: bold; }
        .card { 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            padding: 15px; 
            margin: 10px 0;
            background-color: #f9f9f9;
        }
        .card-header { font-weight: bold; font-size: 16px; margin-bottom: 10px; }
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            margin-right: 5px;
        }
        .badge-atencao { background-color: #fff3cd; color: #856404; }
        .badge-prioridade { background-color: #f8d7da; color: #721c24; }
        .badge-ok { background-color: #d4edda; color: #155724; }
    </style>
""", unsafe_allow_html=True)

# Função para carregar dados do Excel
@st.cache_data
def load_data(file_path):
    """Carrega dados do arquivo Excel"""
    try:
        df = pd.read_excel(file_path)
        df['Dt. Agendamento'] = pd.to_datetime(df['Dt. Agendamento'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

# Função para determinar status
def get_status(qtd, saldo_atual, saldo_calculado):
    """
    Determina o status do pedido baseado nas quantidades
    """
    if qtd > saldo_calculado:
        return "PRIORIDADE", "prioridade"
    elif qtd > saldo_atual:
        return "ATENÇÃO", "atencao"
    else:
        return "OK", "ok"

# Função para criar cards de pedidos agrupados por cliente
def create_client_cards(df_filtered):
    """Cria cards agrupados por cliente"""
    clients = df_filtered['Cliente'].unique()
    
    for client in sorted(clients):
        df_client = df_filtered[df_filtered['Cliente'] == client]
        
        with st.container():
            st.markdown(f"### 👤 {client}")
            
            cols = st.columns(3)
            for idx, (_, row) in enumerate(df_client.iterrows()):
                col_idx = idx % 3
                
                with cols[col_idx]:
                    status_text, status_class = get_status(
                        row['Qtd'], 
                        row['Saldo Atual'], 
                        row['Saldo Calculado']
                    )
                    
                    # Determinar cor da borda baseado no status
                    if status_class == "prioridade":
                        border_color = "#f44336"
                    elif status_class == "atencao":
                        border_color = "#ff9800"
                    else:
                        border_color = "#4caf50"
                    
                    st.markdown(f"""
                        <div class="card" style="border-left: 4px solid {border_color};">
                            <div class="card-header">Pedido #{row['Pedido']}</div>
                            <div style="margin-bottom: 10px;">
                                <span class="status-badge badge-{status_class}">{status_text}</span>
                            </div>
                            <div style="font-size: 12px; margin-bottom: 8px;">
                                <b>Produto:</b> {row['Produto']}<br>
                                <b>Cód:</b> {row['Cód Prod']}<br>
                                <b>Data:</b> {row['Dt. Agendamento'].strftime('%d/%m/%Y') if pd.notna(row['Dt. Agendamento']) else 'N/A'}<br>
                                <b>Coleção:</b> {row['Coleção']}<br>
                                <b>Operação:</b> {row['Operação Produtiva']}<br>
                                <b>Segmento:</b> {row['Segmento']}
                            </div>
                            <hr style="margin: 8px 0;">
                            <div style="font-size: 11px;">
                                <b>Quantidade Pedida:</b> {row['Qtd']}<br>
                                <b>Saldo Atual:</b> {row['Saldo Atual']}<br>
                                <b>Saldo Calculado:</b> {row['Saldo Calculado']}<br>
                                <b>Valor Total:</b> R$ {row['R$ Total']:.2f}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# Função para criar visualização de calendário
def create_calendar_view(df_filtered):
    """Cria visualização de calendário com pedidos agrupados por data"""
    
    # Agrupar pedidos por data
    df_filtered_clean = df_filtered.dropna(subset=['Dt. Agendamento'])
    
    if df_filtered_clean.empty:
        st.warning("Nenhum pedido com data de agendamento disponível para exibir no calendário.")
        return
    
    # Criar estrutura de dados para o calendário
    agendamentos = defaultdict(list)
    
    for _, row in df_filtered_clean.iterrows():
        data = row['Dt. Agendamento'].date()
        status_text, status_class = get_status(
            row['Qtd'], 
            row['Saldo Atual'], 
            row['Saldo Calculado']
        )
        
        agendamentos[data].append({
            'pedido': row['Pedido'],
            'produto': row['Produto'],
            'cliente': row['Cliente'],
            'qtd': row['Qtd'],
            'saldo_atual': row['Saldo Atual'],
            'saldo_calculado': row['Saldo Calculado'],
            'valor': row['R$ Total'],
            'status': status_text,
            'status_class': status_class,
            'colecao': row['Coleção'],
            'operacao': row['Operação Produtiva'],
            'segmento': row['Segmento']
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
                        
                        # Contar status
                        prioridades = sum(1 for p in pedidos_dia if p['status_class'] == 'prioridade')
                        atencoes = sum(1 for p in pedidos_dia if p['status_class'] == 'atencao')
                        
                        cor_fundo = "#f8d7da" if prioridades > 0 else "#fff3cd" if atencoes > 0 else "#d4edda"
                        
                        with col:
                            with st.expander(f"📌 **{dia}** ({len(pedidos_dia)} pedido(s))", 
                                           expanded=False):
                                for pedido in pedidos_dia:
                                    status_badge_class = f"badge-{pedido['status_class']}"
                                    st.markdown(f"""
                                        <div style="margin-bottom: 10px; padding: 8px; border-left: 3px solid #ddd; background-color: #f5f5f5;">
                                            <b>Pedido #{pedido['pedido']}</b><br>
                                            <span class="status-badge {status_badge_class}">{pedido['status']}</span><br>
                                            <small>
                                                <b>Cliente:</b> {pedido['cliente']}<br>
                                                <b>Produto:</b> {pedido['produto']}<br>
                                                <b>Qtd Pedida:</b> {pedido['qtd']}<br>
                                                <b>Saldo Atual:</b> {pedido['saldo_atual']}<br>
                                                <b>Saldo Calc:</b> {pedido['saldo_calculado']}<br>
                                                <b>Valor:</b> R$ {pedido['valor']:.2f}<br>
                                                <b>Operação:</b> {pedido['operacao']}<br>
                                                <b>Segmento:</b> {pedido['segmento']}<br>
                                                <b>Coleção:</b> {pedido['colecao']}
                                            </small>
                                        </div>
                                    """, unsafe_allow_html=True)
                    else:
                        col.markdown(f"<div style='text-align: center; padding: 10px; color: #ccc;'>{dia}</div>", 
                                    unsafe_allow_html=True)

# Interface principal
st.title("📅 Agendamento de Pedidos")

# Sidebar para carregar arquivo
with st.sidebar:
    st.header("Configurações")
    
    uploaded_file = st.file_uploader(
        "Carregue o arquivo Excel com os pedidos",
        type=['xlsx', 'xls'],
        help="Arquivo deve conter as colunas: Pedido, Cliente, Cód Prod, Produto, Qtd, R$ Total, Operação Produtiva, Segmento, Saldo Atual, Coleção, Saldo Calculado, Dt. Agendamento"
    )

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None and not df.empty:
        # Filtros na sidebar
        with st.sidebar:
            st.markdown("---")
            st.subheader("🔍 Filtros")
            
            # Filtro por Operação Produtiva
            operacoes = st.multiselect(
                "Operação Produtiva",
                options=df['Operação Produtiva'].unique(),
                help="Selecione uma ou mais operações"
            )
            
            # Filtro por Segmento
            segmentos = st.multiselect(
                "Segmento",
                options=df['Segmento'].unique(),
                help="Selecione um ou mais segmentos"
            )
            
            # Filtro por Coleção
            colecoes = st.multiselect(
                "Coleção",
                options=df['Coleção'].unique(),
                help="Selecione uma ou mais coleções"
            )
            
            # Filtro por Cliente
            clientes = st.multiselect(
                "Cliente",
                options=df['Cliente'].unique(),
                help="Selecione um ou mais clientes"
            )
            
            # Filtro por Status
            status_filtro = st.multiselect(
                "Status",
                options=["PRIORIDADE", "ATENÇÃO", "OK"],
                default=["PRIORIDADE", "ATENÇÃO", "OK"],
                help="Selecione os status que deseja visualizar"
            )
        
        # Aplicar filtros
        df_filtered = df.copy()
        
        if operacoes:
            df_filtered = df_filtered[df_filtered['Operação Produtiva'].isin(operacoes)]
        
        if segmentos:
            df_filtered = df_filtered[df_filtered['Segmento'].isin(segmentos)]
        
        if colecoes:
            df_filtered = df_filtered[df_filtered['Coleção'].isin(colecoes)]
        
        if clientes:
            df_filtered = df_filtered[df_filtered['Cliente'].isin(clientes)]
        
        # Adicionar coluna de status para filtro
        df_filtered['Status'] = df_filtered.apply(
            lambda row: get_status(row['Qtd'], row['Saldo Atual'], row['Saldo Calculado'])[0],
            axis=1
        )
        
        df_filtered = df_filtered[df_filtered['Status'].isin(status_filtro)]
        
        # Exibir resumo dos dados
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
        tab1, tab2 = st.tabs(["📅 Calendário", "🎯 Cards por Cliente"])
        
        with tab1:
            if not df_filtered.empty:
                create_calendar_view(df_filtered)
            else:
                st.warning("Nenhum pedido encontrado com os filtros selecionados.")
        
        with tab2:
            if not df_filtered.empty:
                create_client_cards(df_filtered)
            else:
                st.warning("Nenhum pedido encontrado com os filtros selecionados.")
        
        # Tabela de detalhes
        st.markdown("---")
        st.subheader("📋 Tabela Detalhada")
        
        # Preparar dados para exibição
        df_display = df_filtered[[
            'Pedido', 'Cliente', 'Cód Prod', 'Produto', 'Qtd', 
            'Saldo Atual', 'Saldo Calculado', 'R$ Total', 
            'Operação Produtiva', 'Segmento', 'Coleção', 'Dt. Agendamento', 'Status'
        ]].copy()
        
        df_display['Dt. Agendamento'] = df_display['Dt. Agendamento'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            df_display.sort_values('Pedido'),
            use_container_width=True,
            hide_index=True
        )
        
        # Download dos dados filtrados
        csv = df_display.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar dados filtrados (CSV)",
            data=csv,
            file_name=f"pedidos_agendados_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv"
        )

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
        - **R$ Total** - Valor total do pedido
        - **Operação Produtiva** - Tipo de operação
        - **Segmento** - Segmento de mercado
        - **Saldo Atual** - Estoque atual disponível
        - **Coleção** - Coleção do produto
        - **Saldo Calculado** - Estoque calculado/projetado
        - **Dt. Agendamento** - Data do agendamento (formato: DD/MM/YYYY)
        
        ### 📊 Como a priorização funciona:
        
        - 🔴 **PRIORIDADE**: Quando Qtd > Saldo Calculado (sem estoque previsão)
        - 🟠 **ATENÇÃO**: Quando Qtd > Saldo Atual (sem estoque atual)
        - 🟢 **OK**: Quando há estoque suficiente
    """)
