import pandas as pd
import plotly.express as px

files = ["Pedestrian Crashes", "Bike Crashes"]

def collect_data():
    import os

    for filename in files:
        #open Map.csv with utf-16 encoding. tab seperated
        df = pd.read_csv(filename + ".csv", sep='\t', encoding='utf-16')
        #delete the column headers and set the first row as the column headers
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header

        #lat_columns are the columns not in [Latitude, Municipality, Location]

        long_columns = df.columns[~df.columns.isin(['Latitude', 'Municipality', 'Location'])]

        df = pd.melt(df, id_vars=['Latitude', 'Municipality', 'Location'], value_vars=long_columns, var_name='Longitude', value_name='Count')
        df.dropna(subset=['Count'], inplace=True)
        
        df.to_csv("Cleaned " + filename + ".csv", index=False)

    return

def map_data():

    for filename in files:
        df = pd.read_csv("Cleaned " + filename + ".csv")
        df.dropna(inplace=True)

        #set count to be int
        df["Count"] = df["Count"].astype(int)

        df["Label"] = None

        def create_label(count):
            if count == 1:
                return "1 " + filename[:-2]
            else:
                return " {} {}".format(count, filename)
        
        df["Label"] = df["Count"].apply(create_label)

        df['Location'] = df['Location'].str.title()
        df['Municipality'] = df['Municipality'].str.title()

        #create hover template showing location, count, and municipality
        hover_template = """
        <b>%{customdata[1]}</b><br>
        %{customdata[2]}<br>
        %{customdata[3]}"""
        
        config = {'scrollZoom': True}
        
        #HEATMAP

        fig = px.density_mapbox(df, lat='Latitude', lon='Longitude', z='Count', radius=10,
                                mapbox_style="carto-positron",
                                #scale values = 25 is very bright, 0 is very dark
                                range_color=(0, 15),
                                #custom hover data
                                custom_data=['Count', 'Location', 'Municipality', 'Label']
                        )

        fig.update_traces(hovertemplate=hover_template)

        fig.update_layout(title_text=filename + ", 2016-2020 (ICBC)",
                          title_x=0.5,
                          mapbox_center={"lat": 49.2827, "lon": -123.1207},
                          mapbox_zoom=7,
                          margin={"r":0,"t":0,"l":0,"b":0})
        #set margins to 0

        fig.write_html("Maps/Heatmap " + filename + ".html", config=config)

        #BUBBLE PLOT

        fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', 
                        size="Count",
                        mapbox_style="carto-positron",
                        hover_data=['Count', 'Location', 'Municipality', 'Label'],
                        color_discrete_sequence=['red'],
                        opacity=0.65
                        )
        
        fig.update_traces(hovertemplate=hover_template)

        fig.update_layout(title_text=filename + ", 2016-2020 (ICBC)",
                        title_x=0.5,
                        mapbox_center={"lat": 49.2827, "lon": -123.1207},
                        mapbox_zoom=7,
                        margin={"r":0,"t":0,"l":0,"b":0})
        
        fig.write_html("Maps/Bubble " + filename + ".html", config=config)

    return

#collect_data()

map_data()