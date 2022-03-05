from Evaluate import *
from Filter import *
from Functions import *
import warnings

warnings.filterwarnings('ignore')

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数

print('策略名称:', strategy_name)
print('周期:', period_type)

# ===导入数据
# 从pickle文件中读取整理好的所有股票数据
df = pd.read_pickle(root_path + '\\financial_factor_stock_picking\\data\\output\\选股策略\\all_stock_data_%s.pkl' % period_type)
df.dropna(subset=['下周期每天涨跌幅'], inplace=True)
# 导入指数数据
index_data = import_index_data(root_path + '\\financial_factor_stock_picking\\data\\index_data\\sh000300.csv', back_trader_start=date_start,
                               back_trader_end=date_end)

# 创造空的事件周期表，用于填充不选股的周期
empty_df = create_empty_data(index_data, period_type)

# ===删除新股
df = df[df['上市至今交易天数'] > 250]

# ===删除下个交易日不交易、开盘涨停的股票，因为这些股票在下个交易日开盘时不能买入。
df = df[df['下日_是否交易'] == 1]
df = df[df['下日_开盘涨停'] == False]
df = df[df['下日_是否ST'] == False]
df = df[df['下日_是否退市'] == False]

df

# ========只需要修改 filter_and_choose 函数============
df = filter_and_rank(df)
# ===================================================

df

# ===选股
# ===按照开盘买入的方式，修正选中股票在下周期每天的涨跌幅。
# 即将下周期每天的涨跌幅中第一天的涨跌幅，改成由开盘买入的涨跌幅
df['下日_开盘买入涨跌幅'] = df['下日_开盘买入涨跌幅'].apply(lambda x: [x])
df['下周期每天涨跌幅'] = df['下周期每天涨跌幅'].apply(lambda x: x[1:])
df['下周期每天涨跌幅'] = df['下日_开盘买入涨跌幅'] + df['下周期每天涨跌幅']

# ===整理选中股票数据
# 挑选出选中股票
df['股票代码'] += ' '
df['股票名称'] += ' '
group = df.groupby('交易日期')
select_stock = pd.DataFrame()
select_stock['股票数量'] = group['股票名称'].size()
select_stock['买入股票代码'] = group['股票代码'].sum()
select_stock['买入股票名称'] = group['股票名称'].sum()

# 计算下周期每天的资金曲线
select_stock['选股下周期每天资金曲线'] = group['下周期每天涨跌幅'].apply(lambda x: np.cumprod(np.array(list(x)) + 1, axis=1).mean(axis=0))
# x = df.iloc[:3]['下周期每天涨跌幅']
# print()
# print(x)
# print(list(x))  # 将x变成list
# print(np.array(list(x)))  # 矩阵化
# print(np.array(list(x)) + 1)  # 矩阵中所有元素+1
# print(np.cumprod(np.array(list(x)) + 1, axis=1))  # 连乘，计算资金曲线
# print(np.cumprod(np.array(list(x)) + 1, axis=1).mean(axis=0))  # 连乘，计算资金曲线

# 扣除买入手续费
select_stock['选股下周期每天资金曲线'] = select_stock['选股下周期每天资金曲线'] * (1 - c_rate)  # 计算有不精准的地方
# 扣除卖出手续费、印花税。最后一天的资金曲线值，扣除印花税、手续费
select_stock['选股下周期每天资金曲线'] = select_stock['选股下周期每天资金曲线'].apply(
    lambda x: list(x[:-1]) + [x[-1] * (1 - c_rate - t_rate)])

# 计算下周期整体涨跌幅
select_stock['选股下周期涨跌幅'] = select_stock['选股下周期每天资金曲线'].apply(lambda x: x[-1] - 1)
# 计算下周期每天的涨跌幅
select_stock['选股下周期每天涨跌幅'] = select_stock['选股下周期每天资金曲线'].apply(
    lambda x: list(pd.DataFrame([1] + x).pct_change()[0].iloc[1:]))
del select_stock['选股下周期每天资金曲线']

# 将选股结果更新到empty_df上
empty_df.update(select_stock)
select_stock = empty_df

# 计算整体资金曲线
select_stock.reset_index(inplace=True)
select_stock['资金曲线'] = (select_stock['选股下周期涨跌幅'] + 1).cumprod()
print(select_stock.tail())

# ===计算选中股票每天的资金曲线
# 计算每日资金曲线
equity = pd.merge(left=index_data, right=select_stock[['交易日期', '买入股票代码']], on=['交易日期'],
                  how='left', sort=True)  # 将选股结果和大盘指数合并

equity['持有股票代码'] = equity['买入股票代码'].shift()
equity['持有股票代码'].fillna(method='ffill', inplace=True)
equity.dropna(subset=['持有股票代码'], inplace=True)
del equity['买入股票代码']
equity['涨跌幅'] = select_stock['选股下周期每天涨跌幅'].sum()
equity['equity_curve'] = (equity['涨跌幅'] + 1).cumprod()
equity['benchmark'] = (equity['指数涨跌幅'] + 1).cumprod()

# ===计算策略评价指标
rtn, year_return, month_return = strategy_evaluate(equity, select_stock)
print(rtn)
print(rtn.loc['年化收益/回撤比'])
print(year_return)
rtn.to_csv(root_path + '\\financial_factor_stock_picking\\data\\output\\策略结果\\策略评价_%s.csv' % period_type, encoding='gbk')
year_return.to_csv(root_path + '\\financial_factor_stock_picking\\data\\output\\策略结果\\策略评价_year_%s.csv' % period_type, encoding='gbk')

# # ===画图
equity = equity.reset_index()
draw_equity_curve_mat(equity, data_dict={'策略表现': 'equity_curve', '基准涨跌幅': 'benchmark'}, date_col='交易日期')
plt.savefig(root_path + '\\financial_factor_stock_picking\\figures\\strategy_%s.jpg' % period_type, dpi=600)
plt.show()

# 如果上面的函数不能画图，就用下面的画图
# plotlt生成HTML

# draw_equity_curve_plotly(equity, data_dict={'策略涨跌幅': 'equity_curve', '基准涨跌幅': 'benchmark'}, date_col='交易日期', path=root_path + '\\financial_factor_stock_picking\\figures\\strategy_%s.html'% period_type)