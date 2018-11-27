#!/bin/bash -eux

if   [[ $PACKER_BUILDER_TYPE =~ virtualbox-iso ]] || \
     [[ $PACKER_BUILDER_TYPE =~ amazon-ebs ]]; then

    echo "Set locale to en_US.utf8"

    localedef --list-archive | grep -a -v en_US.utf8 | xargs sudo localedef --delete-from-archive
    cp /usr/lib/locale/locale-archive{,.tmpl}
    build-locale-archive

fi
