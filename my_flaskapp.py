import pandas as pd
import re
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# CSVファイルの読み込み
df=pd.read_csv("予約一覧20240717.csv")
df = pd.read_csv(df)

# カラムのリネーム
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

# NaNの値を無視して集計
prefecture_counts = df['prefecture'].dropna().value_counts()
print(prefecture_counts)




# Dashアプリケーションの設定
app = dash.Dash(__name__)

# アプリケーションのレイアウト
app.layout = html.Div(children=[
    html.H1(children='都道府県別住所頻度グラフ'),
    dcc.Graph(
        id='prefecture-graph',
        figure={
            'data': [
                go.Bar(
                    x=prefecture_counts.index,
                    y=prefecture_counts.values
                )
            ],
            'layout': {
                'title': '都道府県別住所頻度'
            }
        }
    )
])

# サーバーを起動
if __name__ == '__main__':
    app.run_server(debug=True)
