Company Efficiency Analysis (N & M Metrics)

A Python program for calculating and visualizing cost dynamics and sales efficiency based on historical data from CSV files. 
The software analyzes company financial indicators from 2008 to 2025.

Problem Description

The script reads a company database and calculates two key parameters for assessing business financial performance:

1. **Parameter N (Cost Growth)**: Reflects the change in absolute company costs (difference between revenue and profit) year-over-year.

2. **Parameter M (Efficiency Coefficient)**: Shows the ratio of revenue growth to cost growth. 
Reveals how much additional revenue each unit of invested costs generates.

Mathematical Model

For each pair of consecutive years ($t-1$ and $t$), the following metrics are calculated:

**Costs**: $Costs = Sales - Profit$

**X-axis (N)**: 
$$N = (Sales_t - Profit_t) - (Sales_{t-1} - Profit_{t-1})$$

**Y-axis (M)**: 
$$M = \frac{Sales_t - Sales_{t-1}}{N}$$

**Functionality**

**Flexible selection**: User enters company name manually
**Dynamic range**: Data filtering within the 2008–2025 interval
**Error handling**: Protection against division by zero and missing data for specific years
**Visualization**: Generation of interactive graphs (Scatter Plot with trend lines) with period labels"
