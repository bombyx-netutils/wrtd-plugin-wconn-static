#!/bin/bash

LIBFILES="$(find ./wconn_static -name '*.py' | tr '\n' ' ')"

autopep8 -ia --ignore=E501 ${LIBFILES}
