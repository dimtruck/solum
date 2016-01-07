#!/bin/bash
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script is executed inside post_test_hook function in devstack gate.

source $BASE/new/devstack/functions
echo "TEMPEST_SERVICES+=,solum" >> $localrc_path
pushd $BASE/new/tempest
sudo chown -R jenkins:stack $BASE/new/tempest

# show tempest config with solum
cat etc/tempest.conf

# Set up concurrency and test regex
export SOLUM_TEMPEST_CONCURRENCY=${SOLUM_TEMPEST_CONCURRENCY:-1}
export SOLUM_TESTS=${SOLUM_TESTS:-'solum.tests.functional.api'}

API_RESPONDING_TIMEOUT=20
SERVICES=("solum-api" "solum-worker" "solum-conductor" "solum-deployer")
SOLUM_CONFIG="/etc/solum/solum.conf"
declare -A CONFIG_SECTIONS=(["api"]=9777)

function check_api {
    local host=$1
    local port=$2
    if ! timeout ${API_RESPONDING_TIMEOUT} sh -c "while ! curl -s -o /dev/null http://$host:$port ; do sleep 1; done"; then
        echo "Failed to connect to API $host:$port within ${API_RESPONDING_TIMEOUT} seconds"
        exit 1
    fi
}

# Check if solum services are running
for s in ${SERVICES[*]}
do
    if [ ! `pgrep -f $s` ]; then
        echo "$s is not running"
        exit 1
    fi
done

for sec in ${!CONFIG_SECTIONS[*]}
do
    pt=${CONFIG_SECTIONS[$sec]}
    line=$(sed -ne "/^\[$sec\]/,/^\[.*\]/ { /^port[ \t]*=/ p; }" $SOLUM_CONFIG)
    if [ ! -z "${line#*=}" ]; then
        pt=${line#*=}
    fi
    hst="127.0.0.1"
    line=$(sed -ne "/^\[$sec\]/,/^\[.*\]/ { /^host[ \t]*=/ p; }" $SOLUM_CONFIG)
    if [ ! -z "${line#*=}" ]; then
        hst=${line#*=}
    fi

    check_api $hst $pt
done

echo "Running tempest solum test suites"
sudo -H -u jenkins tox -eall-plugin -- $SOLUM_TESTS --concurrency=$SOLUM_TEMPEST_CONCURRENCY
