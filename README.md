# Stock Picking Strategies Based on Financial Factors
This project is an individual quant trading strategy research for a hedge fund manager. It builds the framework to backtest the effectiveness of a total of more than 1000 financial factors (ROE, PE, etc.) on China A-share market. These factors are basic raw data from financial statements, balance sheets, income statement..... Many "derivative" financial factors, such as TTM value, year-on-year, month-on-month, etc., are calculated manually.

**Motivation:**
Although many strategies, whatever stock picking strategies or timing strategies are constructed based on price and volume information, the real "secret" behinds a mature trading strategy must mingle with financial data information, as what the mutual fund managers do. The reason is that many digged price or volume factors rely only on pure data mining techniques and are lack of theoretical support, so that many effective factors are only useful for a short period, even less than one day, and then becomes useless. Besides, technical analysis has already been familiar and useless as the market efficiency increases. Basic financial factors are still crucial for quantitative tadings as the "core logic" if the manager wants to pursue a relatively stable long-term returns.

**Data**:
We used all stocks in the China A-share market with all historical ohlcv information to do the backtesting. Rigorously, the stocks that have been delisted by the market are still considered (this is what WIND Terminal cannot give you!). The price information is crawled from fianancial websites and updated in the database every day. The financial factor dataset is purchased and maintained by the company, containing valuable and accurate information such as the published date of the financial reports, which is crucial!! (Imagine in the platform such as JoinQuant. They will provide many financial factors as well. But say the annual report of 2021 is published at around March, 2022. Then we **cannot** use the data of 2021 from the report until March, 2022!! However in such platforms, they provide you with the data already in 2021, which may be unreliable since you are using **future information** in your backtesting!!)

Since the data is large (>4GB) and cannot be uploaded on Github, contact boyuyang@link.cuhk.edu.cn if you want to obtain the data.

**Scripts:**
- `Config.py`: state the parameter settings and financial factors that will be used
- `Functions.py`: manipulate the ohlcv information of the stock data, considering limit-up and limit-down issues, etc.
- `Functions_fin.py`: data cleaning process for financial data
- `data_process.py`: manipulate the stock data and financial data, and then merge into a HDF5 file
- `CalcFactor.py`: functions to compute financial factors, price factors, volume factors
- `Filter.py`: functions to pick the stock at the end of every trading cycle according to the calculated factors 
- `Evaluate.py`: functions to plot the result
- `visualization.py`: read the HDF5 file, calculate factor values, pick the stocks for each trading cycle, and obtain the strategy performance
- `markdown_template.md: template for generating the markdown report
- `auto_markdown.py`: automatically generate the final report according to the script `Filter.py`, 'CalcFactor.py`, 'Config.py` and the markdown template
- `Bradley_result.md`: final report for the current research strategy


**Notes:**
- The framework can be reused for further research of fianancial factors. The current achieved RoMaD is 1.42, with annually return 56.1\% and maximum drawdown -39.45\%
- If you have questions regarding any scripts or want the source data for personal use, contact boyuyang@link.cuhk.edu.cn for details
