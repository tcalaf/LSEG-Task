Task: LSEG Pre-Interview Coding Challenge
Name: Calafeteanu Tudor-Alexandru

Setup:
1. Create a 'stock_exchanges' directory in the same base directory where 'predict.py' script exists.
This will be the base data directory.
2. Move all data subdirectories ('LSE', 'NASDAQ', 'NYSE') in the 'stock_exchanges' directory.

How to run: "python3 predict.py N", where N is the specified number of files.

Output: A 'predicted_stock_exchanges' directory with the same structure as the 'stock_exchanges' directory. It will be found in the same
base directory where 'predict.py' script exists.

Assumptions:
- I assumed that if the input "N" is lower than the number of files in a subdirectory, we choose "N" files in a random order.
- I also assumed that the predicted values of the stock datapoints will be rounded to two decimals, and the rounding method is the
Python default one.

Observations:
Pandas library needs to be installed!
