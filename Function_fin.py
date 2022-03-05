import os

import numpy as np
import pandas as pd

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数


# region  财务数据处理
def mark_old_report(date_list):
    """
    标记当前研报期是否为废弃研报。
    例如，已经发布1季度报，又更新了去年的年报，则去年的年报就是废弃报告
    :param date_list:
    :param x:最近N期的财报季度
    :return:1表示为旧研报，nan表示非旧研报
    """
    res = []
    for index, date in enumerate(date_list):
        flag = 0  # 初始化返回结果，0表示为非废弃报告
        for i in sorted(range(index), reverse=True):
            # 如果之前已经有比now更加新的财报了，将now标记为1
            if date_list[i] > date:
                flag = 1
        res.append(flag)
    return res


def get_last_quarter_and_year_index(date_list):
    """
    获取上季度、上年度、以及上一次年报的索引
    :param date_list: 财报日期数据
    :return: 上季度、上年度、以及上一次年报的索引
    """
    # 申明输出变量
    last_q_index = []  # 上个季度的index
    last_4q_index = []  # 去年同期的index
    last_y_index = []  # 去年年报的index
    last_y_3q_index = []  # 去年三季度的index
    last_y_2q_index = []  # 去年二季度的index
    last_y_q_index = []  # 去年一季度的index

    no_meaning_index = len(date_list) - 1  # 无意义的索引值，（最后一行的索引）

    # 逐个日期循环
    for index, date in enumerate(date_list):
        # 首个日期时，添加空值
        if index == 0:
            last_q_index.append(no_meaning_index)
            last_4q_index.append(no_meaning_index)
            last_y_index.append(no_meaning_index)
            last_y_3q_index.append(no_meaning_index)
            last_y_2q_index.append(no_meaning_index)
            last_y_q_index.append(no_meaning_index)
            continue

        # 反向逐个遍历当前日期之前的日期
        q_finish = False
        _4q_finish = False
        y_finish = False
        _y_3q_index = False
        _y_2q_index = False
        _y_q_index = False
        for i in sorted(range(index), reverse=True):
            # 计算之前日期和当前日期相差的月份
            delta_month = (date - date_list[i]).days / 30
            delta_month = round(delta_month)
            # 如果相差3个月，并且尚未找到上个季度的值
            if delta_month == 3 and q_finish is False:
                last_q_index.append(i)
                q_finish = True  # 已经找到上个季度的值
            # 如果相差12个月，并且尚未找到去年同期的值
            if delta_month == 12 and _4q_finish is False:
                last_4q_index.append(i)
                _4q_finish = True  # 已经找到上个年度的值
            # 如果是去年4季度，并且尚未找到去年4季度的值
            if date.year - date_list[i].year == 1 and date_list[i].month == 3 and _y_q_index is False:
                last_y_q_index.append(i)
                _y_q_index = True
            # 如果是去年4季度，并且尚未找到去年4季度的值
            if date.year - date_list[i].year == 1 and date_list[i].month == 6 and _y_2q_index is False:
                last_y_2q_index.append(i)
                _y_2q_index = True
            # 如果是去年4季度，并且尚未找到去年4季度的值
            if date.year - date_list[i].year == 1 and date_list[i].month == 9 and _y_3q_index is False:
                last_y_3q_index.append(i)
                _y_3q_index = True
            # 如果是去年4季度，并且尚未找到去年4季度的值
            if date.year - date_list[i].year == 1 and date_list[i].month == 12 and y_finish is False:
                last_y_index.append(i)
                y_finish = True

            # 如果三个数据都找到了
            if q_finish and _4q_finish and y_finish and _y_q_index and _y_2q_index and _y_3q_index:
                break  # 退出寻找
        if q_finish is False:  # 全部遍历完之后，尚未找到上个季度的值
            last_q_index.append(no_meaning_index)
        if _4q_finish is False:  # 全部遍历完之后，尚未找到4个季度前的值
            last_4q_index.append(no_meaning_index)
        if y_finish is False:  # 全部遍历完之后，尚未找到去年4季度的值
            last_y_index.append(no_meaning_index)
        if _y_q_index is False:  # 全部遍历完之后，尚未找到去年4季度的值
            last_y_q_index.append(no_meaning_index)
        if _y_2q_index is False:  # 全部遍历完之后，尚未找到去年4季度的值
            last_y_2q_index.append(no_meaning_index)
        if _y_3q_index is False:  # 全部遍历完之后，尚未找到去年4季度的值
            last_y_3q_index.append(no_meaning_index)
    # 返回
    return last_q_index, last_4q_index, last_y_index, last_y_q_index, last_y_2q_index, last_y_3q_index


def get_index_data(data, index_list, col_list):
    """
    根据索引获取数据
    :param data: 输入的数据
    :param index_list: 索引值的list
    :param col_list: 需要获取的字段list
    :return:
    """
    df = data.loc[index_list, col_list].reset_index()
    df = df[df['index'] != df.shape[0] - 1]  # 删除没有意义的行
    return df


def cal_fin_data(df, flow_fin_list=[], cross_fin_list=[], discard=True):
    """
    计算财务数据的各类指标
    :param df: 输入的财务数据
    :param flow_fin_list: 流量型财务指标：净利润之类的
    :param cross_fin_list: 截面型的财务指标：净资产
    :param discard: 是否废弃财报
    :return:计算好财务指标的数据
    """

    # 数据排序
    data = df.copy()
    data.sort_values(['publish_date', 'report_date'], inplace=True)
    data.reset_index(drop=True, inplace=True)
    # 时间格式转换
    data['report_date'] = pd.to_datetime(data['report_date'], format='%Y%m%d')
    # 获取上一季度、年度的索引、上年报索引
    last_q_index, last_4q_index, last_y_index, last_y_q_index, last_y_2q_index, last_y_3q_index = \
        get_last_quarter_and_year_index(data['report_date'])

    # 计算单季度数据、ttm数据
    last_q_df = get_index_data(data, last_q_index, flow_fin_list)  # 获取上个季度的数据
    last_4q_df = get_index_data(data, last_4q_index, flow_fin_list)  # 获取去年同期的数据
    last_y_df = get_index_data(data, last_y_index, flow_fin_list)  # 获取去年4季度数据

    # ==========处理流量数据
    for col in flow_fin_list:
        # 计算当季度数据
        data[col + '_单季'] = data[col] - last_q_df[col]
        # 第一季度的单季值等于本身
        data.loc[data['report_date'].dt.month == 3, col + '_单季'] = data[col]
        # 计算累计同比数据
        data[col + '_累计同比'] = data[col] / last_4q_df[col] - 1
        minus_index = last_4q_df[last_4q_df[col] < 0].index
        data.loc[minus_index, col + '_累计同比'] = 1 - data[col] / last_4q_df[col]
        # 计算ttm数据
        data[col + '_ttm'] = data[col] + last_y_df[col] - last_4q_df[col]
        # 第四季度的ttm等于本身
        data.loc[data['report_date'].dt.month == 12, col + '_ttm'] = data[col]

    # 单季度环比、同比，ttm同比
    last_q_df = get_index_data(data, last_q_index, [c + '_单季' for c in flow_fin_list])
    last_4q_df = get_index_data(data, last_4q_index,
                                [c + '_单季' for c in flow_fin_list] + [c + '_ttm' for c in flow_fin_list])
    for col in flow_fin_list:
        # 计算单季度环比、同比
        data[col + '_单季环比'] = data[col + '_单季'] / last_q_df[col + '_单季'] - 1  # 计算当季度环比
        minus_index = last_q_df[last_q_df[col + '_单季'] < 0].index
        data.loc[minus_index, col + '_单季环比'] = 1 - data[col + '_单季'] / last_q_df[col + '_单季']  # 计算当季度环比

        data[col + '_单季同比'] = data[col + '_单季'] / last_4q_df[col + '_单季'] - 1  # 计算当季度同比
        minus_index = last_4q_df[last_4q_df[col + '_单季'] < 0].index
        data.loc[minus_index, col + '_单季同比'] = 1 - data[col + '_单季'] / last_4q_df[col + '_单季']  # 计算当季度同比
        # ttm同比
        data[col + '_ttm同比'] = data[col + '_ttm'] / last_4q_df[col + '_ttm'] - 1  # 计算ttm度同比
        minus_index = last_4q_df[last_4q_df[col + '_ttm'] < 0].index
        data.loc[minus_index, col + '_ttm同比'] = 1 - data[col + '_ttm'] / last_4q_df[col + '_ttm']  # 计算ttm度同比

    # ==========处理截面数据
    last_q_df = get_index_data(data, last_q_index, cross_fin_list)  # 获取上个季度的数据
    last_4q_df = get_index_data(data, last_4q_index, cross_fin_list)  # 获取去年4季度数据
    for col in cross_fin_list:  # 处理截面型数据

        data[col + '_环比'] = data[col] / last_q_df[col] - 1
        minus_index = last_q_df[last_q_df[col] < 0].index
        data.loc[minus_index, col + '_环比'] = 1 - data[col] / last_q_df[col]

        data[col + '_同比'] = data[col] / last_4q_df[col] - 1
        minus_index = last_4q_df[last_4q_df[col] > 0].index
        data.loc[minus_index, col + '_同比'] = 1 - data[col] / last_4q_df[col]

    # 标记废弃报告：例如已经有了1季度再发去年4季度的报告，那么4季度报告就只用来计算，不最终合并。
    if discard:
        data['废弃报告'] = mark_old_report(data['report_date'])
        # 删除废弃的研报
        data = data[data['废弃报告'] != 1]
        # 删除不必要的行
        del data['废弃报告']
    return data


def get_his_data(fin_df, data_cols, span='q'):
    """
    获取财务数据的历史数据值
    :param fin_df: 财务数据的dataframe
    :param data_cols:需要获取的列名
    :param span:事件间隔
    :return:
    """
    data = fin_df.copy()
    # 获取上一季度、年度的索引、上年报索引
    last_q_index, last_4q_index, last_y_index, last_y_q_index, last_y_2q_index, last_y_3q_index = \
        get_last_quarter_and_year_index(data['report_date'])
    if span == '4q':  # 去年同期
        last_index = last_4q_index
        label = '去年同期'
    elif span == 'y':  # 去年年报
        last_index = last_y_index
        label = '去年年报'
    elif span == 'y_q':
        last_index = last_y_q_index
        label = '去年一季度'
    elif span == 'y_2q':
        last_index = last_y_2q_index
        label = '去年二季度'
    elif span == 'y_3q':
        last_index = last_y_3q_index
        label = '去年三季度'
    else:  # 默认使用上季度
        last_index = last_q_index
        label = '上季度'

    # 获取历史数据
    last_df = get_index_data(data, last_index, data_cols)
    del last_df['index']
    # 合并数据
    data = pd.merge(left=data, right=last_df, left_index=True, right_index=True, how='left', suffixes=('', '_' + label))
    # 只输出历史数据
    new_cols = [col + '_' + label for col in data_cols]
    keep_col = ['publish_date', 'report_date'] + new_cols
    data = data[keep_col].copy()

    return data, new_cols


def import_fin_data(code, finance_data_path):
    """
    导入财务数据
    :param code:
    :param finance_data_path:
    :return:
    """
    # 股票财务数据路径
    file_path = f'{finance_data_path}/{code}'

    # 创建空df
    finance_df = pd.DataFrame()
    # 判断该股票是否存在财务数据
    if os.path.exists(file_path):
        # 获取该文件夹下的文件
        file = os.listdir(file_path)[0]
        # 读取财务数据
        finance_df = pd.read_csv(f'{file_path}/{file}', skiprows=1, encoding='gbk', parse_dates=['publish_date'])
        finance_df.sort_values(by=['publish_date', 'report_date'], inplace=True)
        finance_df.reset_index(drop=True, inplace=True)

    return finance_df


def proceed_fin_data(finance_df, raw_fin_cols, flow_fin_cols, cross_fin_cols, derived_fin_cols):
    """
    处理财务数据
    :param finance_df:
    :param raw_fin_cols:
    :param flow_fin_cols:
    :param cross_fin_cols:
    :return:
    """
    # ===选股需要的财务数据字段
    # 判断财务数据中是否包含我们需要的finance_cols，没有的话新增一列，赋值为空
    cols = raw_fin_cols + derived_fin_cols
    all_cols = finance_df.columns
    for col in cols:
        if col not in all_cols:
            finance_df[col] = np.nan

    # 选取指定的字段
    necessary_cols = ['stock_code', 'report_date', 'publish_date']
    finance_df = finance_df[set(necessary_cols + cols)]

    # ===对指定的字段，计算同比，环比，ttm等指标
    finance_df = cal_fin_data(df=finance_df, flow_fin_list=flow_fin_cols, cross_fin_list=cross_fin_cols)

    # ===数据最后处理
    # 对计算之后的财务数据进行排序
    finance_df.sort_values(by=['publish_date', 'report_date'], inplace=True)
    # 对计算之后的财务数据，根据publish_date进行去重
    finance_df.drop_duplicates(subset=['publish_date'], keep='last', inplace=True)
    # 重置索引
    finance_df.reset_index(drop=True, inplace=True)
    # 返回需要字段的财务数据

    return finance_df[['publish_date', 'report_date'] + cols]

# endregion
