#!/bin/sh

QUERY="all"
TOPK_FILEPATH=data/query.knits.top100.txt
NUM_REVIEWS=5
MAX_PAGING_INDEX=3

python -m main \
  --query="$QUERY" \
  --num_reviews=$NUM_REVIEWS \
  --max_paging_index=$MAX_PAGING_INDEX \
  --topk_filepath=$TOPK_FILEPATH
