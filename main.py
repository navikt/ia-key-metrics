from google.cloud.bigquery import Client
from datetime import datetime, timedelta

import plotly.graph_objs as go
import plotly.subplots as sp

import config
from amplitude import hent_antall_besøkende_siste_30_dager


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
    antall_dager_per_orgnr = data[
        (data.opprettet > startdato) & (data.opprettet <= sluttdato)
    ].orgnr.value_counts()

    antall_åpnet_kort = antall_dager_per_orgnr.count()
    antall_åpnet_kort_flere_dager = (antall_dager_per_orgnr >= 2).sum()

    return antall_åpnet_kort, antall_åpnet_kort_flere_dager


def calculate_repeated_key_metrics(
    data_raw,
    startdato,
    sluttdato,
    minimum_days_between_visits=30,
    kilde_applikasjon="FOREBYGGINGSPLAN",
):
    applikasjon_data = data_raw[
        data_raw.kilde_applikasjon == kilde_applikasjon
    ].sort_values(by=["opprettet"])
    datofiltrert_data = applikasjon_data[
        (applikasjon_data.opprettet > startdato)
        & (applikasjon_data.opprettet <= sluttdato)
    ]
    only_duplicated_data = datofiltrert_data[
        datofiltrert_data.duplicated("orgnr", keep=False)
    ]

    first_date_set = only_duplicated_data.drop_duplicates(
        subset=["orgnr"], keep="first"
    )
    last_date_set = only_duplicated_data.drop_duplicates(subset=["orgnr"], keep="last")

    combined_set = first_date_set.merge(last_date_set, on="orgnr")
    diffed_set = combined_set.assign(
        diff=(combined_set["opprettet_y"] - combined_set["opprettet_x"])
    )

    filtered_set = diffed_set[
        diffed_set["diff"] > timedelta(days=minimum_days_between_visits)
    ]

    return filtered_set.orgnr.size


def plot_key_metrics(data):
    now = datetime.now()
    antall_åpnet_kort, antall_åpnet_kort_flere_dager = calculate_key_metrics(
        data, now - timedelta(days=30), now
    )
    antall_brukt_med_måneds_mellomrom = calculate_repeated_key_metrics(
        data, now - timedelta(days=365), now
    )

    make_key_metric_indicator(
        antall_åpnet_kort,
        300,
        formater_tittel(
            "Antall virksomheter som har interagert med siden",
            "i løpet av de siste 30 dagene",
        ),
    ).show()

    make_key_metric_indicator(
        antall_åpnet_kort_flere_dager,
        30,
        formater_tittel(
            "Antall virksomheter som har interagert med siden flere dager",
            "i løpet av de siste 30 dagene",
        ),
    ).show()
    make_key_metric_indicator(
        antall_brukt_med_måneds_mellomrom,
        100,
        formater_tittel(
            "Antall virksomheter som har gjort noe med minst 30 dager fra første til siste hendelse",
            "i løpet av de siste 365 dagene",
        ),
    ).show()

    sp.make_subplots(
        rows=2,
        cols=1,
        specs=[
            [{"type": "indicator"}], [{"type": "indicator"}],
        ],
    ).add_trace(
        go.Indicator(
            mode="number",
            value=hent_antall_besøkende_siste_30_dager(),
            # number={"valueformat": ", g"},
            title={
                "text": "<br><span style='font-size:0.7em;color:gray'>{0}</span>".format(
                    "Antall besøkende siste 30 dager"
                )
            },
        ),
        row=1,
        col=1,
    ).show()


def make_key_metric_indicator(verdi, mål, tittel):
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
