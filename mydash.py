from dash import Dash, html, dcc, callback, Output, Input, dash_table
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from KakaoTalkAnalysis.preprocessor import GeneralPreproc, SessionPreproc
from KakaoTalkAnalysis.eda import EdaController
from KakaoTalkAnalysis.stats import StatsController
from KakaoTalkAnalysis.relationship import RelationController

################################################################
raw_df = pd.read_csv("./chat.csv")

general_preproc = GeneralPreproc(raw_df)
df = general_preproc(min_chat=300)

session_preproc = SessionPreproc(df)
session_df = session_preproc.cluster_bsd_session()

relation_controller = RelationController(session_df)
score_df = relation_controller.format_score(
    relation_controller.calc_abs_score(), relation_controller.calc_rel_score()
)
################################################################

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1("회기농장 채팅분석", style={"textAlign": "center"}),
        dcc.Dropdown(
            id="first-dropdown",
            options=[
                {"label": opt, "value": opt}
                for opt in [
                    "데이터 개괄",
                    "통계적 분석",
                    "관계도 분석",
                    "감정 분석",
                ]
            ],
            value="데이터 개괄",
        ),
        html.Br(),
        dcc.Dropdown(id="second-dropdown"),
        html.Div(id="display-container"),
    ]
)


################################################################
@app.callback(
    Output("second-dropdown", "options"),
    Input("first-dropdown", "value"),
)
def set_options(selected_value):
    if selected_value == "데이터 개괄":
        return []
    elif selected_value == "통계적 분석":
        return [
            {"label": str(num), "value": str(num)}
            for num in range(1, len(df.User.unique()))
        ]
    elif selected_value == "관계도 분석":
        return [{"label": user, "value": user} for user in df.User.unique()]

    elif selected_value == "감정 분석":
        return []


################################################################
def get_eda_df(df):
    eda_df = pd.DataFrame([EdaController().info_dict(df)]).T
    eda_df = eda_df.reset_index()
    eda_df.columns = ["feature", "value"]
    return eda_df


def get_ratio_df(df, top_n):
    stats_controller = StatsController(df)
    ucr_df = stats_controller.user_chat_ratio(top_n).reset_index(
        names="user"
    )  # 사용자별 채팅 비율
    ulr_df = stats_controller.user_len_ratio(top_n).reset_index(
        names="user"
    )  # 사용자별 채팅 길이 비율
    return (ucr_df, ulr_df)


@app.callback(
    Output("display-container", "children"),
    [Input("first-dropdown", "value"), Input("second-dropdown", "value")],
)
def update_display(first_selection, second_selection):
    if first_selection == "데이터 개괄":
        eda_df = get_eda_df(df)
        return dash_table.DataTable(
            data=eda_df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in eda_df.columns],
            page_size=10,  # 한 페이지에 표시할 행의 수
        )
    elif first_selection == "통계적 분석" and second_selection:
        top_n = int(second_selection)
        ucr_df, ulr_df = get_ratio_df(df, top_n)

        # 파이 차트 생성
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "domain"}, {"type": "domain"}]],
            subplot_titles=["사용자별 채팅 비율", "사용자별 채팅량 비율"],
        )

        fig.add_trace(
            go.Pie(
                labels=ucr_df["user"], values=ucr_df["ratio"], name="채팅 비율"
            ),
            1,
            1,
        )
        fig.add_trace(
            go.Pie(
                labels=ulr_df["user"],
                values=ulr_df["ratio"],
                name="채팅 길이 비율",
            ),
            1,
            2,
        )

        fig.update_traces(hole=0.4, hoverinfo="label+percent+name")
        fig.update_layout(
            title_text=f"상위 {top_n} 사용자별 채팅 및 채팅 길이 비율"
        )
        return dcc.Graph(figure=fig)

    elif first_selection == "관계도 분석" and second_selection:
        user = str(second_selection)
        _score_df = pd.concat(
            [
                score_df[score_df["subject"] == user],
                score_df[score_df["subject"] != user]
                .groupby("subject")
                .apply(lambda x: x.nlargest(3, "score"))
                .reset_index(drop=True),
            ]
        )
        G = create_networkx_graph(_score_df)
        fig = plotly_networkx(G)
        return dcc.Graph(figure=fig)
    elif first_selection == "감정 분석":
        sentimental_df = get_sentimental_df(session_df)
        return dash_table.DataTable(
            data=sentimental_df.to_dict("records"),
            columns=[
                {"name": i, "id": i}
                for i in sentimental_df.columns
            ],
            sort_action="native"
        )


################################################################
import networkx as nx


def create_networkx_graph(df):
    G = nx.Graph()

    for idx, row in df.iterrows():
        G.add_edge(row["subject"], row["object"], weight=row["score"])

    return G


def plotly_networkx(G):
    pos = nx.spring_layout(G)  # 노드의 위치를 계산

    edge_x = []
    edge_y = []
    edge_width = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.0, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=10,
            color=[],
            line_width=2,
        ),
    )

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(
            f"{adjacencies[0]} (# of connections: {len(adjacencies[1])})"
        )

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=0),
        ),
    )

    return fig


################################################################
def get_sentimental_df(session_df):
    from KakaoTalkAnalysis import SentimentalController
    import pickle

    with open("./sentimental_dict.pkl", "rb") as f:
        sentimental_dict = pickle.load(f)

    sentimental_ctr = SentimentalController(session_df, sentimental_dict)

    sentimental_total_ratio = sentimental_ctr.calc_total_ratio()
    sentimental_user_ratio = sentimental_ctr.calc_user_ratio()
    sentimental_df = sentimental_user_ratio.div(sentimental_total_ratio)
    sentimental_df = sentimental_df.apply(lambda x : round(x,3))
    sentimental_df = sentimental_df.reset_index()
    return sentimental_df


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8050, debug=True)
    # app.run_server(debug=True)
