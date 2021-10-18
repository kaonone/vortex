FOUND_WARNINGS=`grep "failed" -Po ./echidna_report.txt`

if [ ! -z "$FOUND_WARNINGS" ]; then echo "Echidna testing failed. Check the report." >&2; exit 1; fi
