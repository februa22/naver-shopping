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
                        리뷰 갯수가 이 값보다 작은 상품만 조회합니다. (default: 5)
  --num_jjim NUM_JJIM
                        찜하기 갯수가 이 값보다 작은 상품만 조회합니다. (default: 10)
  --max_paging_index MAX_PAGING_INDEX
                        최대 페이지 갯수 (defalut: 3)
```

Sample output:

```
[1] 검색어: 니트; 전체 상품 갯수: 11056264
리뷰 갯수가 5개 미만인 상품은 총 14개 입니다.
====================
[2] 검색어: 앙고라니트; 전체 상품 갯수: 113666
리뷰 갯수가 5개 미만인 상품은 총 174개 입니다.
```

Sample summary:

```
검색순위, 검색어, 판매점수 낮은 상품 갯수
1, 니트, 14
2, 앙고라니트, 174
```
