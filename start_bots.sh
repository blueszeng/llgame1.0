#!/bin/sh

export KBE_ROOT="../"
export KBE_RES_PATH="$KBE_ROOT/kbe/res/:$KBE_ROOT/llgame1.0:$KBE_ROOT/llgame1.0/res/:$KBE_ROOT/llgame1.0/scripts/"
export KBE_BIN_PATH="$KBE_ROOT/kbe/bin/server/"

echo KBE_ROOT = \"${KBE_ROOT}\"
echo KBE_RES_PATH = \"${KBE_RES_PATH}\"
echo KBE_BIN_PATH = \"${KBE_BIN_PATH}\"

$KBE_BIN_PATH/bots&

