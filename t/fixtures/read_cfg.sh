#!/bin/bash
[[ $# -ne 1 ]] && exit 1
# shellcheck source=ngcpcfg.cfg
source "${1}"
echo "[ngcpcfg]"
# directory name where ngcpcfg is managed through git
echo "NGCPCTL_BASE=${NGCPCTL_BASE:-}"
echo "NGCPCTL_MAIN=${NGCPCTL_MAIN:-}"
echo "NGCPCTL_CONFIG=${NGCPCTL_CONFIG:-}"
# HA_CONFIG is deprecated, only for backwards compatibility.
echo "HA_CONFIG=${NODE_CONFIG:-}"
echo "NODE_CONFIG=${NODE_CONFIG:-}"
echo "PAIR_CONFIG=${PAIR_CONFIG:-}"
echo "HOST_CONFIG=${HOST_CONFIG:-}"
echo "LOCAL_CONFIG=${LOCAL_CONFIG:-}"
echo "CONSTANTS_CONFIG=${CONSTANTS_CONFIG:-}"
echo "NETWORK_CONFIG=${NETWORK_CONFIG:-}"
echo "RTP_INTERFACES_CONFIG=${RTP_INTERFACES_CONFIG:-}"
echo "EXTRA_CONFIG_DIR=${EXTRA_CONFIG_DIR:-}"

# configuration dirs that should be managed
echo "CONFIG_POOL=${CONFIG_POOL:-}"

# location of templates
echo "TEMPLATE_POOL_BASE=${TEMPLATE_POOL_BASE:-}"

# location of service definitions
echo "SERVICES_POOL_BASE=${SERVICES_POOL_BASE:-}"

# location of instances info for templates
echo "TEMPLATE_INSTANCES=${TEMPLATE_INSTANCES:-}"

# timestamp format for console output
echo "TIME_FORMAT=${TIME_FORMAT:-}"

# Run-time state directory
echo "RUN_DIR=${RUN_DIR:-}"

# directory holding files for internal state of ngcpcfg
echo "STATE_FILES_DIR=${STATE_FILES_DIR:-}"

# validate configs using kwalify schema
echo "VALIDATE_SCHEMA=${VALIDATE_SCHEMA:-}"

# file ownership and permissions for YML files
echo "CONFIG_USER=${CONFIG_USER:-}"
echo "CONFIG_GROUP=${CONFIG_GROUP:-}"
echo "CONFIG_CHMOD=${CONFIG_CHMOD:-}"
echo "CONSTANTS_CONFIG_USER=${CONSTANTS_CONFIG_USER:-}"
echo "CONSTANTS_CONFIG_GROUP=${CONSTANTS_CONFIG_GROUP:-}"
echo "CONSTANTS_CONFIG_CHMOD=${CONSTANTS_CONFIG_CHMOD:-}"
echo "NETWORK_CONFIG_USER=${NETWORK_CONFIG_USER:-}"
echo "NETWORK_CONFIG_GROUP=${NETWORK_CONFIG_GROUP:-}"
echo "NETWORK_CONFIG_CHMOD=${NETWORK_CONFIG_CHMOD:-}"

# fake values from ngcpcfg-ha
# HA_FILE is deprecated, only for backwards compatibility.
echo "HA_FILE=${HA_FILE:-}"
echo "NODE_FILE=${NODE_FILE:-}"
echo "HOST_FILE=${HOST_FILE:-}"
echo "PAIR_FILE=${PAIR_FILE:-}"
