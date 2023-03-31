#!/bin/bash

quarto render index.qmd

curl -X PUT -F file=@index.html \
    https://${NADA_HOST}/quarto/update/${QUARTO_ID} \
    -H "Authorization:Bearer ${TEAM_TOKEN}"
