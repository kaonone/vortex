FALSE_POSITIVE_WARNIGNS=21
FOUND_WARNINGS=`grep "\d+ result" -Po ./slither_report.txt | sed 's/ result//g'`

echo "False positive warnings: $FALSE_POSITIVE_WARNIGNS"
echo "Slither has found $FOUND_WARNINGS issues"
if [ $FOUND_WARNINGS -gt $FALSE_POSITIVE_WARNIGNS ]; then echo "$FOUND_WARNINGS issues exceeds limit" >&2; exit 1; fi
if [ $FALSE_POSITIVE_WARNIGNS -gt $FOUND_WARNINGS ]; then echo "False positives number should be reduced"; fi
