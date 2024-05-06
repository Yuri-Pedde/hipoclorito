import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import geopandas as gpd
import unicodedata
from streamlit_extras.app_logo import add_logo 
from streamlit_elements import elements, mui, html

st.set_page_config(
    page_title="NaClO RS",
    page_icon="	:droplet:",
    layout="wide",
    initial_sidebar_state='collapsed'
)

with st.container():
    coluna_inicial1,coluna_inicial2,coluna_inicial3 = st.columns([1,6,1])
    with coluna_inicial1:
        st.image("logo_estado.png", width=250)

    with coluna_inicial2:
        st.markdown(f'<h1 style="text-align: center;color:#000000;font-size:42px;">{"Painel de Análise de Distribuição de Hipoclorito de Sódio no RS"}</h1>', unsafe_allow_html=True)    
        st.markdown(f'<h1 style="text-align: center;color:#000000;font-size:24px;">{"VIGIAGUA/DVAS/CEVS - Secretaria de Saúde do Estado do Rio Grande do Sul"}</h1>', unsafe_allow_html=True)

    with coluna_inicial3:
        st.image('CEVS.png', width=200)
        
@st.cache_data
def remover_acentos(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
@st.cache_data #nao precisa fazer o loading o tempo todo
def load_data(url):
    df = pd.read_table(url)
    df = df.dropna(how='all', axis=0)
    df = df.rename(columns={'Carimbo de data/hora':'data e hora'})
    df = df[['data e hora', 'Coordenadoria Regional de Saúde (CRS)',
        'Município','Quantidade de Caixas', 'Motivo',
        'População Atendida - Estimativa', 'Locais de Distribuição']]
    df = df[df['data e hora']!='IMS']
    df_notnull = df[(df['Coordenadoria Regional de Saúde (CRS)']!="")&(df['Município']!='2')]
    df_notnull['Coordenadoria Regional de Saúde (CRS)'] = df_notnull['Coordenadoria Regional de Saúde (CRS)'].str.replace('5ªCRS', '5ª CRS')
    df_notnull['Coordenadoria Regional de Saúde (CRS)'] = df_notnull['Coordenadoria Regional de Saúde (CRS)'].str.strip()
    df_notnull.reset_index(drop=True, inplace = True)
    lista_estimativa = []
    for i in df_notnull['População Atendida - Estimativa']:
        try:
            i = int(i)
        except:
            try:
                if 'mil' not in i:
                    numeros=""
                    for caractere in i:
                        if caractere.isdigit():
                            numeros += caractere
                    i = int(numeros)
                    #print(numeros)
                else:
                    for caractere in i:
                        if caractere.isdigit():
                            numeros += caractere
                    i = int(numeros)*1000
            except:
                pass
            pass
        if '.' in str(i):
            try:
                numero = str(i).split('.')[0]+str(i).split('.')[1]
                numero = int(numero)
            except:
                numero = "Sem dados"
                pass
        elif "" == i:
            numero = "Sem dados"
        elif isinstance(i,str):
            numero = "Sem dados"
        elif isinstance(i,int):
            numero = i
        else:
            numero = "Sem dados"
        lista_estimativa.append(numero)
    
    df_notnull['População Atendida - Estimativa2'] = lista_estimativa
    df_notnull = df_notnull[['data e hora','Coordenadoria Regional de Saúde (CRS)', 'Município',
       'Quantidade de Caixas', 'Motivo','População Atendida - Estimativa2']]
    df_notnull=df_notnull.dropna(how='any', axis=0)
    df_notnull["Quantidade de Frascos 50mL"] = df_notnull["Quantidade de Caixas"]*50
    df_notnull['Data de Registro'] = df_notnull['data e hora'].str.split(' ',expand=True)[0]
    df_notnull['Data de Registro'] = pd.to_datetime(df_notnull['Data de Registro'],format="%d/%m/%Y", errors='coerce')
    df_notnull['Motivo'] = df_notnull['Motivo'].str.replace('DIstribuição em SAI','Distribuição em SAI')
    df_notnull['Motivo'] = df_notnull['Motivo'].str.replace('DIstribuição em SAC','Distribuição em SAC')
    df_notnull['Motivo'] = df_notnull['Motivo'].str.replace('DIstribuição em escolas','Distribuição em escolas')
    df_notnull['Motivo'] = df_notnull['Motivo'].str.replace('Desastre - Estiagem (preventiva)','Desastre - Estiagem')
    df_notnull['Motivo'] = df_notnull['Motivo'].str.replace('distribuição em SAI','Distribuição em SAI')
    df_notnull['data e hora'] = df_notnull['data e hora'].str.strip()
    df_notnull['Ano de referência'] = df_notnull['data e hora'].str.split(' ', expand=True)[0].str.split('/', expand=True)[2]
    df_notnull['Mês de referência'] = df_notnull['data e hora'].str.split(' ', expand=True)[0].str.split('/', expand=True)[1]
    df_notnull['Dia de referência'] = df_notnull['data e hora'].str.split(' ', expand=True)[0].str.split('/', expand=True)[0]
    df_notnull['Date'] = df_notnull['Dia de referência'] + '/' + df_notnull['Mês de referência'] + '/' + df_notnull['Ano de referência']
    df_notnull['Date'] = pd.to_datetime(df_notnull['Date'], format = "%d/%m/%Y")
    return df_notnull

@st.cache_data #nao precisa fazer o loading o tempo todo
def load_geodata(url):
    gdf = gpd.read_file(url)
    return gdf

df_hipoclorito = load_data('https://docs.google.com/spreadsheets/d/e/2PACX-1vRAccHk7j1-Oh7u6P-r70vX4WWud1S_3SCURCfcjzPgz1x7a9GH8OAocnxbz9zmvVNG0bHMGQRmzOyI/pub?output=tsv')
df_hipoclorito['Ano de referência'] = df_hipoclorito['Ano de referência'].fillna('0')
df_hipoclorito = df_hipoclorito[df_hipoclorito['Ano de referência']!='0']
df_hipoclorito['Município'] = df_hipoclorito['Município'].apply(lambda x: remover_acentos(x.strip().lower()))

municipios = load_geodata('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
municipios["IBGE6"] = municipios["CD_MUN"].str.slice(0,6)
municipios['NOME_MUNICIPIO'] = municipios['NM_MUN']
municipios['NOME_MUNICIPIO'] = municipios['NOME_MUNICIPIO'].apply(lambda x: remover_acentos(x.strip().lower()))

st.markdown("""
<style>
    [data-testid=stSelectbox] {
        color: #000000;
        text-align:center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
col_cabecalho1, col_cabecalho2 = st.columns([1,1.2])
with col_cabecalho1:
    ano = st.selectbox('Selecione o ano',sorted(df_hipoclorito['Ano de referência'].unique()), index=len(df_hipoclorito['Ano de referência'].unique())-1)

filtro_ano = df_hipoclorito['Ano de referência'] == str(ano)

df_hipoclorito_ano = df_hipoclorito[filtro_ano]
df_hipoclorito_ano['Quantidade de Frascos 50mL'] = df_hipoclorito_ano['Quantidade de Frascos 50mL'].astype(int)

df_hipoclorito_ano_pivoted = pd.pivot_table(df_hipoclorito_ano, index=['Coordenadoria Regional de Saúde (CRS)', 'Município'], values='Quantidade de Frascos 50mL', aggfunc='sum').fillna(0).reset_index()

municipios = municipios[['geometry','IBGE6','NOME_MUNICIPIO']]
dados_mapa_final = municipios.merge(df_hipoclorito_ano_pivoted, left_on ="NOME_MUNICIPIO", right_on='Município', how='left')
dados_mapa_final['Quantidade de Frascos 50mL'] = dados_mapa_final['Quantidade de Frascos 50mL'].fillna(0)
dados_mapa_final = dados_mapa_final[['geometry','IBGE6','NOME_MUNICIPIO','Coordenadoria Regional de Saúde (CRS)','Quantidade de Frascos 50mL']]
dados_mapa_final['IBGE6'] = dados_mapa_final['IBGE6'].astype(str)

crs_muni = pd.read_csv("https://raw.githubusercontent.com/Yuri-Pedde/hipoclorito/main/CRS_MUNI.csv?token=GHSAT0AAAAAACKGYFXD3QRR23AGULBRMDP2ZK3WD2A")
dicionario_crs_certa = {'1ª': '01ª CRS',
                        '2ª': '02ª CRS',
                        '3ª': '03ª CRS',
                        '4ª': '04ª CRS',
                        '5ª': '05ª CRS',
                        '6ª': '06ª CRS',
                        '7ª': '07ª CRS',
                        '8ª': '08ª CRS',
                        '9ª': '09ª CRS',
                        '10ª': '10ª CRS',
                        '11ª': '11ª CRS',
                        '12ª': '12ª CRS',
                        '13ª': '13ª CRS',
                        '14ª': '14ª CRS',
                        '15ª': '15ª CRS',
                        '16ª': '16ª CRS',
                        '17ª': '17ª CRS',
                        '18ª': '18ª CRS'}
crs_muni['MUNICÍPIOS'] = crs_muni['MUNICÍPIOS'].apply(lambda x: remover_acentos(x.strip().lower()))
crs_muni['CRS'] = crs_muni['CRS'].map(dicionario_crs_certa)
crs_muni_2 = crs_muni.set_index('MUNICÍPIOS')

dicionario_crs_muni = crs_muni_2.to_dict()['CRS']
dados_mapa_final['NOME_MUNICIPIO'] = dados_mapa_final['NOME_MUNICIPIO'].apply(lambda x: x.strip().lower())
dados_mapa_final['CRS'] = dados_mapa_final['NOME_MUNICIPIO'].map(dicionario_crs_muni)
dados_mapa_final = dados_mapa_final.drop('Coordenadoria Regional de Saúde (CRS)', axis=1)

import json

geojson_str = dados_mapa_final.to_json()

map_fig = px.choropleth_mapbox(dados_mapa_final, 
                                geojson=geojson_str,  # Use the GeoJSON string
                                locations=dados_mapa_final.index, 
                                color='Quantidade de Frascos 50mL',
                                color_continuous_scale='YlOrBr',
                                center={'lat':-30.452349861219243, 'lon':-53.55320517512141},
                                zoom=5.7,
                                mapbox_style="stamen-watercolor",
                                hover_name='NOME_MUNICIPIO',
                                width=1000,
                                height=750,
                                template='plotly_dark',
                                title=f'Mapa de Calor: Quantidade de Frascos Distribuídos por Município do Rio Grande do Sul no ano de {ano}')

map_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=30, r=30, t=50, b=30))

map_fig.update_traces(marker_line_width=0.2)

# Update color axes
map_fig.update_coloraxes(colorbar={'orientation':'h', 'thickness':30},
                         colorbar_yanchor='bottom',
                         colorbar_y=-0.2) 
                                  
dados_mapa_final_crs = dados_mapa_final.groupby('CRS').sum('Quantidade de Frascos 50mL')
dados_crs = dados_mapa_final_crs.rename_axis('CRS').reset_index()
dados_crs = dados_crs.rename(columns={'Quantidade de Frascos 50mL':'Quantidade de Frascos Distribuídos'})
dados_crs['Quantidade de Frascos Distribuídos'] = dados_crs['Quantidade de Frascos Distribuídos'].astype(int)

contagem_pedidos_crs = df_hipoclorito_ano.groupby('Coordenadoria Regional de Saúde (CRS)').count()
contagem_pedidos_crs = contagem_pedidos_crs.rename_axis('CRS').reset_index()
contagem_pedidos_crs = contagem_pedidos_crs[['CRS','Município']]
contagem_pedidos_crs = contagem_pedidos_crs.rename(columns={'Município':'Número de Pedidos'})
total_pedidos = contagem_pedidos_crs['Número de Pedidos'].sum()
contagem_pedidos_crs[r'% do total de pedidos no RS'] = round((contagem_pedidos_crs['Número de Pedidos']/total_pedidos)*100,2).astype(float)

tabela_merged_calor = pd.merge(contagem_pedidos_crs, dados_crs, on='CRS')
tabela_merged_calor = tabela_merged_calor.set_index('CRS')

filtro_desastre = df_hipoclorito_ano['Motivo'].str.contains('Desastre')==True
df_desastre = df_hipoclorito_ano[filtro_desastre]
df_hipoclorito_ano_desastre_pop_semdados = df_desastre[df_desastre['População Atendida - Estimativa2']!="Sem dados"]
total_desastre = round((df_desastre['Quantidade de Frascos 50mL'].sum()/dados_crs['Quantidade de Frascos Distribuídos'].sum()),4)
total_rotina = 1-total_desastre

tabela_merged_calor_resetada = tabela_merged_calor.reset_index()
crs_max = tabela_merged_calor_resetada.loc[tabela_merged_calor_resetada['Quantidade de Frascos Distribuídos'].idxmax()]['CRS']
crs_max_pedidos = tabela_merged_calor_resetada.loc[tabela_merged_calor_resetada['Número de Pedidos'].idxmax()]['CRS']
mun_max_frascos = dados_mapa_final.loc[dados_mapa_final['Quantidade de Frascos 50mL'].idxmax()]['NOME_MUNICIPIO']
contagem_pedidos_municipios = df_hipoclorito_ano.groupby('Município').count()
contagem_pedidos_municipios = contagem_pedidos_municipios.rename_axis('Município').reset_index()
contagem_pedidos_municipios = contagem_pedidos_municipios[['Município', 'Coordenadoria Regional de Saúde (CRS)']]
contagem_pedidos_municipios = contagem_pedidos_municipios.rename(columns={'Coordenadoria Regional de Saúde (CRS)':'Número de Pedidos'})
contagem_pedidos_municipios['Município'] = contagem_pedidos_municipios['Município'].apply(lambda x: str(x).strip().capitalize() if ' ' not in str(x) else str(x))
mun_max_pedidos = contagem_pedidos_municipios.loc[contagem_pedidos_municipios['Número de Pedidos'].idxmax()]['Município']    
df_hipoclorito_ano_pop_semdados = df_hipoclorito_ano[df_hipoclorito_ano['População Atendida - Estimativa2']!="Sem dados"]

col1, col2 = st.columns([1,1.2])
tabela_df = tabela_merged_calor[['Quantidade de Frascos Distribuídos', 'Número de Pedidos',r'% do total de pedidos no RS']]
tabela_df_stilished = tabela_df.style.background_gradient(cmap='YlOrBr', subset=['Quantidade de Frascos Distribuídos', 'Número de Pedidos'])

with col1:
     st.dataframe(tabela_df_stilished, height = 675, use_container_width =True,
                column_config={r'% do total de pedidos no RS': st.column_config.ProgressColumn(
                                f'% do Total de Solicitações em {ano}',
                                help="Porcentagem de Solicitações da CRS em relação ao total de Solicitações do Rio Grande do Sul",
                                format="%f",
                                min_value=0,
                                max_value=100,),
                                'Quantidade de Frascos Distribuídos': st.column_config.NumberColumn(
                                f'Total de Frascos Distribuídos em {ano}',
                                help="Quantidade de Frascos de Hipoclorito de Sódio Distribuídos por CRS",format="%d"),
                                "Número de Pedidos": st.column_config.NumberColumn(
                                f"Total de Solicitações em {ano}",
                                help=f"Número de Solicitações da CRS em {ano}", format="%d")}
                                )

with col2:
    map_fig

st.markdown("""
<style>
    [data-testid=stMetric] {
        background: white;
        color: #000000;
        text-align:center;
        border-radius: 20px;
        border: 2px solid #000000;
        box-sizing: border-box;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    [data-testid=stMetricLabel] {
        color: #000000;
        width: fit-content; 
        margin: auto;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
with col_cabecalho2:
    col_cabecalho2_1, col_cabecalho2_2, col_cabecalho2_3 = st.columns(3)
    col_cabecalho2_1.metric(f'Total de Solicitações em {ano}', total_pedidos)
    col_cabecalho2_2.metric(f'Total de Frascos Distribuídos em {ano}', dados_crs['Quantidade de Frascos Distribuídos'].sum())
    col_cabecalho2_3.metric(f'População Atendida (Estimada) em {ano}', df_hipoclorito_ano_pop_semdados['População Atendida - Estimativa2'].sum())

col4, col5, col6, col7 = st.columns([1.1,1.1,1.3,1.3])
with col4:
    with elements("style_mui_sx"):
        mui.Box(
                f"⭐CRS com mais frascos distribuídos  em {ano}: {crs_max}",
                sx={
                    "bgcolor": "#ffffff",
                    "boxShadow": 1,
                    "borderRadius": 2,
                    "p": 2,
                    "minWidth": 300,
                    'text-align':'center',
                    'border-radius': '20px',
                    'border': '2px solid #000000',
                    "color":"#000000",
                    "font-weight":'bold'
                }
            )
with col5:
    with elements("style_mui_sx2"):
        mui.Box(
                f"⭐CRS com mais solicitações realizadas em {ano}: {crs_max_pedidos}",
                sx={
                    "bgcolor": "#ffffff",
                    "boxShadow": 1,
                    "borderRadius": 2,
                    "p": 2,
                    "minWidth": 300,
                    'text-align':'center',
                    'border-radius': '20px',
                    'border': '2px solid #000000',
                    "color":"#000000",
                    "font-weight":'bold'
                }
            )
with col6:
    with elements("style_mui_sx3"):
        mui.Box(
                f"⭐Município com mais frascos distribuídos em {ano}: {mun_max_frascos}",
                sx={
                    "bgcolor": "#ffffff",
                    "boxShadow": 1,
                    "borderRadius": 2,
                    "p": 2,
                    "minWidth": 300,
                    'text-align':'center',
                    'border-radius': '20px',
                    'border': '2px solid #000000',
                    "color":"#000000",
                    "font-weight":'bold'
                }
            )

with col7:
    with elements("style_mui_sx4"):
        mui.Box(
                f"⭐Município com mais solicitações realizados em {ano}: {mun_max_pedidos}",
                sx={
                    "bgcolor": "#ffffff",
                    "boxShadow": 1,
                    "borderRadius": 2,
                    "p": 2,
                    "minWidth": 300,
                    'text-align':'center',
                    'border-radius': '20px',
                    'border': '2px solid #000000',
                    "color":"#000000",
                    "font-weight":'bold'
                }
            )
        
#INICIANDO A PARTE DE DESASTRES AMBIENTAIS

df_hipoclorito_ano_desastre = df_hipoclorito_ano[filtro_desastre]

total_pedidos_desastre = df_hipoclorito_ano_desastre['Motivo'].count()
df_hipoclorito_ano_desastre_pop_semdados = df_hipoclorito_ano_desastre[df_hipoclorito_ano_desastre['População Atendida - Estimativa2']!="Sem dados"]
total_população_atendida = df_hipoclorito_ano_desastre_pop_semdados['População Atendida - Estimativa2'].sum()
df_desastre_df = df_hipoclorito_ano_desastre[['Date','Coordenadoria Regional de Saúde (CRS)','Município','Motivo','População Atendida - Estimativa2','Quantidade de Frascos 50mL',"Mês de referência"]]
df_desastre_df = df_desastre_df.rename(columns={'Date':'Registro', 'Coordenadoria Regional de Saúde (CRS)':'CRS', 'População Atendida - Estimativa2':'Estimativa de Pop. Atendida','Quantidade de Frascos 50mL':'Quantidade de Frascos Distribuídos'})
df_desastre_df['Motivo'] = df_desastre_df['Motivo'].fillna('Desastre Não Identificado')
df_desastre_df['Motivo'] = df_desastre_df['Motivo'].str.split(' - ', expand=True)[1]
df_desastre_df['Motivo'] = df_desastre_df['Motivo'].apply(lambda x: str(x).split(' e ')[0] if ' e ' in str(x) else str(x))
df_desastre_df['Motivo'] = df_desastre_df['Motivo'].apply(lambda x: str(x).split('(')[1].split(')')[0] if ' (' in str(x) else str(x))
df_desastre_df['Motivo'] = df_desastre_df['Motivo'].apply(lambda x: str(x).replace('Ciclone Extratropical', 'Ciclone').replace('None', 'Desastre Não Identificado'))

df_desastre_df = df_desastre_df.set_index('Registro')
df_desastre_df_sorted = df_desastre_df.sort_values('Mês de referência')



st.markdown(f'<h1 style="text-align: center;color: #000000;font-size:18px;">{f"Distribuição de Hipoclorito em {ano} para Municípios em Situação de Evento Adverso"}</h1>', unsafe_allow_html=True)
coluna1, coluna2, coluna3, coluna4 = st.columns(4)
coluna1.metric(f'Total de Solicitações em {ano} - Desastre', total_pedidos_desastre)
coluna2.metric(f'População Atendida (Estimada) em {ano} - Desastre', total_população_atendida)
coluna3.metric(f'Total de Frascos Distribuídos em {ano} - Desastre', df_desastre_df['Quantidade de Frascos Distribuídos'].sum())
coluna4.metric(f'Média de Frascos Distribuídos por Solicitação em {ano} - Desastre', int(round((df_desastre_df['Quantidade de Frascos Distribuídos'].sum()/total_pedidos_desastre),0)))

motivo_pivoted = pd.pivot_table(df_desastre_df_sorted, index='Motivo', values='Quantidade de Frascos Distribuídos',aggfunc="sum").reset_index()
motivo_pivoted_2 = df_desastre_df_sorted.groupby('Motivo').count()
motivo_pivoted_2 = motivo_pivoted_2.rename_axis('Motivo')
motivo_pivoted_2 = motivo_pivoted_2.reset_index()
motivo_pivoted_2 = motivo_pivoted_2.rename(columns={'Município':'Quantidade de Solicitações'})
motivo_pivoted_2 = motivo_pivoted_2[['Motivo','Quantidade de Solicitações']]
motivo_merge = pd.merge(motivo_pivoted, motivo_pivoted_2, on ='Motivo')

fig1_bar = px.bar(motivo_merge, x='Motivo', y='Quantidade de Frascos Distribuídos',
             hover_data=['Motivo','Quantidade de Frascos Distribuídos','Quantidade de Solicitações'], color='Quantidade de Solicitações', color_continuous_scale='Burg',
             height=600, width=700, title="Quantidade de Frascos Distribuídos (tamanho) e Número de Solicitações (cor) por Tipo de Desastre")

fig1_bar.update_coloraxes(colorbar={'orientation':'h','thickness':30},
                         colorbar_yanchor='bottom',
                         colorbar_y=-0.5) 

eventos_significativos = pd.pivot_table(df_desastre_df_sorted, index=['Mês de referência', 'Município'],values='Quantidade de Frascos Distribuídos',aggfunc="sum").reset_index()
eventos_significativos_gb = eventos_significativos.groupby('Mês de referência')['Município'].apply(lambda x: ', '.join(x)).reset_index()
eventos_significativos_gbx = eventos_significativos.groupby('Mês de referência').sum('Quantidade de Frascos Distribuídos').reset_index()
eventos_significativos_gb_gbx_merge = pd.merge(eventos_significativos_gb,eventos_significativos_gbx, on='Mês de referência')
eventos_significativos_gb_gbx_merge = eventos_significativos_gb_gbx_merge.rename(columns={'Município':'Municípios Atingidos'})

eventos_significativos2 = df_desastre_df_sorted.groupby('Mês de referência').count()
eventos_significativos2 = eventos_significativos2.rename_axis('Mês de referência')
eventos_significativos2 = eventos_significativos2.reset_index()
eventos_significativos2 = eventos_significativos2.rename(columns={'Município':'Quantidade de Eventos'})
eventos_significativos2 = eventos_significativos2[['Mês de referência', 'Quantidade de Eventos']]
eventos_significativos_merged = pd.merge(eventos_significativos_gb_gbx_merge, eventos_significativos2, on ='Mês de referência')

eventos_significativos_renamed = eventos_significativos_merged.rename(columns={'Mês de referência':'Mês de Referência','Quantidade de Eventos':'Quantidade de Solicitações'})
eventos_significativos_renamed = eventos_significativos_renamed.set_index('Mês de Referência')
eventos_significativos_renamed2 = eventos_significativos_renamed[['Municípios Atingidos','Quantidade de Frascos Distribuídos','Quantidade de Solicitações']]

eventos_significativos_renamed2_resetado = eventos_significativos_renamed2.reset_index()

dicionario_meses = {
    '01' : 'Janeiro',
    '02' : 'Fevereiro',
    '03' : 'Março',
    '04' : 'Abril',
    '05' : 'Maio',
    '06' : 'Junho',
    '07' : 'Julho',
    '08' : 'Agosto',
    '09' : 'Setembro',
    '10' : 'Outubro',
    '11' : 'Novembro',
    '12' : 'Dezembro'
}
eventos_significativos_renamed2_resetado['Mês de Referência'] = eventos_significativos_renamed2_resetado['Mês de Referência'].astype(str)
eventos_significativos_renamed2_resetado['Mês de Referência'] = eventos_significativos_renamed2_resetado['Mês de Referência'].map(dicionario_meses)

fig2_bar = px.bar(eventos_significativos_renamed2_resetado, x='Mês de Referência', y='Quantidade de Frascos Distribuídos',
             hover_data=['Mês de Referência','Municípios Atingidos','Quantidade de Frascos Distribuídos','Quantidade de Solicitações'],
             width=850, color='Quantidade de Solicitações', color_continuous_scale='Brwnyl',
             height=600, title="Quantidade de Frascos Distribuídos por Mês de Referência com Registro de Desastre")

fig2_bar.update_coloraxes(colorbar={'orientation':'h','thickness':30},
                         colorbar_yanchor='bottom',
                         colorbar_y=-0.5) 

with st.container():
    coluna_bar1,coluna_bar2  = st.columns(2)
    
    with coluna_bar1:
        fig1_bar
    
    with coluna_bar2:
        fig2_bar
        #st.dataframe(eventos_significativos_renamed2,height=225, use_container_width =True)       

st.dataframe(df_desastre_df_sorted[['CRS','Município','Motivo','Estimativa de Pop. Atendida','Quantidade de Frascos Distribuídos']], use_container_width =True)
