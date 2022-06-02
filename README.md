# Fundamental Factors Mining and Backtesting

### Introduction
This project is an individual quant trading strategy research for a hedge fund manager. It builds a rigorous framework to backtest the effectiveness of a total of more than 1000 financial factors (ROE, PE, etc.) on the China A-share market. These factors are basic raw data from financial statements, balance sheets, income statement..... Many "derivative" financial factors, such as TTM value, year-on-year, month-on-month, etc., will be calculated manually in `CalcFactor.py`.

### Motivation
Although many strategies, whatever stock picking strategies or timing strategies are constructed based on price and volume information, the real "secret" behinds a mature trading strategy must mingle with financial data information, as what the mutual fund managers do. The reason is that many digged price or volume factors rely only on pure data mining techniques and are lack of theoretical support, so that many effective factors are only useful for an extremely short period, even less than one day, and then become useless. Besides, technical analysis has already been familiar and useless as the market efficiency increases. Basic financial factors are still crucial for quantitative tadings as the "core logic" if the manager wants to pursue a relatively stable long-term returns.

### Data
We used all stocks in the China A-share market with **all historical ohlcv information til Feb 28th, 2022** to do the backtesting. Rigorously, the stocks that have been delisted by the market are still considered (this is what WIND Terminal cannot give you!). The price information is crawled from fianancial websites and updated in the database every day. The financial factor dataset is purchased and maintained by the company, containing valuable and accurate information such as the published date of the financial reports, which is crucial!! (Imagine in the platform such as JoinQuant. They will provide many financial factors as well. But say the annual report of 2021 is published at around March, 2022. Then we **cannot** use the data of 2021 from the report until March, 2022!! However in such platforms, they provide you with the data already in 2021, which may be unreliable since you are using **future information** in your backtesting!!)

Since the data is large (>4GB) and cannot be uploaded on Github, contact boyuyang@link.cuhk.edu.cn if you want to obtain the data.

### Scripts
- `Config.py`: state the parameter settings and financial factors that will be used
- `Functions.py`: manipulate the ohlcv information of the stock data, considering limit-up and limit-down issues, etc.
- `Functions_fin.py`: data cleaning process for financial data
- `data_process.py`: manipulate the stock data and financial data, and then merge into a HDF5 file
- `CalcFactor.py`: functions to compute financial factors, price factors, volume factors
- `Filter.py`: functions to pick the stock at the end of every trading cycle according to the calculated factors 
- `Evaluate.py`: functions to plot the result
- `visualization.py`: read the HDF5 file, calculate factor values, pick the stocks for each trading cycle, and obtain the strategy performance
- `markdown_template.md`: template for generating the markdown report
- `auto_markdown.py`: automatically generate the final report according to the script `Filter.py`, `CalcFactor.py`, `Config.py` and the markdown template
- `Bradley_result.md`: final report for the current research strategy

### Results Overview
<img src="./figures/strategy_M.png" width="800">

- Performance Metrics:

| Metrics                    | Value               |
|:--------------------------:|:-------------------:|
| Cumulative Return          | 204.49              |
| Annualized Return          | 56.1%               |
| MDD                        | -39.45%             |
| MDD Begin                  | 2011-05-03 00:00:00 |
| MDD End                    | 2012-01-05 00:00:00 |
| RoMaD                      | 1.42                |
| Win Period                 | 97.0                |
| Loss Period                | 47.0                |
| Win Ratio                  | 67.36%              |
| Avg Return per Cycle       | 4.22%               |
| Calmar                     | 1.67                |
| Max Return per Cycle       | 60.31%              |
| Min Return per Cycle       | -18.31%             |
| Max Continuous Win Period  | 10.0                |
| Max Continuous Loss Period | 5.0                 |

- Annual Result:

| Trade Period (year) | Cumulative Period Return | Cumulative Return (Benchmark Index) | Excess Return |
|:-------------------:|:------------------------:|:-----------------------------------:|:-------------:|
| 2010-12-31          | 69.09%                   | -2.37%                              | 71.46%        |
| 2011-12-31          | -10.51%                  | -25.01%                             | 14.50%        |
| 2012-12-31          | 32.53%                   | 7.55%                               | 24.98%        |
| 2013-12-31          | 120.82%                  | -7.65%                              | 128.47%       |
| 2014-12-31          | 139.19%                  | 51.66%                              | 87.53%        |
| 2015-12-31          | 304.13%                  | 5.58%                               | 298.55%       |
| 2016-12-31          | 43.50%                   | -11.28%                             | 54.78%        |
| 2017-12-31          | 7.52%                    | 21.78%                              | -14.25%       |
| 2018-12-31          | -10.00%                  | -25.31%                             | 15.31%        |
| 2019-12-31          | 39.49%                   | 36.07%                              | 3.42%         |
| 2020-12-31          | 39.01%                   | 27.21%                              | 11.80%        |
| 2021-12-31          | 72.08%                   | -5.20%                              | 77.27%        |
| 2022-12-31          | 3.11%                    | -1.95%                              | 5.06%         |




### Notes
- The currently achieved RoMaD is 1.42, with annually return 56.1\% and maximum drawdown -39.45\%. We update the portfolio **monthly** (since the update for financial information is typically very slow), and choose only **three stocks** with the highest overall weighted factor values. Commission fee of 1.2bps is deducted on both sides of each transaction. The stamp duty is set to be 0.1\%. The results are shown under the folder `strategy_result`.
- The framework can be reused for further research of fianancial factors, adjust model parameters, and change the default settings
- If you have questions regarding any script or want the source data for personal use, contact boyuyang@link.cuhk.edu.cn for details
