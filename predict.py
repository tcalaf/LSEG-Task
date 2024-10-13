import os
import sys
import glob
import pandas as pd
import random
import re
from datetime import timedelta

BASE_DIR = "." # Relative base path
DATA_DIR_NAME = 'stock_exchanges' # Root data dir name
DATA_DIR = os.path.join(BASE_DIR, DATA_DIR_NAME) # Relative data path

# Function that prints error message
def handleError(errorMsg):
  print("[ERROR] " + errorMsg)
  sys.exit(1)

# Function that reads input
def readInput():
  # Check if the number of arguments is 1
  if (len(sys.argv) != 2):
    handleError(f"Number of arguments is not 1! Received {len(sys.argv)} instead!")
  
  # Check if input is a positive integer, denoting the number of required processed files
  if not sys.argv[1].isdigit():
    handleError(f"Argument is not an integer! Received {sys.argv[1]} instead!")
  numProcessedFiles = int(sys.argv[1])
  if numProcessedFiles != 1 and numProcessedFiles != 2:
    handleError(f"Only 1 or 2 processed files are allowed for each stock echange! Received {numProcessedFiles} instead!")

  return numProcessedFiles

# Function that returns NUM_DATA_POINTS consecutive data points starting from a random timestamp
def getRandomConsecutiveDataPoints(stockCSVFile, NUM_DATA_POINTS=10):
  # Open the stockCSVFile into pandas dataframe
  df = pd.read_csv(stockCSVFile, header=None)

  # Check that there are at least NUM_DATA_POINTS entries in the csv file
  if len(df) < NUM_DATA_POINTS:
    handleError(f"There are less than {NUM_DATA_POINTS} entries in the {stockCSVFile} file!")

  # Get a random start index for the entries
  startIdx = random.randint(0, len(df) - NUM_DATA_POINTS)

  # Return NUM_DATA_POINTS consecutive entries starting from startIdx
  return df.iloc[startIdx:startIdx+NUM_DATA_POINTS]

# Function that returns the next predicted 3 values in the timeseries data
def getPredictedDataPoints(stockCSVFile, randomDataPoints):
  # Get first (n+1) predicted datapoint - the 2nd highest value present in the randomDataPoints
  fstPredictedDataPoint = randomDataPoints[2].nlargest(2).iloc[-1]

  # Get second (n+2) predicted datapoint - half the difference between n and n+1 datapoints. Round to 2 decimals
  df = pd.read_csv(stockCSVFile, header=None)
  sndPredictedDataPoint = round(abs(df.iloc[-1][2] - fstPredictedDataPoint)/2, 2)

  # Get third (n+3) predicted datapoint - 1/4 the difference between n+1 and n+2 datapoints. Round to 2 decimals
  thrdPredictedDataPoint = round(abs(fstPredictedDataPoint - sndPredictedDataPoint)/4, 2)

  return fstPredictedDataPoint, sndPredictedDataPoint, thrdPredictedDataPoint

def createPredictedDataFrame(stockCSVFile, predictedDataPoints):
  # Get last date in the stock csv file
  df = pd.read_csv(stockCSVFile, header=None)
  stockID = df.iloc[0][0]
  lastDate = pd.to_datetime(df.iloc[-1][1], format='%d-%m-%Y')

  # Create  predicted rows for the following days
  predictedRows = []
  for i in range(0, len(predictedDataPoints)):
    date = (lastDate + timedelta(days=i+1)).strftime('%d-%m-%Y')
    predictedRows.append([stockID, date, predictedDataPoints[i]])
  
  # Create a predicted dataframe from the predicted rows array
  predictedRowsDF = pd.DataFrame(predictedRows)
  
  # Append predicted dataframe to the original dataframe and return it
  df = pd.concat([df, predictedRowsDF], ignore_index=True)
  return df

def processFiles(numProcessedFiles):
  # Check if data directory exists
  if not os.path.isdir(DATA_DIR):
    handleError(f"Data directory {DATA_DIR} does not exist!")

  # Get all csv stock files in DATA_DIR recursively
  for stockExchangeDir, _, _ in os.walk(DATA_DIR):
    # Skip base directory
    if stockExchangeDir == DATA_DIR:
      continue

    # Get an array of all stock csv files of current stock exchange subdirectory
    stockCSVRegex = os.path.join(stockExchangeDir, '*.csv')
    stockCSVFiles = glob.glob(stockCSVRegex)
    # Check if there are zero csv files in current directory
    if (len(stockCSVFiles) == 0):
      handleError(f"No CSV files in subdirectory {stockExchangeDir}!")
    # If the number of existing csv files is bigger than numProcessedFiles, take first numProcessedFiles csv files returned randomly by glob function
    if (len(stockCSVFiles) > numProcessedFiles):
      stockCSVFiles = stockCSVFiles[:numProcessedFiles]
  
    # Process each stock csv file
    for stockCSVFile in stockCSVFiles:
      # Check if csv file is empty
      if os.stat(stockCSVFile).st_size == 0:
        handleError(f"CSV file {stockCSVFile} from subdirectory {stockExchangeDir} is empty!")
      # Return 10 consecutive data points starting from a random timestamp
      randomDataPoints = getRandomConsecutiveDataPoints(stockCSVFile)
      # Return the next predicted 3 values in the timeseries data
      predictedDataPoints = getPredictedDataPoints(stockCSVFile, randomDataPoints)
      # Create the predicted dataframe
      predictedDF = createPredictedDataFrame(stockCSVFile, predictedDataPoints)
      # Create predicted CSV path
      predictedStockCSVFile = re.sub(r'stock_exchanges', 'predicted_stock_exchanges', stockCSVFile)
      os.makedirs(os.path.dirname(predictedStockCSVFile), exist_ok=True)
      # Output the predicted dataframe to CSV file
      predictedDF.to_csv(predictedStockCSVFile, index=False, header=False, float_format='%.2f')
      
if __name__ == "__main__":
  try:
    numProcessedFiles = readInput()
    processFiles(numProcessedFiles)
    sys.exit(0)
  except Exception as e:
    handleError(e)
