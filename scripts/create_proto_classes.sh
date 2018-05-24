#!/bin/sh
# executed from project root

for file in unidown/plugin/protobuf/*.proto; do
    protoc --proto_path=./ --python_out=./ ${file}
done

