#!/bin/bash

# Packs the code of the lambda function into what Terraform expects
rm -f tag-scheduler.zip 2> /dev/null

pushd src
zip ../tag-scheduler.zip *
popd
