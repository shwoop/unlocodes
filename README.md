# README

## Fetching data

run `./get_codes.sh` to populate the `/data` folder with the 2019-01 unlocode
export.

## Analysis

TODO

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
