#!/usr/bin/env bash

PY="/usr/bin/python3"
PP="/usr/bin/pip3"
DC="/usr/bin/docker"


function check {
    echo "Checking the need command for library ..."
    CMD=($PY $DC $PP)
    for i in "${CMD[@]}"
    do
        if [ -e "${i}" ]
        then
            echo "${i} ... OK"
        else
            echo "${i} ... FAILED"
            echo "${i} command not found"
            exit
        fi
    done
    echo "DONE"
}

function template {

    HOST=template/host/Dockerfile
    ONOS=template/onos/Dockerfile
    WHITEBOX=template/whitebox/Dockerfile

    echo "Installing docker devices ..."
    echo "* HOST computer models"
    $DC build --rm -f ${HOST} -t vsdn/host:latest --no-cache=true . &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "Cannot install host models in docker"
        exit
    fi
    echo "* ONOS network controller models"
    $DC build --rm -f ${ONOS} -t vsdn/onos:latest --no-cache=true . &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "Cannot install onos models in docker"
        exit
    fi
    echo "* WHITEBOX network switch models"
    $DC build --rm -f ${WHITEBOX} -t vsdn/whitebox:latest --no-cache=true . &> /dev/null
    #&> /dev/null
    if [ $? -ne 0 ]
    then
        echo "Cannot install whitebox models in docker"
        exit
    fi
    echo "DONE"

}

function library {
    SUDO="/usr/bin/sudo"
    echo "Installing vSDNAgent python library ..."
    ${SUDO} ${PP} install . &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "Cannot install library "
        exit
    fi
    echo "DONE"
}

function all {
    check
    template
    library
}

case $1 in
    check)
        check
        ;;
    template)
        template
        ;;
    library)
        library
        ;;
    all)
        all
        ;;
    *)
        echo "option not found"
        echo "please use the following options:"
        echo "  [check] --------- for checking command necessaries."
        echo "  [template] ------ for installing devices docker."
        echo "  [library] ------- for installing only library."
        echo "  [all] ----------- for executing all options before"
esac

