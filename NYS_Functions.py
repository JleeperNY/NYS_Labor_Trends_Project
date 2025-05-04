# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 15:11:20 2025

@author: Jared
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
import numpy as np

#_________________Functions____________________
#Percent Change Function
def pct_chg (n1: float | int, n2: float | int) -> float | int | pd.Series():
    if n1 == 0:
        raise ValueError("Divide by zero error! n1 is zero! Cannot continue.")
    return ((n2 - n1) / n1) * 100

#Custom analysis function to filter and graph
def graph(year1:int, year2:int, data:pd.DataFrame, sectors: list[str] | str, bymonth:bool=False,
          byregion: list[str] | str = None):
    
    # Validation of Data
    if year1 == 0:
        raise ValueError("Divide by zero error! Year 1 is zero! Cannot continue.")
    elif year2 < data["Year"].min():
        raise ValueError(f"{year1} is out of bounds!")
    elif year1 > data["Year"].max() or year2 > data["Year"].max():
        raise ValueError("A year is set for future year not yet in data.")

    if isinstance(sectors, str):
        sectors = [sectors]

    if bymonth:
        data = data[data["Month"] != 0]
    else:
        data = data[data["Month"] == 0]

    if byregion is not None:
        if isinstance(byregion, str):
            byregion = [byregion]
        data = data[data["Area Name"].isin(byregion)]
        region_str = " - " + ", ".join(byregion)
    else:
        region_str = ""

    Org_Data = data[data["Title"].isin(sectors)]
    Org_Data = Org_Data[(Org_Data["Year"] >= year1) & (Org_Data["Year"] <= year2)]
    Org_Data = Org_Data.groupby(["Year", "Title"])["Current Employment"].mean().reset_index()
    Org_Data2 = Org_Data.pivot(index="Year", columns="Title", values="Current Employment").fillna(0)
    print(Org_Data.shape)
    
    #Plot info
    fig, ax = plt.subplots()
    for col in Org_Data2.columns:
        ax.plot(Org_Data2.index, Org_Data2[col], marker='o', linewidth=2, label=col)

    red_patch = None
    if byregion and "New York State" in byregion and not (year2 < 1990 or year1 > 1999):
        span_start = max(year1, 1990)
        span_end = min(year2, 1999)
        ax.axvspan(span_start, span_end, color='red', alpha=0.1)
        red_patch = Patch(facecolor='red', alpha=0.1, label="Partial Data (1990–1999)")

    handles, labels = ax.get_legend_handles_labels()
    if red_patch:
        handles.append(red_patch)
        labels.append("Partial Data")

    if bymonth:
        ax.set_title(f"Employment Trends by Sector {region_str}")
        ax.set_ylabel("Average of Monthly Employment")
    else:
        ax.set_title(f"Employment Trends by Sector {region_str}")
        ax.set_ylabel("Estimate of Annual Employment")

    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    ax.ticklabel_format(style='plain', axis='y')
    ax.legend(handles=handles, labels=labels, title="Industry")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Year")
    ax.grid(True)
    plt.tight_layout()
    plt.show()

#A helper to shorten names
def make_short(label: str) -> str:
    overrides = {
        "Buffalo-Cheektowaga-Niagara Falls Metro Area": "Buffalo MA",
        "Kiryas Joel-Poughkeepsie-Newburgh NY": "KJP-Newburgh"}
    if label in overrides:
        return overrides[label]
    s = label.replace(" County", "").replace(" Metro Area", " MA")
    return s[:12].rstrip() + "…" if len(s) > 12 else s

def to_map(data: pd.DataFrame, GeoData: gpd.GeoDataFrame, year_start: int, year_end: int, sectors: list[str] | str = None,
           output_file: str = "NYS_Regions_Map.gpkg") -> gpd.GeoDataFrame:
    
    #Handle sectors as a list if just a single string is passed
    if isinstance(sectors, str):
        sectors = [sectors] 
    if sectors:
        data = data[data["Title"].isin(sectors)]
    
    #Preparing Map Data to export
    
    data_agg = data.groupby(["Area Name", "Title", "Year"])["Current Employment"].mean().reset_index()
    geopivot = data_agg.pivot(index=["Area Name", "Title"], columns="Year", values="Current Employment")
    print(f"Pivoted Areas: {len(geopivot)}")
    
    colname = f"Pct_Change_{year_start}_{year_end}"
    
    with np.errstate(divide='ignore', invalid='ignore'):
        geopivot[colname] = ((geopivot[year_end] - geopivot[year_start]) / geopivot[year_start]) * 100
        geopivot[colname] = geopivot[colname].round(2)
        geopivot.loc[(geopivot[year_start] == 0) | (geopivot[year_start].isna()), colname] = None
        

    geopivot = geopivot.reset_index()
    geopivot["Area Name"] = geopivot["Area Name"].str.strip()
    geopivot["Sector"] = geopivot["Title"].str.strip()
    geopivot = geopivot.pivot(index="Area Name", columns="Sector", values=colname)
    geopivot = geopivot.reset_index()
    geopivot = geopivot.rename(columns={s: f"{s}_{colname}" for s in geopivot.columns if s != "Area Name"})
    GeoData["Area Name"] = GeoData["Area Name"].str.strip()

    #To merge and label
    GeoMerge = GeoData.merge(geopivot, on="Area Name", how="left")
    # Identify rows with no data
    def label_logic(row):
        if row.drop("geometry").isna().all():
            return f"No Data ({year_start})"
        return make_short(row["Area Name"])
    GeoMerge["Label_Text"] = GeoMerge.apply(label_logic, axis=1)
    GeoMerge["Label_Text"] = GeoMerge["Area Name"].apply(make_short)

    agg_fields = {col: "first" for col in GeoMerge.columns if col != "geometry"}
    dissolved = GeoMerge.dissolve(by="Area Name", aggfunc=agg_fields)
    dissolved = dissolved.reset_index(drop=True)

    dissolved.to_file(output_file, layer="regions", driver="GPKG")
    print(f".gpkg file saved to {output_file}")
    return dissolved

def sector_pct_change(year1:int, year2:int, data:pd.DataFrame, sectors: list[str] | str, bymonth:bool=False,
          byregion: list[str] | str = None, to_DataFrame:bool=False, to_csv:bool=False):
    
    # Validation of Data
    if year1 == 0:
        raise ValueError("Divide by zero error! Year 1 is zero! Cannot continue.")
    elif year2 < data["Year"].min():
        raise ValueError(f"{year1} is out of bounds!")
    elif year1 > data["Year"].max() or year2 > data["Year"].max():
        raise ValueError("A year is set for future year not yet in data.")
    if isinstance(sectors, str):
        sectors = [sectors]
    if byregion and isinstance(byregion, str):
        byregion = [byregion]
    if byregion:
            data = data[data["Area Name"].isin(byregion)]
    if bymonth:
        data = data[data["Month"] != 0]
    else:
        data = data[data["Month"] == 0]
        
    #Filter
    filtered = data[data["Title"].isin(sectors)]
    filtered = filtered[(filtered["Year"] == year1) | (filtered["Year"] == year2)]
    
    #To Aggregate
    grouped = (filtered.groupby(["Year", "Title"])["Current Employment"].mean()
        .unstack(level=0))

    sector_str = ", ".join(sectors)
    region_str = ", ".join(byregion) if byregion else "All Regions"
    print(f"\nPercent Change in Employment in {sector_str} for {region_str} ({year1} → {year2})\n")

    for sector in grouped.index:
        try:
            n1 = grouped.at[sector, year1]
            n2 = grouped.at[sector, year2]
            if pd.isna(n1) or pd.isna(n2) or n1 == 0:
                result = "N/A (missing data)"
            else:
                change = ((n2 - n1) / n1) * 100
                result = f"{change:.1f}%"
        except KeyError:
            result = "N/A (year missing)"
        print(f"Sector: {sector:<20} {result}")
        
    #Optional DataFrame output
    if to_DataFrame or to_csv:
        results = []
        for sector in grouped.index:
            try:
                n1 = grouped.at[sector, year1]
                n2 = grouped.at[sector, year2]
                if pd.isna(n1) or pd.isna(n2) or n1 == 0:
                    pct = None
                    result_str = "N/A (missing data)"
                else:
                    pct = ((n2 - n1) / n1) * 100
                    result_str = f"{pct:.1f}%"
            except KeyError:
                result_str = "N/A (year missing)"
                pct = None
            
            results.append({"Sector": sector, f"Pct_Change_{year1}_{year2}": pct, 
                            f"Note_{year1}_{year2}": result_str})
            
        df_out = pd.DataFrame(results)
                
        if to_csv:
                filename = f"sector_pct_change_{year1}_{year2}.csv"
                df_out.to_csv(filename, index=False)
                print(f"\nCSV saved to {filename}")
        if to_DataFrame:
                print(f"\nDataFrame returned with {len(df_out)} rows.")
                return df_out

def list_sectors(data: pd.DataFrame, filterby: str = None, startswith: str = None) -> list[str]:
    sectors = data["Title"].dropna().unique().tolist()
    if filterby:
        sectors = [s for s in sectors if filterby.lower() in s.lower()]
    if startswith:
        sectors = [s for s in sectors if s.lower().startswith(startswith.lower())]
    return sorted(sectors)