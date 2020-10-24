#!/bin/bash

# Get list with derivates from distrowatch
# https://distrowatch.com/search.php, select "Based On"

if [ -f /tmp/get-distro-families-done ]; then
    # Already done this session
    exit
fi

# My directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Distro families to save
FAMILIES='Ubuntu Debian Manjaro Arch CentOS Fedora Gentoo Mandriva openSUSE Puppy Slackware Solaris'

SAVEPATH="$DIR/data/files/distributions/families"

# Source extras
. "$DIR/families-extra"

# Initiate families file
echo "FAMILIES=\"${FAMILIES,,} independent\"" > "$SAVEPATH.tmp"

# Get derivates for each family
SAVEFILE=false
PREVDISTROS=''
for F in $FAMILIES; do
    echo "Get data for $F..."
    # Build the URL
    URL="https://distrowatch.com/search.php?ostype=All&category=All&origin=All&basedon=$F&notbasedon=None&desktop=All&architecture=All&package=All&rolling=All&isosize=All&netinstall=All&language=All&defaultinit=All&status=Active#simple"
    # Get the data and extract the distro codes
    DISTROS=$(wget -qO- $URL | grep -oP '<b>[0-9]+\.\s<a href="([a-z]*)">[a-zA-Z0-9]*' | sed -n 's/.*"\([a-z]*\)".*/\1/p' | tr '\r\n' ' ')
    DISTROS=${DISTROS,,}
    F=${F,,}
    # Check if distro wasn't already added
    FLTDISTROS="$F"
    for PD in $DISTROS; do
       if [[ "$PREVDISTROS" != *$PD*  ]] && [ "$PD" != "$F" ]; then
           FLTDISTROS="$FLTDISTROS $PD"
       fi
    done
    if [ ! -z "$FLTDISTROS" ]; then
        PREVDISTROS="$FLTDISTROS $PREVDISTROS"
        # Append the extra distributions
        XTRAS=$(eval "echo \$${F^^}")
        if [ ! -z "$XTRAS" ]; then
            XTRAS=" $XTRAS"
        fi
        # Save distros to file
        echo "${F^^}=\"$FLTDISTROS$XTRAS\"" | tee -a "$SAVEPATH.tmp"
        echo
        SAVEFILE=true
    fi
done

if $SAVEFILE; then
    # Add independent distributions
    IND=$(ls "./data/files/distributions/independent" | tr '\r\n' ' ' | sed 's/ *$//')
    echo "INDEPENDENT=\"$IND\"" | tee -a "$SAVEPATH.tmp"
    echo
    mv -vf "$SAVEPATH.tmp" "$SAVEPATH"
    touch /tmp/get-distro-families-done
fi
