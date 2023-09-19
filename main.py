from google.cloud.bigquery import Client
from datetime import datetime, timedelta

import plotly.graph_objs as go

import config


def load_data():
    bq_client = Client(project=config.PROJECT)
    return bq_client.query(query=config.SQL_QUERY).to_dataframe()


def calculate_key_metrics(data_raw, startdato, sluttdato):
    data = (
        data_raw[data_raw.kilde_applikasjon == "FOREBYGGINGSPLAN"]
        .assign(opprettet_date=data_raw["opprettet"].dt.date)
        .sort_values(by=["orgnr", "opprettet"])
        .drop_duplicates(subset=["orgnr", "opprettet_date"])
    )
    count = data[
        (data.opprettet > startdato) & (data.opprettet <= sluttdato)
    ].orgnr.value_counts()

    antall_åpnet_kort = count.count()
    antall_åpnet_kort_flere_dager = (count >= 2).sum()

    return antall_åpnet_kort, antall_åpnet_kort_flere_dager


def plot_key_metrics(data, antall_dager: int):
    sluttdato = datetime.now()
    startdato = sluttdato - timedelta(days=antall_dager)
    antall_åpnet_kort, antall_åpnet_kort_flere_dager = calculate_key_metrics(
        data, startdato, sluttdato
    )

    fig = make_key_result_indicator(
        antall_åpnet_kort,
        300,
        formater_tittel(
            "Antall virksomheter som har interagert med siden",
            "i løpet av de siste 30 dagene",
        ),
    )
    fig.show()

    fig = make_key_result_indicator(
        antall_åpnet_kort_flere_dager,
        30,
        formater_tittel(
            "Antall virksomheter som har interagert med siden flere dager",
            "i løpet av de siste 30 dagene",
        ),
    )
    fig.show()


def make_key_result_indicator(verdi, mål, tittel):
    fig = go.Figure()
    fig.add_trace(make_gauge(verdi, mål))

    fig.update_layout(
        height=300,
        width=850,
        title={
            "text": tittel,
            "x": 0.5,
            "y": 1,
        },
    )
    return fig


def make_gauge(verdi, mål):
    return go.Indicator(
        mode="number+gauge+delta",
        gauge={
            "shape": "bullet",
            "axis": {"range": [None, mål * 1.2]},
            "threshold": {
                "line": {"color": "red", "width": 2},
                "thickness": 0.75,
                "value": mål,
            },
            "bar": {"thickness": 0.5},
        },
        delta={"reference": mål},
        value=verdi,
        number={"valueformat": ", g", "font_size": 85},
    )


def formater_tittel(overskrift, undertekst):
    return f"<br><span style='font-size:1em;color:gray'>{overskrift}<br><span style='font-size:0.7em;color:gray'>{undertekst}"
