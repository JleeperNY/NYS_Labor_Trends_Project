# NYS Labor Market Trends Analysis

This project visualizes employment trends across New York State. The dataset is Current Employment Statistics from New York State, starting in 1990 and as of this project, going to March of 2025. It tracks number of employees on the payroll in a variety of industries. While the initial focus of this project was on the decline of the manufacturing sector, this project supports any sector in the dataset. While the New York State Department of Labor also has a tool for this, this distinguished itself in it's focus on having the option of map data, and the option to graph it.

# Files

I am including the shape files, for the US, broken down by county level, as well as the inital input data. The script NYS_OrganizeData.py will filter the data and shape file for quick use by the other scripts.

## Data Structure

The initial data set was found at https://data.ny.gov/Economic-Development/NY-Employment-data/xn25-vtv7/about_data

- **Geography**: 43 labor market regions (not all 62 NYS counties). These are 42 divisions, which are counties, metropolitan statistical areas, all aligining to combinations of counties,
and then a 43rd area for the whole state of New York. In the short labels for maps, "MA" stands for Metropolitan Area.

- **Titles**: What is commonly called a sector, is structured per BLS standards:
  - Goods-Producing
    - Manufacturing
        - (Sub-sectors) 
    - Mining, Logging and Construction
        - Mining and Logging
        - Construction
  - Service-Providing
    - (Multiple sub-sectors)
- **Time Data**
    - Months 0-12 are in the dataset, where month 0 represents annual data. This is dropped or filtered out depending on whether annual data is being examined.

## Key Questions This Project Can Help to Explore

- What kinds of jobs are people in the Syracuse Metro area holding?
- What happened to the Information sector in Binghamton?
- Were 1990s job losses mostly from the Goods-Producing sector?
- Is non-manufacturing employment dominating NYC?

## How to Use

To run fast analysis of the data, you can use the provied functions to plug in years, your data set, sectors (as found in the "titles" column), monthly breakdown and region breakdown.
Make sure your have all the libraries the script calls to import.

## Functions File

### Graph Function

```python
graph(year1, year2, data, sectors, bymonth=False, byregion=None)
```
year1, year2: As integers.

data: A pandas.DataFrame of cleaned employment data.

sectors: String or list of sectors to analyze.

bymonth: Use monthly data if True.

byregion: Filter for one or more regions.

```python
sector_pct_change(1998, 2006,
    data=my_df,
    sectors=["Manufacturing", "Construction"],
    byregion="Rochester Metro Area",
    to_csv=True)
```
- It can handle divide-by-zero and missing data gracefully (returns "N/A").

- If to_csv and to_DataFrame are both set, both the export and return will occur.

- It can ensure column names match: 'Year', 'Title', 'Current Employment', 'Area Name'.

### Map Function
```python
to_map(data, GeoData, 1998, 2006, sectors=["Manufacturing", "Government"])
```
This generates a .gpkg with percent changes in employment. Each selected sector becomes a column:
Manufacturing_Pct_Change_1998_2006
Government_Pct_Change_1998_2006

### Sector Percent Change Function
```python
sector_pct_change(year1: int, year2: int, data: pd.DataFrame, sectors: list[str] | str,
                  bymonth: bool = False, byregion: list[str] | str = None,
                  to_DataFrame: bool = False, to_csv: bool = False)
```
### List Sectors Function with Filter

The following function allows users to list all unique sectors in the dataset, with an optional 
`filterby` string to search for matches. It is typically called from the module as `alias.list_sectors(...)`.

```python
def list_sectors(data: pd.DataFrame, filterby: str = None) -> list[str]:
    sectors = data["Title"].dropna().unique().tolist()
    if filterby:
        sectors = [s for s in sectors if filterby.lower() in s.lower()]
    return sorted(sectors)
```

#### Example Usage

```python
import NYS_Functions as alias

# List all sectors
alias.list_sectors(data)

# List only those containing the word "manu" (case-insensitive)
alias.list_sectors(data, filterby="manu")
```
Would return something like:
```python
['Manufacturing']
```


Parameters
year1 and year2: Start and end years as integers
data: as a pandas DataFrame
sectors	str or list[str]: Sector(s) to analyze (e.g., "Construction" or ["Construction", "Government"])
bymonth	bool, default False: If True, uses monthly data (non-zero months only)
byregion: str or list[str]: Filter by one or more region names
to_DataFrame: bool, default False and if True, returns result as a DataFrame
to_csv: bool, default False and if True, saves result to CSV file

Output
- Console printout of percent change by sector
- Optional .csv file (e.g., sector_pct_change_1998_2006.csv)
- Optional return: pandas DataFrame of results

Sample code with DataFrame display:
```python
#Define parameters
year_start = 1998
year_end = 2006
selected_sectors = ["Manufacturing", "Construction"]
selected_region = "Rochester Metro Area"

#Run function and store result as DataFrame
df_result = alias.sector_pct_change(
    year1=year_start,
    year2=year_end,
    data=data,  # your main employment DataFrame
    sectors=selected_sectors,
    byregion=selected_region,
    to_DataFrame=True)
# Display DataFrame
print(df_result)
```

# Notes
Regions with missing data (e.g., 1990s) will show NULL.

Label_Text is always derived from geography, not employment data.

Graphs will highlight 1990–1999 partial coverage in red when "New York State" is selected.

# *Known Data Gaps*
Missing 1990–1999 data:
Yates County, Putnam County, Rockland County, Westchester County

Construction Data:
Only available for Rochester Metropolitan Area and New York State.
To determine this, the following line was used, there "data" holds my filtered dataset and looks for the sector in the column called "Title"
in non-annual data and by only the areas where it appears, as stored in the "Area Name" column.
```python
print(data[(data["Title"] == "Construction") & (data["Month"] != 0)]["Area Name"].unique())
```

## Data Valdidation Code

- To validate that the column names are present, makesure the output file name
  and the file being read match.
```python
gdf = gpd.read_file("FileName.gpkg")
print(gdf.columns.to_list())
```

- To ensure that 'New York State' gets removed from
```python
csv_names = set(pd.read_csv('YourData.csv')['Area Name'].unique())
shape_names = set(YourGeoData['Area Name'].unique())
missing_in_shapes = csv_names - shape_names
print(f"Area Names in CSV but missing in my_shapesfile.gpkg:, {missing_in_shapes}")
```

# QGIS Labeling Guide
Step 1: Load the Layer
Open YourMap.gpkg in QGIS.

Step 2: Rule-Based Labeling
Right-click layer → Properties → Labels tab.

Step 3: Choose "Rule-based labeling".

Step 4: Add Custom Rule
Use this filter for regions with no data:

```sql
"Area Name" IN ('Yates County', 'Rockland County', 'Putnam County', 'Westchester County')
```
In the Label field, set the text to: No Data (1990)
Style: Set style according to preferences and clarity. You can add a text buffer.

Export Tips
If your image is getting cut off:
Adjust the size
Use Layout Manager → Export as Image.
Be careful with saving as .svg, as of 5/3/2025, it doesn't work very well.
Set Export resolution (DPI) to 300+.

# Sample Map
https://github.com/JleeperNY/NYS_Labor_Trends_Project/blob/2a9badb0cfe34c2b3c3cb3b081e7ed8901b14029/Sample%20Map%20Legend.png