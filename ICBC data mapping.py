import pandas as pd
import plotly.express as px

files = ["Pedestrian Crashes", "Bike Crashes"]

def collect_data():
    for filename in files:
        #open Map.csv with utf-16 encoding. tab seperated
        df = pd.read_csv(filename + ".csv", sep='\t', encoding='utf-16')
        #delete the column headers and set the first row as the column headers
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header

        df['Longitude'] = None
        df['Count'] = None

        #lat_columns are the columns not in [Latitude, Municipality, Location]

        long_columns = df.columns[~df.columns.isin(['Latitude', 'Municipality', 'Location'])]

        #iterate through each row. Set the value of df.Longitude to the value of the column that is not null
        for i in range(1, len(df)):
            for col in long_columns:
                #if not nan:
                if pd.isna(df[col][i]) == False:
                            #set df.Longitude to the value of the column that is not null
                    #set it on a view, not a copy
                    df.loc[i, 'Count'] = df[col][i]
                    df.loc[i, 'Longitude'] = col
                    print("Row {}/{}".format(i, len(df)))
                    break

        df = df[['Municipality', 'Location', 'Latitude', 'Longitude', 'Count']]

        #icbc counts crashes that occur on the border between two munis twice, i.e. there are two rows for the same intersection
        #keep only one row

        #delete duplicates IF Location	Latitude	Longitude are all the same
        df = df.drop_duplicates(subset=['Location', 'Latitude', 'Longitude'], keep='first')

        print(df)

        df.to_csv("Maps/Cleaned " + filename + ".csv")
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
                          mapbox_zoom=7)
        
        fig.write_html("Maps/Heatmap " + filename + ".html")

        #BUBBLE PLOT

        fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', 
                        size="Count",
                        mapbox_style="carto-positron",
                        hover_data=['Count', 'Location', 'Municipality', 'Label']
                        )
        
        fig.update_traces(hovertemplate=hover_template)

        fig.update_layout(title_text=filename + ", 2016-2020 (ICBC)",
                        title_x=0.5,
                        mapbox_center={"lat": 49.2827, "lon": -123.1207},
                        mapbox_zoom=7)
        
        fig.write_html("Maps/Bubble " + filename + ".html")

    return

#collect_data()

map_data()