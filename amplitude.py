import requests
import pandas as pd


def hent_antall_besøkende_siste_30_dager():
    response = requests.get(
        "https://reops-proxy.intern.nav.no/amplitude/api/3/chart/e-czvqr8g/query"
    )

    if not response.ok:
        print(response)
        return "NaN"

    body = response.json()

    besøkende = body["data"]["series"][0]
    datoer = pd.to_datetime(body["data"]["xValues"])

    dagens_dato = pd.to_datetime("today")
    startdato = dagens_dato - pd.DateOffset(days=30)

    siste_30_dager = pd.DataFrame(data=besøkende, index=datoer)["value"][startdato:dagens_dato]

    return siste_30_dager.sum()


if __name__ == '__main__':
    print(hent_antall_besøkende_siste_30_dager())


