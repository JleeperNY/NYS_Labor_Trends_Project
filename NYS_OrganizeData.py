import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

#Bringing in a dataset; Current Employment by Industry (CES) data reflects jobs by "place of work."
Data1 = pd.read_csv('Current_Employment_Statistics__Beginning_1990_20250416.csv')
#State of New York Shape and New York Counties files
shapes = gpd.read_file('cb_2023_us_county_5m.zip').query("STATEFP == '36'")

#Filtering Data1 for instances where the "Title" columns contains an industry
#as listed above
Data_2 = Data1.sort_values(["Year", "Month"]).copy()
Data_2["Year"] = Data_2["Year"].astype(int)
#County Level Editor, using .tolist() as opposed to .to_list() because the output is a NumPy array
non_c_filter = Data_2[Data_2['Area Name'].str.endswith(("Division", "City", 'Area', 'NY', "State"))]['Area Name'].unique().tolist()
#print(non_c_filter)

nyc_counties = [
    "New York County", "Kings County", "Bronx County", "Queens County", "Richmond County"]
glens_falls_metro_counties = ["Warren County","Washington County"]
Long_Island = ["Nassau County","Suffolk County"]
Albany_Metro = ["Albany County","Rensselaer County","Saratoga County","Schenectady County",
    "Schoharie County"]
Bing_Metro = ["Broome County","Tioga County"]
Buff_Niagara_Metro = ["Erie County","Niagara County"]
SYRMA = ["Onondaga County","Madison County","Oswego County"]
Utica_RomeMA= ["Oneida County","Herkimer County"]
RochesterMA= ["Monroe County","Livingston County","Ontario County","Orleans County",
    "Wayne County"]
KJPNewburgh=["Dutchess County","Orange County"]

mapping_info = {
    **{county: "New York City" for county in nyc_counties},
    **{"Chemung County" : 'Elmira Metro Area'},
    **{county : 'Glens Falls Metro Area' for county in glens_falls_metro_counties},
    **{'Tompkins County' :'Ithaca Metro Area'},
    **{county :'Nassau-Suffolk Metropolitan Division' for county in Long_Island},
    **{'Ulster County' : 'Kingston Metro Area'},
    **{county: 'Albany-Schenectady-Troy Metro Area' for county in Albany_Metro}, 
    **{county:'Binghamton Metro Area' for county in Bing_Metro},
    **{county:'Buffalo-Cheektowaga-Niagara Falls Metro Area' for county in Buff_Niagara_Metro},
    **{county: 'Syracuse Metro Area' for county in SYRMA},
    **{county: 'Utica-Rome Metro Area' for county in Utica_RomeMA},
    **{"Jefferson County" : 'Watertown-Fort Drum Metro Area'},
    **{county:'Rochester Metro Area' for county in RochesterMA},
    **{county:'Kiryas Joel-Poughkeepsie-Newburgh NY' for county in KJPNewburgh},
    **{"Yates County": "Yates County"},
    **{"Rockland County": "Rockland County"},
    **{"Putnam County": "Putnam County"},
    **{"Westchester County": "Westchester County"}
    }

Data_2["Area Name"] = Data_2["Area Name"].replace(mapping_info)
Data_2.to_csv("GoodData.csv", index=False)
#Modifying Shape file
shapes_2 = shapes.copy()
shapes_2["NAMELSAD"] = shapes["NAMELSAD"].replace(mapping_info)
#Renaming columns
shapes_3 = shapes_2.rename(columns={"NAMELSAD" : 'Area Name'})
shapes_3["GEOID"] = shapes_3["GEOID"].astype(str)
shapes_3.to_file("my_shapes.gpkg")
#Apply mapping to the table too

