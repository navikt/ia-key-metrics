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

    text_format = "<br><span style='font-size:1em;color:gray'>{0}<br><span style='font-size:0.7em;color:gray'>{1}"

    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=antall_åpnet_kort,
            number={"valueformat": ", g", 'font_size': 85},
        ),
    )
    fig.update_layout(
        height=200,
        width=850,
        title = {
            'text': text_format.format(
                "Antall virksomheter som har åpnet panel",
                "i løpet av de siste 30 dagene"
            ),
            'x': 0.5,
            'y': 1,
        }
    )
    fig.show()

    mål = 50
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            mode="number+gauge+delta",
            gauge = {
                'shape': "bullet",
                'axis': {'range': [None, mål*1.2]},
                'threshold': {
                    'line': {'color': "red", 'width': 2},
                    'thickness': 0.75,
                    'value': mål
                },
                'bar': {'thickness': 0.5},
            },
            delta = {'reference': mål},
            value=antall_åpnet_kort_flere_dager,
            number={"valueformat": ", g", 'font_size': 85},
        ),
    )
    fig.update_layout(
        height=250,
        width=850,
        title = {
            'text': text_format.format(
                "Antall virksomheter som har åpnet panel flere dager",
                "i løpet av de siste 30 dagene"
            ),
            'x': 0.5,
            'y': 1,
        }
    )
    fig.show()
