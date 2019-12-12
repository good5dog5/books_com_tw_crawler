import pandas as pd
import numpy as np
import json
import re

def categories_col_tolist(col_categories):
    return col_categories.split('本書分類：')[1:]

def get_nth_category_str(col_categories, nth):
    if len(categories_col_tolist(col_categories)) < nth:
        return np.nan
    return categories_col_tolist(col_categories)[nth-1]

def top_n_percent_money_saving(df, percent):
    import math
    assert percent >= 0 and percent <= 100
    nth = math.ceil(percent / 100 * df.shape[0])

    return df.sort_values(by=['save_amount'], ascending=False).iloc[0:nth, :]


raw_df = pd.read_json('./top100.json', orient='index')
raw_df['categories']   = raw_df['categories'].apply(lambda x: re.sub(r'\s+', '', x))

new_df = raw_df.copy()
new_df['title'] = raw_df['title'].apply(lambda x: x.replace('\n', ' '))
new_df['orig_price']   = raw_df['orig_price'].apply(lambda x: int(re.findall(r'\d+', x)[0]))
new_df['spec_price']   = raw_df['spec_price'].apply(lambda x: int(re.findall(r'\d+', x)[1]))
new_df['discount']     = raw_df['spec_price'].apply(lambda x: int(re.findall(r'\d+', x)[0]))
new_df['save_amount']  = new_df.apply(lambda x: x['orig_price'] - x['spec_price'], axis=1)
new_df['num_category'] = raw_df['categories'].apply(lambda x: len(categories_col_tolist(x)))

# category 欄位為 categories 中的第一筆, 並轉成 list
new_df['category']          = raw_df['categories'].apply(lambda x: get_nth_category_str(x, 1).split('>'))

# 處理有大於一比分類的書
for idx, row in new_df.iterrows():
    if len(categories_col_tolist(row['categories'])) > 1:
        for i in range(2, len(categories_col_tolist(row['categories'])) + 1):
            new_row = row
            row['category'] = get_nth_category_str(row['categories'], i).split('>')
            new_df = new_df.append(row)

new_df.sort_values(by=['title'])
new_df.reset_index(inplace=True)

new_df['level_of_category'] = new_df['category'].apply(lambda x: len(x))

# 檢查要做幾層
max(new_df['level_of_category'])

new_df['l1']           = new_df['category'].apply(lambda x: x[0] if len(x) >= 1 else np.nan)
new_df['l2']           = new_df['category'].apply(lambda x: x[1] if len(x) >= 2 else np.nan)
new_df['l3']           = new_df['category'].apply(lambda x: x[2] if len(x) >= 3 else np.nan)
new_df['l4']           = new_df['category'].apply(lambda x: x[3] if len(x) >= 4 else np.nan)

# data inspection
new_df['l1'].unique()
new_df['l2'].unique()
new_df['l3'].unique()
new_df['l4'].unique()

# book count in each categorial level
l1 = new_df.drop_duplicates(subset=['title', 'l1']).groupby(['l1'])['index'].count().to_dict()
l2 = new_df.drop_duplicates(subset=['title', 'l1', 'l2']).groupby(['l1', 'l2'])['index'].count().to_dict()
l3 = new_df.drop_duplicates(subset=['title', 'l1', 'l2', 'l3']).groupby(['l1', 'l2', 'l3'])['index'].count().to_dict()
l4 = new_df.drop_duplicates(subset=['title', 'l1', 'l2', 'l3', 'l4']).groupby(['l1', 'l2', 'l3', 'l4'])['index'].count().to_dict()

format_keys(l2)
format_keys(l3)
format_keys(l4)

def format_keys(dict_name):
    keys = list(dict_name.keys())
    for k in keys:
        val = dict_name.pop(k)
        dict_name['>'.join(k)] = val

def dict_2_json_file(file_name, dict_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(dict_name, f, indent = 4, ensure_ascii = False)

dict_2_json_file('l1_book_cnt.json', l1)
dict_2_json_file('l2_book_cnt.json', l2)
dict_2_json_file('l3_book_cnt.json', l3)
dict_2_json_file('l4_book_cnt.json', l4)

# top n %
# 這本的 discount 欄位錯了
new_df.drop(3, inplace=True)
top_n_df = top_n_percent_money_saving(new_df, 5)
top_n_df.to_csv('./top_5_discount.csv')