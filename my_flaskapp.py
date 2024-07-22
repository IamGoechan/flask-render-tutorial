import pandas as pd
from flask import Flask
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Excelファイルの読み込み
df = pd.read_csv("予約一覧20240717.csv", header=1)
df.rename(columns={'住所': 'address'}, inplace=True)

# 都道府県名を抽出する関数
def extract_prefecture(address):
    if pd.isnull(address):
        return None
    prefectures = [
        '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
        '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
        '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
        '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
        '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
        '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
        '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
    ]
    for prefecture in prefectures:
        if prefecture in address:
            return prefecture
    return None

# 住所から都道府県名を抽出
df['prefecture'] = df['address'].apply(extract_prefecture)
prefecture_counts = df['prefecture'].dropna().value_counts()

# '流入経路' カラムの値の頻度を集計
channel_counts = df['流入経路'].value_counts(dropna=False)

# 'リードタイム' 列の計算
df['申込受付日'] = pd.to_datetime(df['申込受付日'])
df['チェックイン日'] = pd.to_datetime(df['チェックイン日'])
df['リードタイム'] = (df['申込受付日'] - df['チェックイン日']).dt.days

# Flask アプリケーションの設定
server = Flask(__name__)

# Dash アプリケーションの設定
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.CYBORG])

# アプリケーションのレイアウト
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("割烹旅館ゆめさき様_CRMデータ一覧", className="text-center mb-4"), width=6)),

    dbc.Row([
        dbc.Col([
            html.H2("都道府県別住所頻度グラフ"),
            dcc.Graph(id='prefecture-graph')
        ], width=5)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H2("流入経路の割合"),
            dcc.Graph(id='channel-pie-chart')
        ], width=5)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H2("リードタイムグラフ"),
            dcc.Graph(id='lead-time-bar-graph')
        ], width=5)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H2("リードタイムの散布図"),
            dcc.Graph(id='lead-time-scatter-plot')
        ], width=5)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H2("プラン名別人気度"),
            dcc.Graph(id='plan-popularity-graph')
        ], width=5)
    ], className="mb-4")
], fluid=True)

# グラフのコールバック関数
@app.callback(
    [Output('prefecture-graph', 'figure'),
     Output('channel-pie-chart', 'figure'),
     Output('lead-time-bar-graph', 'figure'),
     Output('lead-time-scatter-plot', 'figure'),
     Output('plan-popularity-graph', 'figure')],
    [Input('prefecture-graph', 'id')]
)
def update_graph(_):
    # 都道府県別住所頻度グラフ
    prefecture_fig = go.Figure(
        data=[go.Bar(
            x=prefecture_counts.index,
            y=prefecture_counts.values
        )],
        layout=go.Layout(
            title='都道府県別住所頻度',
            xaxis_title='都道府県',
            yaxis_title='頻度'
        )
    )

    # 流入経路の割合
    channel_fig = go.Figure(
        data=[go.Pie(
            labels=channel_counts.index,
            values=channel_counts.values,
            hole=.3
        )],
        layout=go.Layout(
            title='流入経路の割合'
        )
    )

    # リードタイムの棒グラフ
    bar_fig = go.Figure(
        data=[go.Bar(
            x=df.index,
            y=df['リードタイム'],
            text=df['リードタイム'],
            textposition='auto'
        )],
        layout=go.Layout(
            title='リードタイムの棒グラフ',
            xaxis_title='Index',
            yaxis_title='Lead Time'
        )
    )

    # リードタイムの散布図
    scatter_fig = go.Figure(
        data=[go.Scatter(
            x=df.index,
            y=df['リードタイム'],
            mode='markers',
            marker=dict(size=10, color='rgba(219, 64, 82, 0.8)', line=dict(width=2, color='rgba(219, 64, 82, 0.8)'))
        )],
        layout=go.Layout(
            title='リードタイムの散布図',
            xaxis_title='Index',
            yaxis_title='Lead Time'
        )
    )

    # プラン名別人気度
    plan_counts = df['プラン名'].value_counts()
    plan_fig = go.Figure(
        data=[go.Bar(
            x=plan_counts.index,
            y=plan_counts.values,
            text=plan_counts.values,
            textposition='auto'
        )],
        layout=go.Layout(
            title='プラン名別人気度',
            xaxis_title='プラン名',
            yaxis_title='頻度'
        )
    )

    return prefecture_fig, channel_fig, bar_fig, scatter_fig, plan_fig

# サーバーを起動
if __name__ == '__main__':
    app.run_server(debug=True)
