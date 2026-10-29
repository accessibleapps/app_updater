#!/bin/bash
set -e

pid="$1"
SourcePath="$2"
DestPath="$3"
ToExecute="$4"

while kill -0 "$pid" 2>/dev/null; do
    sleep 1
done

# Stage on the destination volume, preserving framework links and permissions.
test -d "$SourcePath/Contents"
test -d "$DestPath/Contents"
stage=$(mktemp -d "${DestPath%/*}/.app-update.XXXXXX")
/usr/bin/ditto "$SourcePath/Contents" "$stage/Contents"
mv "$DestPath/Contents" "$stage/previous"
if ! mv "$stage/Contents" "$DestPath/Contents"; then
    mv "$stage/previous" "$DestPath/Contents"
    exit 1
fi
rm -rf "$stage"
exec "$ToExecute"
