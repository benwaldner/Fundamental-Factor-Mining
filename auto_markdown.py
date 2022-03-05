import pandas as pd
import re

from Config import *

p = re.compile(r'# !!!(.*)# !!!', re.S)


def read_file(path):
    with open(path, 'r', encoding='utf8') as f:
        content = f.read()
        res = p.findall(content)
        return res[0].strip()


def write_file(content):
    with open(root_path + '\\financial_factor_stock_picking\\Bradley_result.md', 'w', encoding='utf8') as f:
        f.write(content)


# 读取config文件
config_str = read_file(root_path + '\\financial_factor_stock_picking\\Config.py')

# 读取CalcFactor文件
factor_str = read_file(root_path + '\\financial_factor_stock_picking\\CalcFactor.py')

# 读取Filter文件
filter_str = read_file(root_path + '\\financial_factor_stock_picking\\Filter.py')

# 策略回测表现
rtn = pd.read_csv(root_path + '\\financial_factor_stock_picking\\data\\output\\策略结果\\策略评价_%s.csv' % period_type, encoding='gbk')
rtn.columns = ['指标', '表现']
rtn_str = rtn.to_markdown(index=False)

# 年度同期表现
year_rtn = pd.read_csv(root_path + '\\financial_factor_stock_picking\\data\\output\\策略结果\\策略评价_year_%s.csv' % period_type, encoding='gbk')
year_rtn.columns = ['交易日期', '策略收益', '指数收益', '超额收益']
year_rtn_str = year_rtn.to_markdown(index=False)

# first write the essay part in the "markdown_template"
# then this py file will fit the code part into the template, and then write into Bradley_result.md
with open(root_path + '\\financial_factor_stock_picking\\markdown_template.md', 'r', encoding='utf8') as file:
    template = file.read()
    template = template % (config_str, factor_str, filter_str, rtn_str, year_rtn_str)
    print(template)
    write_file(template)
