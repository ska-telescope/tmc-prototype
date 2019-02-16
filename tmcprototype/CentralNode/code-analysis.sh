#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=rcfile CentralNode

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=rcfile test
