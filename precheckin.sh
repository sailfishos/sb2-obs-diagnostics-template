#!/bin/sh
ARCHS="armv7hl aarch64 i486"

for x in $ARCHS; do
	sed "s/@ARCH@/$x/g" sb2-obs-diagnostics-template.spec > sb2-obs-diagnostics-$x.spec
done
