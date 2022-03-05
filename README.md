# Stock Picking Strategies Based on Financial Factors
This project is an individual quant trading strategy research for a hedge fund manager. It builds the framework to backtest the effectiveness of a total of more than 1000 financial factors (ROE, PE, etc.) on China A-share market. These factors are basic raw data from financial statements, balance sheets, income statement..... Many "derivative" financial factors, such as TTM value, year-on-year, month-on-month, etc., are calculated manually.

**Motivation:**
Although many strategies whatever stock picking strategies or timing strategies are constructed based on price and volume information, the real "secret" behinds a mature trading strategy must mingle with financial data information, as what the mutual fund managers do. The reason is that many digged price or volume factors rely only on pure data mining techniques and are lack of theoretical support, so that many effective factors are only useful for a short period, even less than one day, and then becomes useless. Besides, technical analysis has already been familiar and useless as the market efficiency increases. Basic financial factors are still crucial for quantitative tadings as the "core logic" if the manager wants to pursue a relatively stable long-term returns.

**Data**:
We used all stocks in the China A-share market with all historical ohlcv information to do the backtesting (rigorously, the stocks that 

**Scripts:**
- Config.py: state the 



If you have questions regarding any scripts or want the source data for personal use, contact boyuyang@link.cuhk.edu.cn for details.
