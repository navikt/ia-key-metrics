from google.cloud.bigquery import Client
from datetime import datetime, timedelta

import plotly.graph_objs as go
import plotly.subplots as sp

import config


def load_data():
    bq_client = Client(project=config.PROJECT)
    return bq_client.query(query=config.SQL_QUERY).to_dataframe()


def calculate_key_metrics(data_raw, startdato, sluttdato):
    data = (
            data_raw[data_raw.kilde_applikasjon=="FOREBYGGINGSPLAN"]
            .assign(opprettet_date=data_raw["opprettet"].dt.date)
            .sort_values(by=["orgnr", "opprettet"])
            .drop_duplicates(subset=["orgnr", "opprettet_date"])
        )
    count = data[(data.opprettet > startdato) & (data.opprettet <= sluttdato)].orgnr.value_counts()

    antall_åpnet_kort = count.count()
    antall_åpnet_kort_flere_dager = (count>=2).sum()

    return antall_åpnet_kort, antall_åpnet_kort_flere_dager


def plot_key_metrics(data, antall_dager: int):
    sluttdato = datetime.now()
    startdato = sluttdato - timedelta(days=antall_dager)
    antall_åpnet_kort, antall_åpnet_kort_flere_dager = calculate_key_metrics(data, startdato, sluttdato)

    fig = sp.make_subplots(
        rows=2,
        cols=1,
        specs=[
            [{"type": "indicator"}], [{"type": "indicator"}],
        ],
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=antall_åpnet_kort,
            number={"valueformat": ", g"},
            title={
                "text": "<br><span style='font-size:0.7em;color:gray'>{0}</span>".format(
                    "Antall virksomheter som har åpnet panel"
                )
            },
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Indicator(
            mode="number+gauge+delta",
            gauge = {'shape': "bullet"},
            delta = {'reference': 50},
            value=antall_åpnet_kort_flere_dager,
            number={"valueformat": ", g"},
            title={
                "text": "<br><span style='font-size:0.7em;color:gray'>{0}</span>".format(
                    "Antall virksomheter som har åpnet panel flere dager"
                )
            },
        ),
        row=2,
        col=1,
    )
    return fig


def plot_frequency_forebyggingsplan(data_raw):
    data = (
        data_raw[data_raw.kilde_applikasjon=="FOREBYGGINGSPLAN"]
        .assign(opprettet_date=data_raw["opprettet"].dt.date)
        .sort_values(by=["orgnr", "opprettet"])
        .drop_duplicates(subset=["orgnr", "opprettet_date"])
    )

    idag = datetime.now()
    count = data[data.opprettet > idag - timedelta(days=30)].orgnr.value_counts()

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=count))
    fig.update_layout(
        height=400,
        width=500,
        title="Antall dager virksomheter brukte planen",
        xaxis_title="Antall dager",
        yaxis_title="Antall virksomheter",
    )
    return fig