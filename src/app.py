import plotly.express as px
import geopandas as gpd                         #pip install geopandas
import json
import plotly.graph_objects as go               # pip install plotly
from dash import Dash, dcc, Output,html, Input  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import pandas as pd                        # pip install pandas
from geopy.geocoders import Nominatim       # pip install geopy
import dash_vega_components as dvc                                    # pip install dash_vega_components
import altair as alt                        # pip install altair


point_size = 20
# Alexis datasets
shelters = pd.read_pickle('../clean_datasets/shelters.pkl')
shelters_loc = pd.read_pickle('../clean_datasets/shelters_locations.pkl')
indvd_year = pd.read_pickle('../clean_datasets/graph_bars-and-pies_df.pkl')
indvd_total_per_month_pred = pd.read_pickle('../clean_datasets/shelters_prediction.pkl')
mw = pd.read_pickle('../clean_datasets/minimum_wage.pkl')
apts_tdy = pd.read_pickle('../clean_datasets/apts_tdy.pkl')

# to incorporate Kevins
neighbourhood_loc = gpd.read_file("../clean_datasets/OPS_Neighbourhoods_Open_Data.geojson")
neighbourhood_dic = neighbourhood_loc.set_index("namese2016").geometry

df_categ = pd.read_pickle('../clean_datasets/Criminal_Offences_clean_by_categ.pkl')
df = pd.read_pickle("../clean_datasets/Criminal_Offences_clean_full.pkl")
police_centers = pd.read_pickle("../clean_datasets/police_centers.pkl")
hospitals_clusters = pd.read_pickle("../clusters/hospitals_clusters.pkl")
hospitals_dbscan = pd.read_pickle("../clusters/hospitals_dbscan.pkl")
police_clusters = pd.read_pickle("../clusters/police_clusters")

df = df[df.YEAR > 2015]
df_categ = df_categ[df_categ.YEAR > 2015]

hospitals = pd.read_pickle("../clean_datasets/hospitals.pkl")

# to incorporate overdoses
overdose_calls = pd.read_csv('../clean_datasets/Overdose_calls.csv')
opioid_related_deaths= pd.read_csv('../clean_datasets/overdose_related_deaths.csv')
overdose_emergency_month = pd.read_csv('../clean_datasets/overdose_emergency_visits_by_month.csv')


# Build your components
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    )
server = app.server
mytitle = dcc.Markdown(children='')
mygraph = dcc.Graph(figure={})
individuals_graph=dvc.Vega(id="altair-chart1", opt={"renderer": "svg", "actions": False}, spec={})
shelters_graph=dvc.Vega(id="altair-chart2", opt={"renderer": "svg", "actions": False}, spec={})
inflation_graph=dvc.Vega(id="altair-chart2bis", opt={"renderer": "svg", "actions": False}, spec={})
overdose_calls_year=dvc.Vega(id="altair-chart3", opt={"renderer": "svg", "actions": False}, spec={})
overdose_deaths_year=dvc.Vega(id="altair-chart4", opt={"renderer": "svg", "actions": False}, spec={})
overdose_emergency_year=dvc.Vega(id="altair-chart5", opt={"renderer": "svg", "actions": False}, spec={})
dropdown = dcc.Dropdown(options=['All Clients', 'All Singles', 'Family Household Members', 'Family Member', 'Offsite/Overflow Singles', 'Mens Shelter',
                                 'Womens Shelter', 'Mixed-Gender', 'Youth Shelter', 'Single Adult Males', 'Single Adult Females',
                                 'Single Youth 18 Under', 'Family Units', 'Family Households'],
                        value='All Clients',  # initial value displayed when page first loads
                        clearable=False)
# Add own CSS
# dropdown =dcc.Slider(2016, 2022, 1,
#                value=2022,
#                id='my-slider')
dropdown2 = dcc.Dropdown(options=['All','2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021','2023', '2022'],
                        value='All',  # initial value displayed when page first loads
                        clearable=False)

dropdown3 = dcc.Dropdown(options=['All',"Empty Map",'Assaults', 'Break and Enter', 'Fraud', 'Mischief',
       'Offensive Weapons', 'Other Criminal Code',
       'Other Violations Involving Violence Or The Threat Of Violence',
       'Possession / Trafficking Stolen Goods', 'Theft $5000 and Under',
       'Theft - Motor Vehicle', 'Theft Over $5000',
       'Violations Causing Death',
       'Violations Resulting In The Deprivation Of Freedom', 'Arson',
       'Attempting The Commission Of A Capital Crime',
       'Operation while Impaired/Low Blood Drug Concentration Violations',
       'Possession', 'Trafficking', 'Operation while Prohibited',
       'Gaming and Betting', 'Failure to Stop after Accident',
       'Distribution', 'Failure or Refusal to Comply with Demand',
       'Dangerous Operation', 'Flight From Peace Officer',
       'Commodification Of Sexual Activity', 'Prostitution',
       'Other Cannabis Violations', 'Production', 'Sale'],
                        value='All',  # initial value displayed when page first loads
                        clearable=False)
dropdown4 = dcc.Dropdown(options=['By days - (2017-2022)',"By days - before Covid",'By days - after Covid', 'By day of the week - (2017-2022)', 'By month - (2017-2022)'],
                        value='By days - (2017-2022)',  # initial value displayed when page first loads
                        clearable=False)
dropdown5 = dcc.Dropdown(options=['By days - (2017-2022)',"By days - before Covid",'By days - after Covid', 'By day of the week - (2017-2022)', 'By month - (2017-2022)'],
                        value='By days - (2017-2022)',  # initial value displayed when page first loads
                        clearable=False)


# Customize your own Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("On the streets of Ottawa: a perspective on drugs, crime, and homelessness by IKEA",style={'color':"white",'text-align': "center"}), width=12)
    ], justify='center',align='center',className="pt-1 bg-dark"),
    dbc.Row([
        dbc.Col(html.Div({}), width=6,id='title')
    ],justify='center',align='center',className="pt-4"),
    dbc.Row([
        dbc.Col([dropdown3], width=6)
    ],className="pt-4 justify-content-center align-self-center"),
    dbc.Row([
        dbc.Col([mygraph], width=12)
    ]),
    # dbc.Row([
    #     dbc.Col(html.Div({},style={'text-align': 'center'}), width=6,id='title')
    # ], justify='center',align='center',className="pt-1 text-decoration-underline"),
    dbc.Row([
        dbc.Col(html.H2("Homelessness",style={'text-align': "center"}), width=12)
    ], justify='center',align='center',className="pt-1"),
    dbc.Row([
        dbc.Col([dropdown2], width=6),
        dbc.Col([dropdown], width=6)
    ],align='center',className="pt-4"),
    dbc.Row([
        dbc.Col([individuals_graph], width=6,
                style ={
                    'align-self': 'center',
                    'justify-content': 'space-around',
                    'align-items': 'center',
                    'display': 'flex'}),
        dbc.Col([shelters_graph], width=3,
                style ={
                    'align-self': 'center',
                    'justify-content': 'space-around',
                    'align-items': 'center',
                    'display': 'flex'},className="pt-1"),
        dbc.Col([inflation_graph], width=3,
                style ={
                    'align-self': 'center',
                    'justify-content': 'space-around',
                    'align-items': 'center',
                    'display': 'flex'},className="pt-1")

    ], className="justify-content-evenly"),
    dbc.Row([
        dbc.Col(html.H2("Overdoses",style={'text-align': "center"}), width=12)
    ], justify='center',align='center',className="pt-1"),
    dbc.Row([
        dbc.Col([overdose_calls_year], width=4,
                style ={
                    'align-self': 'center',
                    'justify-content': 'space-around',
                    'align-items': 'center',
                    'display': 'flex'}),
        dbc.Col([overdose_deaths_year], width=4,
                style ={
                    'align-self': 'center',
                    'justify-content': 'space-around',
                    'align-items': 'center',
                    'display': 'flex'}),
        dbc.Col([overdose_emergency_year], width=4,
                style ={
                    'align-self': 'center',
                    'justify-content': 'space-around',
                    'align-items': 'center',
                    'display': 'flex'})
    ], className="d-flex justify-content-evenly"),
    dbc.Row([
        dbc.Col([dropdown4], width=6),
        dbc.Col([dropdown5], width=6)
    ],align='center',className="pt-4"),
    

], fluid=True)
# Callback allows components to interact
@app.callback(
    Output(mygraph, 'figure'),
    Output(component_id='title', component_property='children'),
    Output(component_id="altair-chart1", component_property="spec"),
    Output(component_id="altair-chart2", component_property="spec"),
    Output(component_id="altair-chart2bis", component_property="spec"),
    Output(component_id="altair-chart3", component_property="spec"),
    Output(component_id="altair-chart4", component_property="spec"),
    Output(component_id="altair-chart5", component_property="spec"),
    Input(dropdown2, 'value'),
    Input(dropdown, 'value'),
    Input(dropdown3,'value'),
)


def update_graph(year,population,type):  # function arguments come from the component property of the Input
    df2=indvd_year
    df3=shelters[shelters['Category']==population]
    df4=overdose_calls
    df5=opioid_related_deaths
    df6=overdose_emergency_month

    if year != 'All':
        df2 = df2[df2['Year'] == year]

        chart1_1 = (
            alt.Chart(df2,
                title='Average number of individuals in shelters per month')
            .encode(
                column=alt.Column('Year', title=None, header=None),
                y=alt.Y('Category', title='').axis(labels=False),
                x=alt.X('mean(Count_)', title='Average headcount per month'),
                color=alt.Color('Category')
            )
            .mark_bar()
            .properties(height=150)
        )

        chart1_2 = (
            alt.Chart(df2).mark_arc().encode(
                column=alt.Column('Year', title=None, header=alt.Header(labelOrient='bottom')),
                color=alt.Color('Category'),
                theta='mean(Count_)'
            ).properties(height=150, width=150)
        )

        chart = chart1_2 | chart1_1

    else:
        chart1_1 = (
            alt.Chart(df2,
                title='Average number of individuals in shelters per month')
            .encode(
                column=alt.Column('Year', title=None, header=None),
                x=alt.X('Category', title='').axis(labels=False),
                y=alt.Y('mean(Count_)', title=None),
                color=alt.Color('Category')
            )
            .mark_bar()
            .properties(width=45)
        )

        chart1_2 = (
            alt.Chart(df2).mark_arc().encode(
                column=alt.Column('Year', title=None, header=alt.Header(labelOrient='bottom')),
                color=alt.Color('Category'),
                theta='mean(Count_)'
            ).properties(height=45, width=47)
        )

        chart = chart1_1 & chart1_2

    chart2 = (
        alt.Chart(df3,
          title="Number of individuals/families in shelters every month")
        .mark_bar()
        .encode(
        x=alt.X('Date', title='Year'),
        y=alt.Y('Count_', title=None),
        color='Category'
        )
    )

    mw_plot = (
        alt.Chart(mw,
            title='Evolution of Ontario minimum wage').mark_line(width=2, color='red').encode(
        x=alt.X('month', title='Year'),
        y=alt.Y('monthly_wage', title='Monthly amount in CAD (for 37.5 hrs/wk)')
        ).interactive()
    )
    apts_tdy_plot = (
        alt.Chart(apts_tdy).mark_line(strokeDash=[4,4], width=.5, opacity=.5).encode(
            x=alt.X('date', title='Year'),
            y=alt.Y('med', title=''),
            color=alt.Color('type', title='Median rent:')
        )
    )
    line = alt.Chart(pd.DataFrame({'y': [733]})).mark_rule(color='green', opacity=.5).encode(y='y')
    text1 = line.mark_text(text='Ontario Works maximum',dx=87, dy=10, color='green')
    text2 = line.mark_text(text='pay nowadays',dx=112, dy=21, color='green')

    chart2bis = mw_plot + apts_tdy_plot + line + text1 + text2

    chart3 = (
        alt.Chart(df4)
        .mark_bar()
        .encode(
        x=alt.X('YEAR:O', title='Year'),
        y=alt.Y('count():Q', title='Number of calls').scale(domain=(0, 1100)),
        color=alt.Color('NARCAN_ADM:N',title='Narcan Administered')
        )
        .properties(width=200)
    )

    chart4 = (
        alt.Chart(df5)
        .mark_bar()
        .encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Confirmed_opioid_related_deaths:Q', title='Confirmed opioid related deaths').scale(domain=(0, 1100)),
        color=alt.Color('Quarter:O',title='Quarter')
        )
        .properties(width=200)
    )

    chart5 = (
        alt.Chart(df6)
        .mark_bar()
        .encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Total ED visits for opioid overdose:Q', title='Number of individuals'),
        )
        .properties(width=200)
    )



    if type != 'All':
        fig_sca_geo = px.scatter_mapbox(df_categ[df_categ['OFF_CATEG']==type].sort_values("YEAR"),
            labels = {"perc_of_crimes":"Percentage of Crime Type"},
            lat="lat",
            lon = "long",
            size = "number_of_crimes" ,
            color = "perc_of_crimes",
            color_continuous_scale="viridis",
            animation_frame="YEAR",
            height=600,
            range_color=(0, 1),
            
            mapbox_style="carto-positron",
            center = {"lat": 45.4215, "lon": -75.6993},
            zoom=9,
            opacity=0.7)
        if len(df_categ[df_categ['OFF_CATEG']==type].YEAR.unique()) > 1:
            fig_sca_geo.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1800
    elif type == "Empty Map":
        fig_sca_geo = px.scatter_mapbox(pd.DataFrame(0),
            height=600,
            range_color=(0, 1),
            mapbox_style="carto-positron",
            center = {"lat": 45.4215, "lon": -75.6993},
            zoom=9,
            opacity=0)
    
    else:
        fig_sca_geo = px.scatter_mapbox(df.sort_values("YEAR"),
                    labels = {"number_of_crimes": "Number of Crimes"},
                    lat="lat",
                    lon = "long",
                        size = "number_of_crimes",
                        color = "number_of_crimes",
                        color_continuous_scale="viridis",
                        animation_frame="YEAR",
                        height=600,
                        range_color=(0, 6500),
                        mapbox_style="carto-positron",
                        center = {"lat": 45.4215, "lon": -75.6993},
                        zoom=9,
                        opacity=0.7)
        if len(df.YEAR.unique()) > 1:
            fig_sca_geo.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1800
    
    ##### Police centers (real positions)
    police_centers_positions = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = police_centers.long, lat = police_centers.lat,
    
    marker=dict(
                size= point_size,
                color = 'black',
                opacity = .8,
            ),
    name="Police Stations",
    text = police_centers.Name,
    textposition = "bottom right",
    visible='legendonly'))

    ##### Hospitals (real positions)
    hospitals_position = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = hospitals.long, lat = hospitals.lat,
    marker=dict(
                size= point_size,
                color = 'red',
                opacity = .8,
            ),
    name="Hospitals",
    text = hospitals.NAME,
    textposition = "bottom right",
    visible='legendonly'))


    #### Police centers (kmeans)
    police_centers_kmeans = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = police_clusters.X, lat = police_clusters.Y,
    marker=dict(
                size= point_size,
                color = 'blue',
                opacity = .8
            ),
    name="Police Stations using kMeans",
    textposition = "bottom right",
    visible='legendonly'))

    new_police_station = pd.DataFrame({"y": [45.426788871368295], "x":[-75.69112349310356]})
    police_new_center = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = new_police_station.x, lat = new_police_station.y,
    marker=dict(
                size= point_size,
                color = 'brown',
                opacity = .8
            ),
    name="New Police Station",
    textposition = "bottom right",
    visible='legendonly'))

    ##### Hospitals (kmeans)
    hospitals_kmeans = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = hospitals_clusters.X, lat = hospitals_clusters.Y,
    marker=dict(
                size= point_size,
                color = 'orange',
                opacity = .8
            ),
    name="Hospitals using kMeans",
    textposition = "bottom right",
    visible='legendonly'))

    ##### Hospitals (dbscan then kmeans)
    hospitals_dbscan_then_kmeans = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = hospitals_dbscan.X, lat = hospitals_dbscan.Y,
    marker=dict(
                size= point_size,
                color = 'purple',
                opacity = .8
            ),
    name="Hospitals using dbscan, then kmeans",
    textposition = "bottom right",
    visible='legendonly'))

    ##### Shelters
    shelters_on_map = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = shelters_loc.long, lat = shelters_loc.lat,
    marker=dict(
                size= point_size,
                color = 'green',
                opacity = .8,
            ),
    name="Shelters",
    visible='legendonly',
    text = shelters_loc.name,
    textposition = "bottom right"))
    ##
    fig_sca_geo.add_trace(police_centers_positions.data[0])
    fig_sca_geo.add_trace(police_centers_kmeans.data[0])
    fig_sca_geo.add_trace(police_new_center.data[0])

    fig_sca_geo.add_trace(hospitals_position.data[0])
    fig_sca_geo.add_trace(hospitals_kmeans.data[0])
    fig_sca_geo.add_trace(hospitals_dbscan_then_kmeans.data[0])
    fig_sca_geo.add_trace(shelters_on_map.data[0])

    fig_sca_geo.update_geos(fitbounds="geojson", visible=False)
    fig_sca_geo.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    

    # try:f
    #     fig_sca_geo.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1800
    # finally:
    #     None
    

    return fig_sca_geo, [html.H2 (type+' crimes in Ottawa',style={'text-align': "center"})], chart.to_dict(),chart2.to_dict(),chart2bis.to_dict(),chart3.to_dict(),chart4.to_dict(),chart5.to_dict()


# Run app
if __name__=='__main__':
    app.run_server(debug=True, port=5500)