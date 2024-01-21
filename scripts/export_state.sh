#!/bin/bash

INI_FILE=$1
STAGE=$2
PLATFORM=$3
OUTPUT_FILE=statevars.sh

awk -v stage="[$STAGE]" -v out="$OUTPUT_FILE" '
BEGIN {flag=0}
$0 ~ stage {flag=1; next}
/^\[/ && flag {flag=0}
flag && NF >= 2 {
    if (platform == "ado") {
        print $1 "=" $2 > out
        print "export " $1 "=" $2 >> out
        print "echo \"##vso[task.setvariable variable="$1"]"$2"\"" >> out
    } else if (platform == "github") {
        print $1"="$2" >> $GITHUB_ENV"
    }
}
' "$INI_FILE"
