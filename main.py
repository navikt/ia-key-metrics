from google.cloud.bigquery import Client
from datetime import datetime, timedelta

import plotly.graph_objs as go
import plotly.subplots as sp

import config


def load_data():
    bq_client = Client(project=config.PROJECT)
    return bq_client.query(query=config.SQL_QUERY).to_dataframe()


def calculate_key_metrics(data, startdato, sluttdato):
    data["målgruppe"] = (data.antall_ansatte > 1) & (data.antall_ansatte <= 50)
    data["opprettet_dato"] = data["opprettet"].dt.date

    data_intervall = data[(data.opprettet > startdato) & (data.opprettet <= sluttdato)]
    data_utenfor_intervall = data[(data.opprettet <= startdato)]

    # Antall brukere
    brukere_intervall = data_intervall.orgnr.unique().tolist()
    brukere_utenfor_intervall = data_utenfor_intervall.orgnr.unique().tolist()

    # Antall tilbakevendende brukere
    tilbakevendende_brukere = len(
        set(brukere_intervall).intersection(brukere_utenfor_intervall)
    )

    # Antall brukere i målgruppen
    brukere_målgruppen = data_intervall[data_intervall.målgruppe].orgnr.nunique()

    # Antall leverte IA-tjenester til målgruppen
    ia_tjenester_målgruppen = (
        data_intervall[data_intervall.målgruppe].drop_duplicates(
            ["orgnr", "opprettet_dato"]
        )
    ).shape[0]

    return tilbakevendende_brukere, brukere_målgruppen, ia_tjenester_målgruppen


def plot_key_metrics(data, antall_dager: int):
    sluttdato = datetime.now()
    startdato = sluttdato - timedelta(days=antall_dager)
    (
        tilbakevendende_brukere,
        brukere_målgruppen,
        ia_tjenester_målgruppen,
    ) = calculate_key_metrics(data, startdato, sluttdato)
    (
        ref_tilbakevendende_brukere,
        ref_brukere_målgruppen,
        ref_ia_tjenester_målgruppen,
    ) = calculate_key_metrics(
        data, startdato - timedelta(days=1), sluttdato - timedelta(days=1)
    )

    fig = sp.make_subplots(
        rows=1,
        cols=3,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
        ],
    )

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=tilbakevendende_brukere,
            delta={"reference": ref_tilbakevendende_brukere},
            number={"valueformat": ", g"},
            title={
                "text": "<br><span style='font-size:0.7em;color:gray'>{0}</span>".format(
                    "Tilbakevendende brukere"
                )
            },
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=brukere_målgruppen,
            delta={"reference": ref_brukere_målgruppen},
            number={"valueformat": ", g"},
            title={
                "text": "<br><span style='font-size:0.7em;color:gray'>{0}</span>".format(
                    "Brukere i målgruppen"
                )
            },
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=ia_tjenester_målgruppen,
            delta={"reference": ref_ia_tjenester_målgruppen},
            number={"valueformat": ", g"},
            title={
                "text": "<br><span style='font-size:0.7em;color:gray'>{0}</span>".format(
                    "Leverte IA-tjenester til målgruppen"
                )
            },
        ),
        row=1,
        col=3,
    )

    return fig
