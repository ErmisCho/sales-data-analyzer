# Sales Data Analyzer

A Python-based tool for analyzing sales data and generating visual reports for seller effectiveness, coverage, and unoffered products.

## Features

- **Configuration Manager**: Reads configuration settings from an external `conf.ini` file.
- **Data Loader**: Loads and validates sales data from a CSV file.
- **Data Analyzer**: Performs analysis on seller effectiveness, coverage, and unoffered products.
- **Result Generation**: Saves the results as images using `dataframe_image`.

## Prerequisites

Tested with Python 3.11.9 64-bit

# You can install the required libraries using the following command:

```bash
pip install -r requirements.txt
```

## Getting Started

1. Run the unit tests:
```bash
python unit_test.py
```
![The picture "unit_test_execution.png" was not loaded, please download separately](https://github.com/ErmisCho/sales_data_analyzer/blob/main/github_pictures/unit_test_execution.png)

2. Analyze the sales:
```bash
python sales_data_analyzer_execution.py
```
![The picture "sales_data_analyzer_execution.png" was not loaded, please download separately](https://github.com/ErmisCho/sales_data_analyzer/blob/main/github_pictures/sales_data_analyzer_execution.png)


## Expected Results
Seller Coverage: a table demonstrating which sellers approached which supermarkets
![The picture "Seller_Coverage.png" was not loaded, please download separately](https://github.com/ErmisCho/sales_data_analyzer/blob/main/results/Analysis_Results_2024-09-14_14-23-32/Seller_Coverage.png)

Seller_Effectiveness: a table demonstrating the effectiveness of each seller that approached the aforementioned supermarkets
![The picture "Seller_Effectiveness.png" was not loaded, please download separately](https://github.com/ErmisCho/sales_data_analyzer/blob/main/results/Analysis_Results_2024-09-14_14-23-32/Seller_Effectiveness.png)

Unoffered Products: a table demonstrating which products were not successfully offered to which supermarkets
![The picture "Unoffered_Products.png" was not loaded, please download separately](https://github.com/ErmisCho/sales_data_analyzer/blob/main/results/Analysis_Results_2024-09-14_14-23-32/Unoffered_Products.png)
