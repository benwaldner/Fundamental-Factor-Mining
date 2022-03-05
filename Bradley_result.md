# 一、策略思路
基于原始策略并仿照仿照`https://bbs.quantclass.cn/thread/10053`计算数据，增加盈利现金比率、中户资金流、市销率等财务因子，并在此基础上尝试调整股票池各指标筛选的权重，删除了一些指标的筛选条件，例如ROE。

# 二、策略描述

**股票池初步筛选：**
- 0.1 < PE(ttm)升序 <= 0.4
- 0.1 < 二级行业PE(ttm)升序 <= 0.4
- 现金流负债比降序 <= 0.4
- 资产负债率 <= 0.7
- 企业倍数升序 <= 0.55

**符合因子升序筛选：**
- 市值升序
- 中户资金流降序
- ROE(ttm)降序
- 市销率ttm升序
- 成交额std_10分位数降序
- bias_10降序
- 现金流比降序
- 成本营收比降序
- 盈利现金比率降序

# 三、策略代码

## 3.1 config代码
```python
# 因为财务数据众多，将本策略中需要用到的财务数据字段罗列如下
raw_fin_cols = [
    # 短期借款 长期借款 应付债券 一年内到期的非流动负债
    'B_st_borrow@xbx', 'B_lt_loan@xbx', 'B_bond_payable@xbx', 'B_noncurrent_liab_due_in1y@xbx',
    # 营业总收入 负债应付利息 应付手续费及佣金
    'R_operating_total_revenue@xbx', 'B_interest_payable@xbx', 'B_charge_and_commi_payable@xbx',
    # 销售费用 管理费用 研发费用 资产减值损失
    'R_sales_fee@xbx', 'R_manage_fee@xbx', 'R_rad_cost_sum@xbx', 'R_asset_impairment_loss@xbx',
    # 固定资产折旧、油气资产折耗、生产性生物资产折旧 无形资产摊销 长期待摊费用摊销
    'C_depreciation_etc@xbx', 'C_intangible_assets_amortized@xbx', 'C_lt_deferred_expenses_amrtzt@xbx',
    # 其他综合利益 税金及附加 营业成本
    'R_other_compre_income@xbx', 'R_operating_taxes_and_surcharge@xbx', 'R_operating_cost@xbx',
    # 归母净利润 归母所有者权益合计 货币资金 流动负债合计
    'R_np_atoopc@xbx', 'B_total_equity_atoopc@xbx', 'B_currency_fund@xbx', 'B_total_current_liab@xbx',
    # 非流动负债合计 经营活动产生的现金流量净额
    'B_total_noncurrent_liab@xbx', 'C_ncf_from_oa@xbx',
    # 净利润  营业总成本
    'R_np@xbx', 'R_operating_total_cost@xbx',


    # 资产总额、负债总额
    'B_total_assets@xbx', 'B_total_liab@xbx',
    # 非流动资产合计  流动资产合计
    'B_total_noncurrent_assets@xbx', 'B_total_current_assets@xbx',
    # 经营性应付项目的增加
    'C_increase_of_operating_item@xbx',
    # 营业收入
    'R_revenue@xbx',
    # 经营活动产生的现金流量的商品销售、提供劳务收到的现金
    'C_cash_received_of_sales_service@xbx',
]

# raw_fin_cols财务数据中所需要计算流量数据的原生字段
flow_fin_cols = [
    # 归母净利润 净利润 营业总收入 营业总成本
    'R_np_atoopc@xbx', 'R_np@xbx', 'R_operating_total_revenue@xbx', 'R_operating_total_cost@xbx',
    # 营业收入
    'R_revenue@xbx',
]

# raw_fin_cols财务数据中所需要计算截面数据的原生字段
cross_fin_cols = []

# 下面是处理财务数据之后需要的ttm，同比等一些字段
derived_fin_cols = [
    # 归母净利润_TTM  归母净利润_TTM同比  净利润_TTM  净利润_TTM同比
    'R_np_atoopc@xbx_ttm', 'R_np_atoopc@xbx_ttm同比', 'R_np@xbx_ttm', 'R_np@xbx_ttm同比',
    # 营业总收入_TTM  营业总成本_TTM
    'R_operating_total_revenue@xbx_ttm', 'R_operating_total_cost@xbx_ttm',
    # 营业收入_TTM
    'R_revenue@xbx_ttm',
]
```

## 3.2 CalcFactor代码
```python
def cal_tech_factor(df, extra_agg_dict):
    """
    计算量价因子
    :param df:
    :param extra_agg_dict:
    :return:
    """
    # =计算均价
    df['VWAP'] = df['成交额'] / df['成交量']
    extra_agg_dict['VWAP'] = 'last'

    # =计算换手率
    df['换手率'] = df['成交额'] / df['流通市值']
    extra_agg_dict['换手率'] = 'sum'

    # =计算5日均线
    df['5日均线'] = df['收盘价_复权'].rolling(5).mean()
    extra_agg_dict['5日均线'] = 'last'

    # =计算10日均线
    df['10日均线'] = df['收盘价_复权'].rolling(10).mean()
    extra_agg_dict['10日均线'] = 'last'

    # =计算20日均线
    df['20日均线'] = df['收盘价_复权'].rolling(20).mean()
    extra_agg_dict['20日均线'] = 'last'


    # =计算bias
    df['bias_5'] = df['收盘价_复权'] / df['5日均线'] - 1
    extra_agg_dict['bias_5'] = 'last'
    # =计算bias
    df['bias_10'] = df['收盘价_复权'] / df['10日均线'] - 1
    extra_agg_dict['bias_10'] = 'last'
    # =计算bias
    df['bias_20'] = df['收盘价_复权'] / df['20日均线'] - 1
    extra_agg_dict['bias_20'] = 'last'

    # =计算5日累计涨跌幅
    df['5日累计涨跌幅'] = df['涨跌幅'].pct_change(5)
    extra_agg_dict['5日累计涨跌幅'] = 'last'

    # =计算12日均线   add by zlj 20220301
    df['12日均线'] = df['收盘价_复权'].rolling(12).mean()
    extra_agg_dict['12日均线'] = 'last'

    # =计算5日成交量均线    add by zlj 20220301
    df['5日成交量均线'] = df['成交量'].rolling(5).mean()
    extra_agg_dict['5日成交量均线'] = 'last'

    # =计算5日成交量均线    add by zlj 20220301
    df['5日中户资金流'] = df['中户资金买入额'].rolling(5).mean() * 10000 / df['成交额'].rolling(5).mean()
    extra_agg_dict['5日中户资金流'] = 'last'

    # =计算5日成交量均线    add by zlj 20220301
    df['5日大户资金流'] = df['大户资金买入额'].rolling(5).mean() * 10000 / df['成交额'].rolling(5).mean()
    extra_agg_dict['5日大户资金流'] = 'last'

    # =计算5日成交量均线    add by zlj 20220301
    df['中户资金流'] = df['中户资金买入额'] * 10000 / df['成交额']
    extra_agg_dict['中户资金流'] = 'last'

    # =计算5日成交量均线    add by zlj 20220301
    df['大户资金流'] = df['大户资金买入额'] * 10000 / df['成交额']
    extra_agg_dict['大户资金流'] = 'last'

    # =计算5日成交量均线    add by zlj 20220301
    df['现金流比'] = df['现金流TTM'] / df['总市值']
    extra_agg_dict['现金流比'] = 'last'

    # # =计算bias
    # df['bias'] = df['收盘价_复权'] / df['5日均线'] - 1
    # extra_agg_dict['bias'] = 'last'
    #
    # # =计算5日累计涨跌幅
    # df['5日累计涨跌幅'] = df['涨跌幅'].pct_change(5)
    # extra_agg_dict['5日累计涨跌幅'] = 'last'

    # =计算10日成交额std
    df['成交额_std_10'] = df['成交额'].rolling(10, min_periods=1).std(ddof=0)
    extra_agg_dict['成交额_std_10'] = 'last'

    # =计算换手率
    df['换手率'] = df['成交额'] / df['流通市值']
    extra_agg_dict['换手率'] = 'sum'

    # =计算125日累计涨跌幅
    df['125日累计涨跌幅'] = df['涨跌幅'].pct_change(125)
    extra_agg_dict['125日累计涨跌幅'] = 'last'

    return df


def calc_fin_factor(df, extra_agg_dict):
    """
    计算财务因子
    :param df:              原始数据
    :param extra_agg_dict:  resample需要用到的
    :return:
    """

    # ====计算常规的财务指标
    # 计算归母PE
    # 归母PE = 总市值 / 归母净利润(ttm)
    df['归母PE(ttm)'] = df['总市值'] / df['R_np_atoopc@xbx_ttm']
    extra_agg_dict['归母PE(ttm)'] = 'last'

    # 计算归母ROE
    # 归母ROE(ttm) = 归母净利润(ttm) / 归属于母公司股东权益合计
    df['归母ROE(ttm)'] = df['R_np_atoopc@xbx_ttm'] / df['B_total_equity_atoopc@xbx']
    extra_agg_dict['归母ROE(ttm)'] = 'last'

    # 计算毛利率ttm
    # 毛利率(ttm) = ( 营业总收入_ttm - 营业总成本_ttm ) / 营业总收入_ttm
    df['毛利率(ttm)'] = 1 - df['R_operating_total_cost@xbx_ttm'] / df['R_operating_total_revenue@xbx_ttm']
    
    extra_agg_dict['毛利率(ttm)'] = 'last'

    # 计算企业倍数指标
    """
    EV2 = 总市值+有息负债-货币资金, 
    EBITDA = 营业总收入-营业税金及附加-营业成本+利息支出+手续费及佣金支出+销售费用+管理费用+研发费用+坏账损失+存货跌价损失+固定资产折旧、油气资产折耗、生产性生物资产折旧+无形资产摊销+长期待摊费用摊销+其他收益
    """
    # 有息负债 = 短期借款 + 长期借款 + 应付债券 + 一年内到期的非流动负债
    df['有息负债'] = df[['B_st_borrow@xbx', 'B_lt_loan@xbx', 'B_bond_payable@xbx', 'B_noncurrent_liab_due_in1y@xbx']].sum(
        axis=1)
    # 计算EV2
    df['EV2'] = df['总市值'] + df['有息负债'] - df['B_currency_fund@xbx'].fillna(0)

    # 计算EBITDA
    # 坏账损失 字段无法直接从财报中获取，暂去除不计
    df['EBITDA'] = df[[
        # 营业总收入 负债应付利息 应付手续费及佣金
        'R_operating_total_revenue@xbx', 'B_interest_payable@xbx', 'B_charge_and_commi_payable@xbx',
        # 销售费用 管理费用 研发费用 资产减值损失
        'R_sales_fee@xbx', 'R_manage_fee@xbx', 'R_rad_cost_sum@xbx', 'R_asset_impairment_loss@xbx',
        # 固定资产折旧、油气资产折耗、生产性生物资产折旧 无形资产摊销 长期待摊费用摊销
        'C_depreciation_etc@xbx', 'C_intangible_assets_amortized@xbx', 'C_lt_deferred_expenses_amrtzt@xbx',
        # 其他综合利益 流动负债合计 非流动负债合计
        'R_other_compre_income@xbx', 'B_total_current_liab@xbx', 'B_total_noncurrent_liab@xbx'
    ]].sum(axis=1) - df[
                       # 税金及附加 营业成本
                       ['R_operating_taxes_and_surcharge@xbx', 'R_operating_cost@xbx']
                   ].sum(axis=1)

    # 计算企业倍数
    df['企业倍数'] = df['EV2'] / df['EBITDA']
    extra_agg_dict['企业倍数'] = 'last'

    # 计算现金流负债比
    # 现金流负债比 = 现金流量净额(经营活动) / 总负债(流动负债合计 + 非流动负债合计)
    df['现金流负债比'] = df['C_ncf_from_oa@xbx'] / (df['B_total_current_liab@xbx'] + df['B_total_noncurrent_liab@xbx'])
    extra_agg_dict['现金流负债比'] = 'last'

    # 盈利现金比率=（经营现金净流量/净利润）*100%；该比率越大，企业盈利质量越强，该值一般大于1
    df['盈利现金比率'] = df['C_ncf_from_oa@xbx'] / df['R_np@xbx']
    extra_agg_dict['盈利现金比率'] = 'last'

    # 现金流量比率 = 经营活动现金流量÷流动负债；与行业平均水平相比进行分析
    df['现金流量比率'] = df['C_ncf_from_oa@xbx'] / df['B_total_current_liab@xbx']
    extra_agg_dict['现金流量比率'] = 'last'

    # ===计算成本营收比：（营业总成本÷营业总收入)×100%
    df['成本营收比'] = df['R_operating_total_cost@xbx'] / df['R_operating_total_revenue@xbx']
    extra_agg_dict['成本营收比'] = 'last'

    # ===计算 成本收入比_TTM= 营业总成本_TTM / 营业总收入_TTM
    df['成本收入比_TTM'] = df['R_operating_total_cost@xbx_ttm'] / df['R_operating_total_revenue@xbx_ttm']
    extra_agg_dict['成本收入比_TTM'] = 'last'

    # 净利率 = 净利润÷营业收入x100 %
    df['净利率'] = df['R_np@xbx'] / df['R_operating_total_revenue@xbx']
    extra_agg_dict['净利率'] = 'last'

    # 计算ROA
    # 总资产收益率= 净利润 / 总资产
    df['资产总额'] = df['B_total_noncurrent_assets@xbx'] + df['B_total_current_assets@xbx']
    df['总资产收益率'] = df['R_np_atoopc@xbx_ttm'] / df['资产总额']
    extra_agg_dict['总资产收益率'] = 'last'

    df['ps_ttm'] = df['总市值'] / df['R_revenue@xbx_ttm']
    extra_agg_dict['ps_ttm'] = 'last'

    # 计算资产负债率
    df['资产负债率'] = df['B_total_liab@xbx'] / df['B_total_assets@xbx']
    extra_agg_dict['资产负债率'] = 'last'

    # 计算 利润现金保障倍数
    # 利润现金保障倍数=经营现金流净额/净利润
    df['利润现金保障倍数'] = df['C_ncf_from_oa@xbx'] / df['R_np@xbx']
    extra_agg_dict['利润现金保障倍数'] = 'last'

    # 计算销售收现比例====================================
    # 销售收现比例 = 经营活动产生的现金流量的商品销售、提供劳务收到的现金 / 主营业务收入净额
    # 主营业务收入净额 = 利润表的营业总收入 - 利润表的营业总成本
    df['主营业务收入净额'] = df['R_operating_total_revenue@xbx'] - df['R_operating_total_cost@xbx']
    df['销售收现比例'] = df['C_cash_received_of_sales_service@xbx'] / df['主营业务收入净额']
    extra_agg_dict['销售收现比例'] = 'last'

    return df
```

## 3.3 Filter代码
```python
from Config import *

def filter_and_rank(df):
    """
    通过财务因子设置过滤条件
    :param df: 原始数据
    :return: 返回 通过财务因子过滤并叠加量价因子的df
    """
    # ======根据各类条件对股票进行筛选

    # 计算归母PE(ttm) 在二级行业的分位数
    # 获取归母PE(ttm) 较小 的股票
    # 归母PE(ttm)会存在负数的情况 => 先求倒数，再从大到小排序
    df['归母EP(ttm)'] = 1 / df['归母PE(ttm)']
    df['归母PE(ttm)_二级行业分位数'] = df.groupby(['交易日期', '申万二级行业名称'])['归母EP(ttm)'].rank(ascending=False, pct=True)
    condition = (df['归母PE(ttm)_二级行业分位数'] <= 0.4)

    # 计算归母PE(ttm) 在所有股票的分位数
    # 获取归母PE(ttm) 较小的股票
    # 归母PE(ttm)会存在负数的情况 => 复用之前 PE(ttm) 的倒数 EP(ttm),再从大到小排序
    df['归母PE(ttm)_分位数'] = df.groupby(['交易日期'])['归母EP(ttm)'].rank(ascending=False, pct=True)
    condition &= (df['归母PE(ttm)_分位数'] > 0.1)
    condition &= (df['归母PE(ttm)_分位数'] <= 0.4)

    # 计算归母ROE(ttm) 在所有股票的分位数
    # 获取归母ROE(ttm) 较大的股票
    df['归母ROE(ttm)_分位数'] = df.groupby(['交易日期'])['归母ROE(ttm)'].rank(ascending=False, pct=True)
    # condition &= (df['归母PE(ttm)_分位数'] > 0.1)
    # condition &= (df['归母PE(ttm)_分位数'] <= 0.4)

    # 计算企业倍数 在所有股票的分位数
    # 获取企业倍数 较小 的股票
    # 企业倍数存在负数的情况 => 先求倒数，再从大到小排序
    df['企业倍数_倒数'] = 1 / df['企业倍数']
    df['企业倍数_分位数'] = df.groupby(['交易日期'])['企业倍数_倒数'].rank(ascending=False, pct=True)
    condition &= (df['企业倍数_分位数'] <= 0.55)

    # 计算现金流负债比 在所有股票的分位数
    # 获取现金流负债比 较大 的股票
    df['现金流负债比_分位数'] = df.groupby(['交易日期'])['现金流负债比'].rank(ascending=False, pct=True)
    condition &= (df['现金流负债比_分位数'] <= 0.4)

    # 计算盈利现金比率 在所有股票的分位数
    # 获取盈利现金比率 较大 的股票
    # df['盈利现金比率_分位数'] = df.groupby(['交易日期'])['盈利现金比率'].rank(ascending=False, pct=True)
    # condition &= (df['盈利现金比率_分位数'] <= 0.4)

    # 计算销售收现比例 在所属行业的分位数
    # 获取销售收现比例 较大 的股票
    # df['销售收现比例_二级行业分位数'] = df.groupby(['交易日期', '申万二级行业名称'])['销售收现比例'].rank(ascending=False, pct=True)  # False是升序
    # condition &= (df['销售收现比例_二级行业分位数'] <= 0.4)

    df['成交额_std_10_分位数'] = df.groupby(['交易日期'])['成交额_std_10'].rank(ascending=False, pct=True)


    df['毛利率(ttm)_倒数'] = 1 / df['毛利率(ttm)']


    # 市销率大于2
    # df = df[df['ps_ttm'] >= 2]


    # condition &= (df['利润现金保障倍数'] > 1)
    condition &= (df['资产负债率'] <= 0.7)


    # 综上所有财务因子的过滤条件，选股
    df = df[condition]

    # 定义需要进行rank的因子
    # 定义需要进行rank的因子
    factors_rank_dict = {
        '归母ROE(ttm)': False,
        '总市值': True,
        '成本营收比': True,
        '成交额_std_10_分位数': False,
        '中户资金流': False,
        '现金流比': False,
        # '资产负债率': False,
        'ps_ttm': True,    # 市销率(ttm)因子，从小到大排序(市销率越低，该公司投资价值越大)
        # '换手率': True,
        # 'C_increase_of_operating_item@xbx': False,
        'bias_10': False,
        # '利润现金保障倍数': False,
        # '现金流量比率': False,
        # '净利率': True,
        # '毛利率(ttm)_倒数': True,
        '盈利现金比率': False,
        # '销售收现比例': True,
    }

    # 定义合并需要的list
    merge_factor_list = []
    # 遍历factors_rank_dict进行排序
    for factor in factors_rank_dict:
        df[factor + '_rank'] = df.groupby('交易日期')[factor].rank(ascending=factors_rank_dict[factor], method='first')
        # 将计算好的因子rank添加到list中
        merge_factor_list.append(factor + '_rank')

    # 对量价因子进行等权合并，生成新的因子
    df['因子'] = df[merge_factor_list].mean(axis=1)
    # 对因子进行排名
    df['排名'] = df.groupby('交易日期')['因子'].rank(method='first')

    # 选取排名靠前的股票
    df = df[df['排名'] <= select_stock_num]

    return df
```

# 四、策略回测表现

## 4.1 回测资金曲线
![backtesting](./figures/strategy_M.png)

## 4.2 策略回测表现
| 指标               | 表现                |
|:-------------------|:--------------------|
| 累积净值           | 204.49              |
| 年化收益           | 56.1%               |
| 最大回撤           | -39.45%             |
| 最大回撤开始时间   | 2011-05-03 00:00:00 |
| 最大回撤结束时间   | 2012-01-05 00:00:00 |
| 年化收益/回撤比    | 1.42                |
| 盈利周期数         | 97.0                |
| 亏损周期数         | 47.0                |
| 胜率               | 67.36%              |
| 每周期平均收益     | 4.22%               |
| 盈亏收益比         | 1.67                |
| 单周期最大盈利     | 60.31%              |
| 单周期大亏损       | -18.31%             |
| 最大连续盈利周期数 | 10.0                |
| 最大连续亏损周期数 | 5.0                 |

## 4.3 策略历年表现
| 交易日期   | 策略收益   | 指数收益   | 超额收益   |
|:-----------|:-----------|:-----------|:-----------|
| 2010-12-31 | 69.09%     | -2.37%     | 71.46%     |
| 2011-12-31 | -10.51%    | -25.01%    | 14.50%     |
| 2012-12-31 | 32.53%     | 7.55%      | 24.98%     |
| 2013-12-31 | 120.82%    | -7.65%     | 128.47%    |
| 2014-12-31 | 139.19%    | 51.66%     | 87.53%     |
| 2015-12-31 | 304.13%    | 5.58%      | 298.55%    |
| 2016-12-31 | 43.50%     | -11.28%    | 54.78%     |
| 2017-12-31 | 7.52%      | 21.78%     | -14.25%    |
| 2018-12-31 | -10.00%    | -25.31%    | 15.31%     |
| 2019-12-31 | 39.49%     | 36.07%     | 3.42%      |
| 2020-12-31 | 39.01%     | 27.21%     | 11.80%     |
| 2021-12-31 | 72.08%     | -5.20%     | 77.27%     |
| 2022-12-31 | 3.11%      | -1.95%     | 5.06%      |

# 五、总结
策略后期的调参很玄学，到后来基本就是数字游戏。前面很多帖子的策略我都试着复现过，包括以上的策略，基本上改动个一行信息整个策略结果就会垮掉。比如参考我引用的老板，我也加了**资产负债率 <= 0.7**的筛选，不知道是什么逻辑，并且稍微改动整个收益回撤比就直接砍半。大家也基本上就是在各种因子True, False是添加还算注释掉去尝试，以及去修改一些初始的筛选边界，整个过程就好似机器学习grid search跑最佳参数一样。

总体来说感觉还是需要和量价因子有机结合，也许在量价因子的基础上去用财务因子做一些**筛选**，而并等权重的**打分**可能更加合适。


# 六、附件内容
#### 1 策略评价附件


#### 2 相关代码
