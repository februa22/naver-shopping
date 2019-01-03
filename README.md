# naver-shopping

## Installing

Clone or download codes: <https://github.com/februa22/naver-shopping.git>

Install Python packages using `pip install`:

```python
beautifulsoup4==4.6.3
requests==2.21.0
```

## Run

쉘스크립트 실행:

```sh
./popularity.sh
```

Optional arguments:

```sh
  --query QUERY         검색어 (default: "all")
  --topk_filepath TOPK_FILEPATH
                        검색어가 "all"인 경우에 사용하는 인기검색어목록 파일경로
  --num_reviews NUM_REVIEWS
                        리뷰 갯수가 이 숫자보다 작은 상품만 조회합니다.
  --max_paging_index MAX_PAGING_INDEX
                        최대 페이지 갯수 (defalut: 3)
```
