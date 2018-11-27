#!/bin/bash

set -e

DIRNAME=$(cd `dirname $0` && pwd)

usage() {
  echo "$0 <image OS>"
}

# load helper functions
source ${DIRNAME}/common.sh

# check for required tools
package_check

#
# base.sh OS
OS="$1"

BASE_NAME=$OS

[[ -z $1  ]] && usage && exit 1

build_caller_id

if [[ -z $BASE_NAME ]]; then
  echo "No base name"
  exit 2
else
  #AMI_BASE="$(get_base_ami "$BASE_BUILT" "$BASE" "$BASE_NAME")"
  AMI_SOURCE=$BASE_NAME
  #echo $AMI_SOURCE
  get_base_ami
fi
