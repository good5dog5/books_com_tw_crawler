# books_com_tw_crawler

## Setup virtualenv

``` bash
python -m venv .venv
source .venv/bin/activate
```

## Install

### Required packages

```
pip  install -r requirements.txt
```

## Usage

### Crawler
Collect data from books.com.tw with the following cmd, the collected data named `top100_0.json`
under current directory.

```
python crawler.py
```

### Data analysis

It will output 4 files which indicate 

1. top 5% discount books(`top_5_discount`).
2. book count of first level  category(`l1_book_cnt`).
3. book count of second level  category(`l2_book_cnt`).
4. book count of third level  category(`l3_book_cnt`).
5. book count of fourth level  category(`l4_book_cnt`).
```
python preprocess.py
```
