#!/bin/bash

set_xterm_title () {
    local title="$1"
    echo -ne "\e]0;$title\007"
}

hn=$(hostname -s)
if [ -z "$*" ]; then
    set_xterm_title "${USER}@${hn}"
else
    set_xterm_title $*
fi
