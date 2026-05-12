import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Filtro de Dados", layout="wide")

st.title("Filtro de Dados de Confecção")
st.markdown("Faça o upload do seu banco de dados em Excel para começar a filtrar e agrupar as informações.")

uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Carregar a planilha
        df = pd.read_excel(uploaded_file)
        
        # Limpar os nomes das colunas (remover espaços em branco no início e no fim) para facilitar
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
            # Preencher valores nulos temporariamente para não dar erro na interface
            df_filtered['Confeccao'] = df_filtered['Confeccao'].fillna("Vazio")
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
                df_filtered['Confeccionado'] = df_filtered['Confeccionado'].astype(str)
                df_filtered = df_filtered[df_filtered['Confeccionado'].str.contains(termo_busca, case=False, na=False)]
                
        # 3. Filtro: Múltiplos Cód. Confeccionado
        if 'Cód Confec' in df_filtered.columns:
            # Converter a coluna original para string de forma consistente (removendo .0 de floats)
            df_filtered['Cód Confec'] = df_filtered['Cód Confec'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            # Pegar todos os códigos únicos (removendo 'nan' se houver)
            cods = [c for c in df_filtered['Cód Confec'].unique().tolist()
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
                    serie_cods = serie_cods.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                    codigos_do_arquivo = [c for c in serie_cods.tolist() if c.lower() != 'nan']
                    
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
            confeccoes_unicas = df_filtered['Confeccao'].dropna().unique().tolist()
            confeccoes_unicas = [str(c) for c in confeccoes_unicas]
            confeccoes_unicas.sort()
            
            nomes_abas = ["📋 Visão Geral", "📊 Resumo Agrupado"] + [f"📁 Aba {conf}" for conf in confeccoes_unicas]
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
                    df_aba = df_filtered[df_filtered['Confeccao'].astype(str) == conf]
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
