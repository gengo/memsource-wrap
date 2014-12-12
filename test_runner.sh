#! /bin/bash
EXIT_STATUSES=()

pep8 .
EXIT_STATUSES=(${EXIT_STATUSES[@]} $?)

nosetests --with-coverage --cover-package=memsource --rednose
EXIT_STATUSES=(${EXIT_STATUSES[@]} $?)

for (( I = 0; I < ${#EXIT_STATUSES[@]}; I++ )) do
    if test ${EXIT_STATUSES[$I]} -ne 0; then
        exit 1
    fi
done

exit 0
