#!/bin/bash -eux

if [[ $PACKER_BUILDER_TYPE =~ amazon-ebs ]] || \
   [[ $PACKER_BUILDER_TYPE =~ virtualbox-iso ]]; then

    echo "Remove machine-id from the box image"
    rm -f /etc/machine-id

    ##if rpm -q --whatprovides kernel | grep -Fqv "$(uname -r)"; then
    ##    rpm -q --whatprovides kernel | grep -Fv "$(uname -r)" | xargs yum -y autoremove
    ##fi

    yum clean all
    #rm -rf /var/cache/yum
    yum history new
    truncate -c -s 0 /var/log/yum.log
    
    #echo "Set locale to en_US.utf8"
    #localedef --list-archive | grep -a -v en_US.utf8 | xargs localedef --delete-from-archive
    #cp /usr/lib/locale/locale-archive{,.tmpl}
    #build-locale-archive


    echo "Clear  temporary files used to build box"
    rm -rf /tmp/*
    rm -rf /var/tmp/*

    if [[ -d /root/.r10k ]]; then 
      rm -rf /root/.r10k
    fi

    echo "Rebuild RPM DB"
    rpmdb --rebuilddb
    rm -f /var/lib/rpm/__db*


    echo 'Clear out swap and disable until reboot'
    set +e
    swapuuid=$(/sbin/blkid -o value -l -s UUID -t TYPE=swap)
    case "$?" in
        2|0) ;;
        *) exit 1 ;;
    esac
    set -e
    if [ "x${swapuuid}" != "x" ]; then
        # Whiteout the swap partition to reduce box size
        # Swap is disabled till reboot
        swappart=$(readlink -f /dev/disk/by-uuid/$swapuuid)
        /sbin/swapoff "${swappart}"
        dd if=/dev/zero of="${swappart}" bs=1M || echo "dd exit code $? is suppressed"
        # Flush the disk cache
        sync

        /sbin/mkswap -U "${swapuuid}" "${swappart}"
    fi

    #echo "Rebooting..."
    #reboot
    #sleep 30

elif [[ $PACKER_BUILDER_TYPE =~ docker ]]; then

    echo "Clear  temporary files used to build box"
    #rm -rf /tmp/*
    #rm -rf /var/tmp/*
fi
