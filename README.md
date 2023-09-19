# ia-key-metrics

## Pre requisites

Installer quarto ved å følge guiden [på quarto sine nettsider](https://quarto.org/docs/get-started/).

Installer [python3.11](https://www.python.org/downloads/).

Som en god praksis, opprett et virtuelt pythonmiljø i root til prosjektet:\
`python3.11 -m venv env`\
`source env/bin/activate`

Installer requirements `pip3 install -r requirements.txt`.

Installer [black](https://pypi.org/project/black/), en python-kode formatter, med `pip3 install black`.

## Lokal utvikling

Logg inn i gcp med `gcloud auth application-default login`.

Kjør opp quarto i preview mode med følgende kommando:
`quarto render index.qmd`

## Troubleshoot

_Problem:_ Advarsel i output fra Quarto som leser
```
our application has authenticated using end user credentials from Google Cloud SDK without a quota project. You might receive a "quota exceeded" or "API not enabled" error.
```
_Fix_: Kjør
```
gcloud auth application-default set-quota-project teamia-prod-df3d
```