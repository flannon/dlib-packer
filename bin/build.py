#!/usr/bin/env python

from __future__ import print_function
from subprocess import call
from subprocess import check_output

import boto3
import json
import os
import sys

#os_name = sys.argv[1]

#print("OS: " + os_name)

def get_image_spec(os_name):
    self_caller_id = boto3.client('sts').get_caller_identity().get('Account')
    #print(boto3.client('sts').get_caller_identity()['Account'])
    os_names = {
        'rhel': ('309956199498', 'RHEL-7.5_HVM_GA*', 'false'),
        'centos': ('679593333241', 'CentOS Linux 7 x86_64 HVM EBS *', 'true'),
        'fedora': ('125523088429', 'Fedora-Cloud-Base-29-*"', 'true'),
        'self': (self_caller_id, 'name'),
    }
    return os_names.get(os_name, 'undef')



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

def main():
    dirname = os.path.dirname(os.path.realpath(sys.argv[0]))
    os_name = sys.argv[1]
    image_spec = get_image_spec(os_name)
    caller_id = image_spec[0]
    base_image_prefix = image_spec[1]
    is_public = image_spec[2]
    base_ami_id, base_name = get_base_ami(caller_id, base_image_prefix, is_public)
    #print(image_id + ': ' + image_name)
    os.environ['BASE_AMI_ID'] = base_ami_id
    os.environ['BASE_NAME'] = base_name
    sha = get_sha()
    os.environ['SHA'] = sha

    ami_name = base_name[:50]

    ami_ssh_user = 'centos'
    os.environ['AMI_SSH_USER'] = ami_ssh_user
    sha = get_sha()

    build_config = "base/" + ami_ssh_user + "-base.json"
    v = check_output(["packer", "validate", build_config])

    #print("v:" + v + ':')
    if v == "Template validated successfully.\n":
        print("building ami")
        call(["packer", "build", build_config])
    else:
        print("Template validation falied")
        print(v)

    test = dirname + '/test.sh'
    #call([test])
    #print('ami_name: ' + ami_name)



if __name__ == "__main__":
    main()
