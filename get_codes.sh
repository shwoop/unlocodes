#!/bin/bash

TMP=mktemp
curl https://www.unece.org/fileadmin/DAM/cefact/locode/loc191csv.zip -o $TMP &>/dev/null &&
    unzip $TMP -d data/ &>/dev/null ||
    echo Unable to download file
rm -f $TMP &>/dev/null &&
    echo success ||
    echo failure
