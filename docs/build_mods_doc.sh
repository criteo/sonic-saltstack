#!/bin/sh

MOD_DIRS='_states _modules _utils'

build_stubs() {
    path="../$1"
    outdir="ref/$1"
    sphinx-apidoc --separate -o "$outdir" $path/
}

main() {
    for mod in $MOD_DIRS
    do
        build_stubs $mod
    done
}

main "$@"
