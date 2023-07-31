#!/bin/bash

curl -s -L https://kolejka.matinf.uj.edu.pl/kolejka-judge -o common/kolejka-judge
curl -s -L https://kolejka.matinf.uj.edu.pl/kolejka-client -o common/kolejka-client

for s in 1_1_set0; do
  rm -rf "${s}.task"
  rm -rf "${s}.result"
  python3 common/kolejka-judge task --callback "https://baca2.ii.uj.edu.pl/callback/abc123def" common/judge.py "${s}"/tests.yaml ../../prog/solution.cpp "${s}.task"
  python3 common/kolejka-client --debug --config-file kolejka.conf execute "${s}.task" "${s}.result"
done
