#!/bin/sh
# executed from project root

for file in unidown/plugins/data/protobuf/*.proto; do
    protoc --proto_path=./ --python_out=./ ${file}
done

