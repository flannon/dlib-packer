#!/usr/bin/env python

from __future__ import print_function
from subprocess import call
from subprocess import check_output

import argparse
import boto3
import json
import os
import sys

#os_name = sys.argv[1]

#print("OS: " + os_name)

#def get_image_spec(os_name):
def get_image_spec(build_os):
    self_caller_id = boto3.client('sts').get_caller_identity().get('Account')
    #print(boto3.client('sts').get_caller_identity()['Account'])
    os_names = {
        'rhel': ('309956199498', 'RHEL-7.5_HVM_GA*', 'false'),
        'centos': ('679593333241', 'CentOS Linux 7 x86_64 HVM EBS *', 'true'),
        'fedora': ('125523088429', 'Fedora-Cloud-Base-29-*"', 'true'),
        'self': (self_caller_id, 'name'),
    }
    return os_names.get(build_os, 'undef')

def get_base_ami(caller_id, base_image_prefix, is_public):
    ec2 = boto3.client('ec2')
    response = ec2.describe_images(
        Owners=[caller_id], # CentOS
        Filters=[
            {'Name': 'name', 'Values': [base_image_prefix]},
            {'Name': 'architecture', 'Values': ['x86_64']},
            {'Name': 'root-device-type', 'Values': ['ebs']},
            {'Name': 'is-public', 'Values': [is_public]},
            #{'Name': 'state', 'Values': ['available']},
        ],
    )

    amis = sorted(response['Images'],
        key=lambda x: x['CreationDate'],
        reverse=True)

    base_image_id = amis[0]['ImageId']
    base_image_name = amis[0]['Name']
    return base_image_id, base_image_name

def get_sha():
    #SHA=$(git ls-tree HEAD "$DIR" | cut -d" " -f3 | cut -f1)
    #TAG_EXISTS=$(tag_exists $SHA)
    sha = '11111111'
    return sha

def get_ssh_user(build_os):
    if build_os == 'centos':
        ami_ssh_user = build_os
    elif build_os == 'rhel':
        ami_ssh_user = 'ec2-user'
    elif build_os == 'fedora':
        ami_ssh_user = build_os

    return ami_ssh_user


def build_config(build_os):
    #print("test")
    access = os.environ['AWS_ACCESS_KEY_ID']
    #print("access: " + access)
    ami_instance_profile = os.environ['AMI_INSTANCE_PROFILE']
    #print("ami_instance_profile: " + ami_instance_profile)
    #print("AMI_INSTANCE_PROFILE: " + os.environ['AMI_INSTANCE_PROFILE'])

    dirname = os.path.dirname(os.path.realpath(sys.argv[0]))

    ##os_name = sys.argv[1]
    print("build_os: " + build_os)
    image_spec = get_image_spec(build_os)
    caller_id = image_spec[0]
    base_image_prefix = image_spec[1]
    #print("is_public, image_spec[2]: " + image_spec[2])
    is_public = image_spec[2]
    #print("is_public: " + is_public)
    base_ami_id, base_name = get_base_ami(caller_id, base_image_prefix, is_public)
    #print("base_ami_id: " + base_ami_id)
    os.environ['BASE_AMI_ID'] = base_ami_id
    os.environ['BASE_NAME'] = base_name
    sha = get_sha()
    os.environ['SHA'] = sha

    ami_name = base_name[:50]
    #ami_name = base_name

    #ami_ssh_user = 'centos'
    ami_ssh_user = get_ssh_user(build_os)

    os.environ['AMI_SSH_USER'] = ami_ssh_user

    #bc = "-var-file=" + dirname + "/base/var/" + ami_ssh_user + "-base.json " + dirname + "base/" + ami_ssh_user + "-base.json"
    bc = "base/" + ami_ssh_user + "-base.json"

    return bc


def main():
#

    ##### !+
    ##v = check_output(["packer", "validate", build_config])

    ###print("v:" + v + ':')
    ##if v == "Template validated successfully.\n":
    ##    print("Template validatd successfully.")
    ##    print("building ami")
    ##    #call(["packer", "build", build_config])
    ##else:
    ##    print("Template validation falied")
    ##    print(v)
    ##### !-
#
    ##test = dirname + '/test.sh'
    ##call([test])
    ##print('ami_name: ' + ami_name)

    ap = argparse.ArgumentParser(description='Build images')
    ap.add_argument("-v", "--validate", action='store_true',
                    help='validate only')
    ap.add_argument("-o", "--os", nargs='*', required=True,
                    help='name of the base os')
    args = vars(ap.parse_args())

    #print("Hi there {}, it's nice to build you.".format(args["osname"]))
#
#    print(args["osname"])

    os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
    if args["validate"]:

        build_os = args["os"][0]
        bc = build_config(build_os)

        #print("Config vars")
        #print("BASE_NAME: " + os.environ['BASE_NAME'])
        #print("BASE_AMI_ID: " + os.environ['BASE_AMI_ID'])
        #print("SHA: " + os.environ['SHA'])
        #print("AMI_SSH_USER: " + os.environ['AMI_SSH_USER'])

        #print("access_key: " + os.environ['AWS_ACCESS_KEY_ID'])
        #print("build_vpc: " + os.environ['BUILD_VPC_ID'])
        #print("build_subnet_id: "  + os.environ['BUILD_SUBNET_ID'])
        #print("build_sec_group: "  + os.environ['BUILD_SECURITY_GROUP'])
        call(["packer", "validate", bc])

    elif args["os"]:
        print("building ami...")

        build_os = args["os"][0]
        bc = build_config(build_os)

        #print("Config vars")
        #print("BASE_NAME: " + os.environ['BASE_NAME'])
        #print("BASE_AMI_ID: " + os.environ['BASE_AMI_ID'])
        #print("SHA: " + os.environ['SHA'])
        #print("AMI_SSH_USER: " + os.environ['AMI_SSH_USER'])

        call(["packer", "build", bc])

    else:
        print("Usage: build.py -os <operating sytem> | -v")


if __name__ == "__main__":
    main()
