#!/bin/sh
mkdir -p workdir
cd workdir \
    && git init \
    && cp ../*.cpp ../*.h . \
    && git add *.cpp *.h \
    && git config user.name test \
    && git config user.email "test@example.com" \
    &&  git commit -m "initial commit"
