# ia-key-metrics





## Troubleshoot

_Problem:_ Advarsel i output fra Quarto som leser
```
our application has authenticated using end user credentials from Google Cloud SDK without a quota project. You might receive a "quota exceeded" or "API not enabled" error.
```
_Fix_: Kjør
```
gcloud auth application-default set-quota-project teamia-prod-df3d
```