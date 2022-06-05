#!/bin/bash

function log() {
    echo $1 >> ${logpath}
}

function script_init() {
    # GENERAL PARAMS
    script_path="${BASH_SOURCE[0]}"
    script_dir="$(dirname "$script_path")"
    script_name="$(basename "$script_path")"
    logpath="./log.txt"

    # CALL PARAMS
    key_file_path="/home/borsu/Documents/cotizatii/Cotizatii/client_key.json"
    file_name="Cotizatii_automat"

    # SCIPT PARAMS
    python_script_path="/home/borsu/Documents/cotizatii/Cotizatii/subscription_precessor.py"
    python_virtualenv_path="/home/borsu/Documents/cotizatii/Cotizatii/virtualenv"

    source "${python_virtualenv_path}/bin/activate"

    log " "
    log "Script has been initialised at $(date)"
}

function catch_params() {
    [[ -z $id ]] && log "Cannot run withoud id" && exit 1
    [[ -z $surname ]] && log "Cannot run withoud surname" && exit 1
    [[ -z $given ]] && log "Cannot run withoud given_name" && exit 1
    [[ -z $pay ]] && log "Cannot run withoud pay_for" && exit 1
}

function build_call() {
    log "Running python3 subscription_precessor.py
        --key-file ${key_file_path} \
        --file-name ${file_name} \
        --id-oncr ${id} \
        --surname ${surname} \
        --given-name ${given} \
        --pay-for ${pay} \
        --update_cotizatie"

    python3 subscription_precessor.py \
        --key-file ${key_file_path} \
        --file-name ${file_name} \
        --id-oncr ${id} \
        --surname ${surname} \
        --given-name ${given} \
        --pay-for ${pay} \
        --update_cotizatie
}

function main() {
    script_init
    catch_params
    build_call
}


if ! (return 0 2> /dev/null); then
    main "$@"
fi

# curl -v -XPOST http://localhost:8080/webhook_wrapper.sh?id=MB3501\&surname=Borsu\&given=Mihai\&pay="2021_Oct-2022_Sept"
