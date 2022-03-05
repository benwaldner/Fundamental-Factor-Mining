
# !!!
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
# !!!

