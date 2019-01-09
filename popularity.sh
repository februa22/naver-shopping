#!/bin/sh

QUERY="all"
TOPK_FILEPATH=data/cardigan.top100.txt
NUM_REVIEWS=5
NUM_JJIM=10
MAX_PAGING_INDEX=6

python -m popularity.popularity \
  --query="$QUERY" \
  --num_reviews=$NUM_REVIEWS \
  --num_jjim=$NUM_JJIM \
  --max_paging_index=$MAX_PAGING_INDEX \
  --topk_filepath=$TOPK_FILEPATH
