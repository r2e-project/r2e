#!/bin/bash

# Default values
REPO_URL="https://github.com/r2e-project/r2e.git"
LOCAL_REPO_PATH="~/buckets/my_repos/r2e"
EXP_ID="demo"
MULTIPROCESS=8
CACHE_BATCH_SIZE=100

# Parse arguments
while getopts u:p:e:m:c: flag
do
    case "${flag}" in
        u) REPO_URL=${OPTARG};;
        p) LOCAL_REPO_PATH=${OPTARG};;
        e) EXP_ID=${OPTARG};;
        m) MULTIPROCESS=${OPTARG};;
        c) CACHE_BATCH_SIZE=${OPTARG};;
    esac
done

# Clone your repo and move it to R2E's workspace
git clone $REPO_URL $LOCAL_REPO_PATH
python r2e/repo_builder/setup_repos.py --local_repo_path $LOCAL_REPO_PATH

# Extract functions and methods from the repo
python r2e/repo_builder/extract_func_methods.py --exp_id $EXP_ID --overwrite_extracted

# Generate equivalence tests
python r2e/generators/testgen/generate.py -i ${EXP_ID}_extracted.json --exp_id $EXP_ID --multiprocess $MULTIPROCESS --use_cache --cache_batch_size $CACHE_BATCH_SIZE