#!/bin/bash

mkdir -fp data &>/dev/null
SQL='select code from ps_voyage_port order by code;'
psql purpletrac -q -P 'tuples_only' -c "$SQL" | \
    tr -d ' ' >data/ptrac_ports.csv && \
    echo SUCCESS || \
    echo FAILURE
