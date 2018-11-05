#!/bin/bash
#
# Increment version number (last part of version string)
# read from a file containing only the version number.
#
# Assuming a version number scheme following SemVer
# consisting of
#
#	MAJOR.MINOR.PATCH
#
# in which case "PATCH" is incremented,
# or alternatively
#
#	MAJOR.MINOR.PATCH.dev#
#
# where the number following "dev" is incremented.
#
# If the internal variable CHECKGIT is set to "true", the file
# containing the version string will be checked for manual changes
# and if there are any, the script will exit immediately.
#
# Copyright (c) 2017-18, Till Biskup
# 2018-11-05

# Some configuration
VERSIONFILE="VERSION"
CHECKGIT=true # set to "true" to check for changes via git diff

# Internal functions
function join_by { local IFS="$1"; shift; echo "$*"; }

if [[ ${CHECKGIT} == true && `git diff --name-only ${VERSIONFILE}` ]]
then
    echo "File $VERSIONFILE has been changed already..."
    exit
fi


# Read version from file
read oldversionstring <<< `cat ${VERSIONFILE}`

# Split version string
IFS='.' read -r -a versionArray <<< "$oldversionstring"

lastPart=${versionArray[${#versionArray[@]}-1]}

# Check whether we need to increment a development version
# Otherwise just increment $lastPart
if [[ ${lastPart} =~ .*dev.* ]]
then
    IFS='dev' read -r -a splitLastPart <<< "$lastPart"
    revision=${splitLastPart[${#splitLastPart[@]}-1]}
    ((revision++))
    lastPart=dev${revision}
else
    ((lastPart++))
fi

# Reassign last part of versionArray
versionArray[${#versionArray[@]}-1]=${lastPart}

# Concatenate new version string
newVersionString=`join_by . ${versionArray[@]}`

# Write new version string to file
echo ${newVersionString} > ${VERSIONFILE}

if [[ ${CHECKGIT} == true ]]
then
    git add ${VERSIONFILE}
    echo "Version in version file upped"
fi
