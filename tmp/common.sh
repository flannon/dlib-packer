#!/bin/#!/usr/bin/env bash

caller_id () {
  export AWS_CALLER_ID=$(aws sts get-caller-identity --query 'Account' --output text)
}

# Fedora Cloud Base images
fedora_caller_id () {
  export AWS_CALLER_ID_FEDORA=125523088429
}

# Official Red Hat images
red_hat_caller_id () {
  export AWS_CALLER_ID_RED_HAT=309956199498
}

# Official Centos images
centos_caller_id () {
  export AWS_CALLER_ID_CENTOS=679593333241
}

build_caller_id () {

  case "$OS" in
    rhel)
        BUILD_CALLER_ID=309956199498
        AMI_PREFIX="RHEL-7.5_HVM_GA*"
        IS_PUBLIC="false"
        ;;
    centos)
        BUILD_CALLER_ID=679593333241
        AMI_PREFIX="CentOS Linux 7 x86_64 HVM EBS *"
        IS_PUBLIC="true"
        ;;
    fedora)
        BUILD_CALLER_ID=125523088429
        AMI_PREFIX="Fedora-Cloud-Base-29-*"
        IS_PUBLIC="true"
        ;;
    dlts)
        BUILD_CALLER_ID=$(aws sts get-caller-identity --query 'Account' --output text)
        # this one still need work
        AMI_PREFIX="*ACM-CentOS-7.4*"
        IS_PUBLIC="false"
        ;;
    *)
        echo "${OS} is not currently supported"
        exit 99
        ;;

  esac

}

get_base_ami () {
  echo "OS: $OS"

  echo "BUILD_CALLER_ID: $BUILD_CALLER_ID"
  aws ec2 describe-images --owners $BUILD_CALLER_ID \
    --filters \
       "Name=is-public,Values=${IS_PUBLIC}" \
       "Name=name,Values=${AMI_PREFIX}" \
       "Name=state,Values=available" \
    --output json | jq -r '.Images | sort_by(.CreationDate) | last(.[]).ImageId'
}

build_vars () {
  OS_MAJ="7"
  OS_MIN="4"
}

package_check () {
    command -v aws > /dev/null || (echo "aws cli must be installed" && exit 1)
    command -v packer > /dev/null || (echo "packer must be installed" && exit 1)
    command -v git > /dev/null || (echo "git must be installed" && exit 1)
    command -v jq > /dev/null || (echo "jq must be installed" && exit 1)
}
