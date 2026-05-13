import streamlit as st
import pandas as pd
import io
import numpy as np
from datetime import datetime
import calendar
from collections import defaultdict

st.set_page_config(page_title="Filtro de Dados", layout="wide")

st.title("Filtro de Dados de Confecção")
st.markdown("Faça o upload do seu banco de dados em Excel para começar a filtrar e agrupar as informações.")

# Criar abas principais
tab_confeccao, tab_agendamento = st.tabs(["📋 Filtro de Confecção", "📅 Agendamento de Pedidos"])

# ==================== ABA 1: FILTRO DE CONFECÇÃO ====================
with tab_confeccao:
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
            
            st.sidebar.header("Filtros")
            
            # 1. Filtro: Agrupar/Filtrar por confecção
            if 'Confeccao' in df_filtered.columns:
                # Converter toda a coluna para string para evitar erro de tipos mistos
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
                    # Garantir que é string para aplicar o contains
                    df_filtered['Confeccionado'] = df_filtered['Confeccionado'].fillna("").astype(str)
                    df_filtered = df_filtered[df_filtered['Confeccionado'].str.contains(termo_busca, case=False, na=False)]
                    
            # 3. Filtro: Múltiplos Cód. Confeccionado
            if 'Cód Confec' in df_filtered.columns:
                # Converter a coluna original para string de forma consistente (removendo .0 de floats)
                df_filtered['Cód Confec'] = df_filtered['Cód Confec'].fillna("").astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                
                # Pegar todos os códigos únicos (removendo strings vazias)
                cods = [c for c in df_filtered['Cód Confec'].unique().tolist() if c and c != '']
                cods.sort()
                
                st.sidebar.markdown("---")
                st.sidebar.markdown("**Filtro Avançado: Cód. Confeccionado**")
                arquivo_cods = st.sidebar.file_uploader("Upload Excel com lista de códigos", type=["xlsx", "xls"], key="upload_cods")
                
                codigos_do_arquivo = []
                if arquivo_cods is not None:
                    try:
                        df_cods = pd.read_excel(arquivo_cods)
                        # Procurar coluna 'Cód Confec' ou usar a primeira coluna
                        if 'Cód Confec' in df_cods.columns:
                            serie_cods = df_cods['Cód Confec']
                        else:
                            serie_cods = df_cods.iloc[:, 0]
                            
                        # Converter a série para string, limpando espaços e '.0'
                        serie_cods = serie_cods.fillna("").astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                        codigos_do_arquivo = [c for c in serie_cods.tolist() if c and c.lower() != 'nan']
                        
                        # Manter apenas códigos que existem nas opções originais
                        codigos_do_arquivo = [c for c in codigos_do_arquivo if c in cods]
                        
                        if codigos_do_arquivo:
                            st.sidebar.success(f"{len(codigos_do_arquivo)} código(s) válido(s) encontrado(s) na lista.")
                        else:
                            st.sidebar.warning("Nenhum código correspondente encontrado. Verifique se os códigos da lista realmente existem no banco de dados principal.")
                    except Exception as e:
                        st.sidebar.error(f"Erro ao ler o arquivo de códigos: {e}")
                
                selecionados_cods = st.sidebar.multiselect("Cód. Confeccionado (Múltiplos):", options=cods, default=codigos_do_arquivo)
                
                # Se selecionou algum, aplica o filtro; senão, mostra todos (comportamento padrão)
                if selecionados_cods:
                    df_filtered = df_filtered[df_filtered['Cód Confec'].isin(selecionados_cods)]
                    
            # Mostrar o resultado principal
            st.markdown("---")
            
            # Encontrar quais colunas numéricas existem para somar
            cols_numericas = [col for col in ['Qtd', 'Qtd Ret', 'Saldo'] if col in df_filtered.columns]
            if cols_numericas:
                # Certificar que as colunas são numéricas
                for col in cols_numericas:
                    df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0)
            
            # NOVA FUNÇÃO: Filtrar linhas onde Qtd Ret é inferior a 95% da Qtd
            if 'Qtd' in df_filtered.columns and 'Qtd Ret' in df_filtered.columns:
                # Calcular o percentual de Qtd Ret em relação à Qtd
                # Evitar divisão por zero onde Qtd for 0
                mask = df_filtered['Qtd'] > 0
                df_filtered['Percentual_Ret'] = 0.0
                df_filtered.loc[mask, 'Percentual_Ret'] = (df_filtered.loc[mask, 'Qtd Ret'] / df_filtered.loc[mask, 'Qtd']) * 100
                
                # Aplicar filtro: manter apenas linhas onde percentual é MENOR que 95%
                linhas_before = len(df_filtered)
                df_filtered = df_filtered[df_filtered['Percentual_Ret'] < 95]
                linhas_after = len(df_filtered)
                
                # Remover a coluna auxiliar Percentual_Ret
                df_filtered = df_filtered.drop(columns=['Percentual_Ret'])
                
                # Informar ao usuário quantas linhas foram removidas
                linhas_removidas = linhas_before - linhas_after
                if linhas_removidas > 0:
                    st.info(f"ℹ️ {linhas_removidas} linha(s) removida(s) por terem Qtd Ret ≥ 95% da Qtd.")
            
            # Exibir Métricas no topo
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Registros", len(df_filtered))
            
            if 'Qtd' in cols_numericas:
                col2.metric("Soma de Qtd", f"{df_filtered['Qtd'].sum():.0f}")
            if 'Qtd Ret' in cols_numericas:
                col3.metric("Soma de Qtd Ret", f"{df_filtered['Qtd Ret'].sum():.0f}")
            if 'Saldo' in cols_numericas:
                col4.metric("Soma de Saldo", f"{df_filtered['Saldo'].sum():.0f}")
            
            if 'Confeccao' in df_filtered.columns:
                # Garantir que a coluna Confeccao seja string e remover valores vazios
                df_filtered['Confeccao'] = df_filtered['Confeccao'].astype(str)
                confeccoes_unicas = df_filtered['Confeccao'].dropna().unique().tolist()
                confeccoes_unicas = [c for c in confeccoes_unicas if c and c != 'nan' and c != '']
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
            
            # Exportar para Excel
            st.markdown("---")
            st.subheader("Exportar Relatórios")
            
            # Criar buffer de memória
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, sheet_name='Filtrado', index=False)
                if 'Confeccao' in df_filtered.columns and cols_numericas:
                    # Verificar se df_agrupado existe antes de tentar salvar
                    if 'df_agrupado' in locals():
                        df_agrupado.to_excel(writer, sheet_name='Agrupado', index=False)
                    
            col_btn1, col_btn2 = st.columns([1, 3])
            with col_btn1:
                st.download_button(
                    label="⬇️ Baixar Excel",
                    data=buffer.getvalue(),
                    file_name="relatorio_confeccao_filtrado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo. Verifique se o formato está correto. Detalhe do erro: {e}")
    else:
        st.info("👆 Por favor, faça o upload de um arquivo Excel acima para iniciar.")

# ==================== ABA 2: AGENDAMENTO DE PEDIDOS ====================
with tab_agendamento:
    st.header("📅 Agendamento de Pedidos")
    
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
    def load_data_agendamento(file_path):
        """Carrega dados do arquivo Excel"""
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()
            if 'Dt. Agendamento' in df.columns:
                df['Dt. Agendamento'] = pd.to_datetime(df['Dt. Agendamento'], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")
            return None
    
    # Função para determinar status
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
    
    # Função para criar cards de pedidos agrupados por cliente
    def create_client_cards(df_filtered):
        """Cria cards agrupados por cliente"""
        if 'Cliente' not in df_filtered.columns:
            st.warning("Coluna 'Cliente' não encontrada no arquivo.")
            return
            
        # Converter Cliente para string e ordenar com tratamento seguro
        df_filtered['Cliente_str'] = df_filtered['Cliente'].fillna("Desconhecido").astype(str)
        clients = sorted(df_filtered['Cliente_str'].unique(), key=str)
        
        for client in clients:
            df_client = df_filtered[df_filtered['Cliente_str'] == client]
            
            with st.container():
                st.markdown(f"### 👤 {client}")
                
                cols = st.columns(3)
                for idx, (_, row) in enumerate(df_client.iterrows()):
                    col_idx = idx % 3
                    
                    with cols[col_idx]:
                        # Verificar se colunas necessárias existem
                        qtd = row.get('Qtd', 0)
                        saldo_atual = row.get('Saldo Atual', 0)
                        saldo_calc = row.get('Saldo Calc.', 0)
                        
                        status_text, status_class = get_status(qtd, saldo_atual, saldo_calc)
                        
                        # Determinar cor da borda baseado no status
                        if status_class == "prioridade":
                            border_color = "#f44336"
                        elif status_class == "atencao":
                            border_color = "#ff9800"
                        else:
                            border_color = "#4caf50"
                        
                        # Formatar data se existir
                        data_str = "N/A"
                        if 'Dt. Agendamento' in row and pd.notna(row['Dt. Agendamento']):
                            try:
                                data_str = row['Dt. Agendamento'].strftime('%d/%m/%Y')
                            except:
                                data_str = str(row['Dt. Agendamento'])
                        
                        # Formatar valor se existir
                        valor_str = "N/A"
                        if 'R$ Total Calc.' in row and pd.notna(row['R$ Total Calc.']):
                            try:
                                valor_str = f"R$ {float(row['R$ Total Calc.']):.2f}"
                            except:
                                valor_str = str(row['R$ Total Calc.'])
                        
                        st.markdown(f"""
                            <div class="card" style="border-left: 4px solid {border_color};">
                                <div class="card-header">Pedido #{row.get('Pedido', 'N/A')}</div>
                                <div style="margin-bottom: 10px;">
                                    <span class="status-badge badge-{status_class}">{status_text}</span>
                                </div>
                                <div style="font-size: 12px; margin-bottom: 8px;">
                                    <b>Produto:</b> {row.get('Produto', 'N/A')}<br>
                                    <b>Cód:</b> {row.get('Cód Prod', 'N/A')}<br>
                                    <b>Data:</b> {data_str}<br>
                                    <b>Coleção:</b> {row.get('Coleção', 'N/A')}<br>
                                    <b>Operação:</b> {row.get('Operação Produtiva', 'N/A')}<br>
                                    <b>Segmento:</b> {row.get('Segmento', 'N/A')}
                                </div>
                                <hr style="margin: 8px 0;">
                                <div style="font-size: 11px;">
                                    <b>Quantidade Pedida:</b> {qtd}<br>
                                    <b>Saldo Atual:</b> {saldo_atual}<br>
                                    <b>Saldo Calculado:</b> {saldo_calc}<br>
                                    <b>Valor Total:</b> {valor_str}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
    
    # Função para criar visualização de calendário
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
                            
                            # Contar status
                            prioridades = sum(1 for p in pedidos_dia if p['status_class'] == 'prioridade')
                            atencoes = sum(1 for p in pedidos_dia if p['status_class'] == 'atencao')
                            
                            cor_fundo = "#f8d7da" if prioridades > 0 else "#fff3cd" if atencoes > 0 else "#d4edda"
                            
                            with col:
                                with st.expander(f"📌 **{dia}** ({len(pedidos_dia)} pedido(s))", 
                                               expanded=False):
                                    for pedido in pedidos_dia:
                                        status_badge_class = f"badge-{pedido['status_class']}"
                                        valor_formatado = f"R$ {float(pedido['valor']):.2f}" if pedido['valor'] else "N/A"
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
                                                    <b>Valor:</b> {valor_formatado}<br>
                                                    <b>Operação:</b> {pedido['operacao']}<br>
                                                    <b>Segmento:</b> {pedido['segmento']}<br>
                                                    <b>Coleção:</b> {pedido['colecao']}
                                                </small>
                                            </div>
                                        """, unsafe_allow_html=True)
                        else:
                            col.markdown(f"<div style='text-align: center; padding: 10px; color: #ccc;'>{dia}</div>", 
                                        unsafe_allow_html=True)
    
    # Carregamento de arquivo
    uploaded_file_agendamento = st.file_uploader(
        "Carregue o arquivo Excel com os pedidos",
        type=['xlsx', 'xls'],
        key="agendamento_file",
        help="Arquivo deve conter as colunas: Pedido, Cliente, Cód Prod, Produto, Qtd, R$ Total Calc., Operação Produtiva, Segmento, Saldo Atual, Coleção, Saldo Calc., Dt. Agendamento"
    )
    
    if uploaded_file_agendamento:
        df = load_data_agendamento(uploaded_file_agendamento)
        
        if df is not None and not df.empty:
            # Exibir colunas disponíveis para debug
            st.sidebar.write("Colunas do arquivo:", list(df.columns))
            
            # Filtros na sidebar
            st.sidebar.header("🔍 Filtros - Agendamento")
            
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
            
            # Adicionar coluna de status para filtro (com tratamento de erro)
            if 'Qtd' in df_filtered.columns and 'Saldo Atual' in df_filtered.columns and 'Saldo Calc.' in df_filtered.columns:
                df_filtered['Status'] = df_filtered.apply(
                    lambda row: get_status(row['Qtd'], row['Saldo Atual'], row['Saldo Calc.'])[0],
                    axis=1
                )
                df_filtered = df_filtered[df_filtered['Status'].isin(status_filtro)]
            else:
                st.error("❌ Colunas necessárias não encontradas: 'Qtd', 'Saldo Atual' ou 'Saldo Calc.'")
                st.info("Por favor, verifique se o arquivo contém todas as colunas necessárias.")
                st.stop()
            
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
            
            # Preparar dados para exibição com colunas que existem
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
            - **R$ Total Calc.** - Valor total do pedido (calculado)
            - **Operação Produtiva** - Tipo de operação
            - **Segmento** - Segmento de mercado
            - **Saldo Atual** - Estoque atual disponível
            - **Coleção** - Coleção do produto
            - **Saldo Calc.** - Estoque calculado/projetado
            - **Dt. Agendamento** - Data do agendamento (formato: DD/MM/YYYY)
            
            ### 📊 Como a priorização funciona:
            
            - 🔴 **PRIORIDADE**: Quando Qtd > Saldo Calc. (sem estoque previsão)
            - 🟠 **ATENÇÃO**: Quando Qtd > Saldo Atual (sem estoque atual)
            - 🟢 **OK**: Quando há estoque suficiente
        """)
