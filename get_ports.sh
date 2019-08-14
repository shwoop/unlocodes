#!/usr/bin/env bash

mkdir -fp data &>/dev/null

psql test_purpletrac <<EOF
\copy ps_voyage_port to data/test_port.csv (header true, format CSV)
\copy ps_voyage_country to data/test_country.csv (header true, format CSV)
\copy ps_voyage_isocountry to data/test_isocountry.csv (header true, format CSV)
EOF
