#!/bin/sh

NUM_QUERY=2
TOPK_FILEPATH=data/query.top$NUM_QUERY.json
NUM_REVIEWS=5
NUM_JJIM=10
MAX_PAGING_INDEX=2
CHROMEDRIVE_PATH=resources/chromedriver_win32/chromedriver.exe

python popularity/get_rank_topk.py \
  --num_query $NUM_QUERY \
  --topk_filepath $TOPK_FILEPATH \
  --chromedrive_path $CHROMEDRIVE_PATH

# python -m popularity.popularity \
#   --topk_filepath $TOPK_FILEPATH \
#   --num_reviews $NUM_REVIEWS \
#   --num_jjim $NUM_JJIM \
#   --max_paging_index $MAX_PAGING_INDEX \
#   --chromedrive_path $CHROMEDRIVE_PATH
