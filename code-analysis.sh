#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint DishMaster

echo "TESTS ANALYSIS"
echo "--------------"
pylint test
