#!/bin/bash

# Disabling following errors:
# D213: Multi-line docstring summary should start at the second line
# D407: Missing dashed underline after section
# D413: Missing blank line after last section ('Keyword Arguments')
# W0511: TODO warnings
# C0111: Missing module docstring
# D100: Missing docstring in public module
# E0602: Undefined variable (as "salt is not defined")
# C0103: Constant name "dry_run" doesn't conform to UPPER_CASE naming style
# C0330 Wrong hanging indentation before block (add 4 spaces) > incompatibily with Black

PYLAMA_IGNORE="D213,D407,D413,W0511,C0111,D100,E0602,C0103,C0330"

ret=0

for f in `find . -type f -iname "*.sls"`
do
    header=`head -1 $f`
    if [ "$header" == "#!py" ]
    then
        pylama --force $f -i $PYLAMA_IGNORE
        ret=$(($ret+$?))
        black $f --check
        ret=$(($ret+$?))
    fi
done

exit $ret
