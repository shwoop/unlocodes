# README

## Fetching data

### UNLOCODES
run `./get_codes.sh` to populate the `/data` folder with the 2019-01 unlocode
export.

### Ports
To grab the Ports information, with a user who can access the ptrac database
via `psql purpletrac` run `./get_ports.sh` to generat a csv of ptrac ports
`data/ptrac_ports.csv`.

## Analysis
Run `python unlocodes.py` to launch an ipython interpreter with access to a
number of python dataframes built from the extracted data.

All have verbose names and are available by checking `locals()`.

## Notes
### The function column uses flags to indicate:

0	A value "0" in the first position specifies that the functional use of a location is not known and is to be specified.

1	Specifies that the location is a Port, as defined in UN/ECE Recommendation 16.

2	Specifies that the location is a Rail terminal.

3	Specifies that the location is a Road terminal.

4	Specifies that the location is an Airport.

5	Specifies that the location is a Postal exchange office.

6	Value reserved for multimodal functions, ICDs etc.

7	Value reserved for fixed transport functions (e.g. oil platform).

B	Specifies that the location is Border crossing.

### Status codes:
AA: Approved by competent national government agency

AC: Approved by Customs Authority

AF: Approved by national facilitation body

AI: Code adopted by international organisation (IATA or ECLAC)

AM: Approved by the UN/LOCODE Maintenance Agency

AQ: Entry approved, functions not verified

AS: Approved by national standardisation body

RL: Recognised location - Existence and representation of location name confirmed by check against nominated gazetteer or other reference work

RN: Request from credible national sources for locations in their own country

RQ: Request under consideration

UR: Entry included on user's request; not officially approved

RR: Request rejected

QQ: Original entry not verified since date indicated

XX: Entry that will be removed from the next issue of UN/LOCODE

### Date format

The date the location was added or updated: 0207 is July 2002, 9501 is January 1995, etc.
