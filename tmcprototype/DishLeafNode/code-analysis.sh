#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=rcfile DishLeafNode


echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=rcfile test
