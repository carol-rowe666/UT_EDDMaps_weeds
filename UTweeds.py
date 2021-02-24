
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


# read in files
edd = pd.read_csv('EDDMapS_UDAFweeds2020.zip')
#print(edd.shape)
#print(edd.columns)

edd_mini = edd[['Longitude', 'Latitude','Genus_sp', 'L3_EcoReg', 'ObsYr', 'objectid' , 'Class']]
regions = ['Central Basin and Range', 'Colorado Plateaus', 'Mojave Basin and Range', 'Northern Basin and Range', 'Southern Rockies', 'Wasatch and Uinta Mountains', 'Wyoming Basin']
colors = ['blueviolet','indianred', 'lime', 'lightcoral','cyan', 'cornflowerblue','red']
reg_col_dict = dict(zip(regions, colors))
species = sorted(edd['Genus_sp'].unique())

yr_options=[{'label': x, 'value': x} for x in sorted(edd['ObsYr'].unique())]
yr_options.insert(0, {'label': 'ALL years', 'value': 0})
print(yr_options)

years = [sorted(edd['ObsYr'].unique())]
my_value = int(edd_mini['ObsYr'].max() + 1)
print(my_value)
slider_options ={str(year): str(year) for year in sorted(edd_mini['ObsYr'].unique())}
#slider_options = {str(k):str(v) for k,v in slider_options.items()}
slider_options.update({my_value: 'ALL Years'})
print(slider_options)
# this is for hiding slide bar depending on selection
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
#app = dash.Dash(__name__)

# ------------------LAYOUT--SECTION----------------------------------------------------------
# App layout
app.layout = dbc.Container([

    dbc.Row(dbc.Col(html.H1('UDAF weeds in EDDMapS for years 1995-2019', className='text-center text-primary mb-4'),
                    width=12)),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='slctd_weed1', multi=False, value="Convolvulus spp.",
                         options=[{'label': x, 'value': x} for x in sorted(edd['Genus_sp'].unique())]),
            dcc.Graph(id='my_weed_bar', figure={})],
            xs=12, sm=12, md=12, lg=7, xl=7),
        dbc.Col([
            dcc.Dropdown(id='slctd_weed2', multi=False, value="Convolvulus spp.",
                         options=[{'label': x, 'value': x} for x in sorted(edd['Genus_sp'].unique())],
                         style={'width': '100%', 'display': 'inline-block'}, searchable=True),
            dcc.Dropdown(id='slctd_yr', multi=False, value=0,
                         options=yr_options,
                         style={'width': '50%', 'display': 'inline-block'}),
            dcc.Graph(id='my_weed_map', figure={})],
            xs=12, sm=12, md=12, lg=5, xl=5)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='all_weed_bar', figure={}),
            dcc.Slider(id='year-slider', min=edd_mini['ObsYr'].min(), max=2020,
                       value=2019,included=False,
                       marks=slider_options)],
                        # marks={str(year): str(year) for year in edd_mini['ObsYr'].unique()}, step=1)],
            xs=12, sm=12, md=12, lg=12, xl=12)
    ])
])


# ------------------CALLBACK--SECTION----------------------------------------------------------

# ------------BAR GRAPH------------BAR GRAPH------------BAR GRAPH------------BAR GRAPH------------BAR GRAPH------
@app.callback(
    Output(component_id='my_weed_bar', component_property='figure'),
    Input(component_id='slctd_weed1', component_property='value')
)
def update_graph(weed_slctd):
    dff = edd[edd['Genus_sp'] == weed_slctd]
    dff = dff.groupby(['ObsYr', 'L3_EcoReg', 'Class'])['objectid'].count().reset_index(name='count')
#    dff = dff.sort_values(['L3_EcoReg'])
    fig_bar = px.bar(dff, x='ObsYr', y='count', color='L3_EcoReg', color_discrete_map=reg_col_dict,
                     range_x = [1994.2,2019.8], hover_data=['count', 'Class'],
                     labels={"L3_EcoReg": "UT EcoRegion",
                             "count": "Number of Records", "ObsYr": 'Year', 'Class': 'UDAF class'}
                     )
    fig_bar.update_layout(xaxis=dict(title='', dtick=1.0, showticklabels=True))

    return fig_bar


# -------------MAP-----------------MAP-----------------MAP-----------------MAP-----------------MAP----------

@app.callback(
    output = Output(component_id='my_weed_map', component_property='figure'),
    inputs=[Input(component_id='slctd_weed2', component_property='value'),
            Input(component_id='slctd_yr', component_property='value')])

def update_graph(weed_slctd, slctd_yr):
    dff2 = edd_mini[edd_mini['Genus_sp'] == weed_slctd]
    dff2 = dff2.sort_values(['L3_EcoReg'])
    if slctd_yr != 0:
        dff = dff2[dff2['ObsYr'] == slctd_yr]
    else:
        dff = dff2.copy()

    if dff.shape[0] == 0:
#        dff3 = pd.DataFrame({'Latitude': [39.5], 'Longitude':[-111.6], 'TEXT':["NO DATA"]})
        fig_map = px.scatter_mapbox(data_frame=dff,lat=dff['Latitude'], lon=dff['Longitude'],
                                    center={"lat": 39.5, "lon": -111.6}, zoom=5.3,
                                    labels={"L3_EcoReg": "UT EcoRegion", 'Class': 'UDAF Class'},
                                    hover_data=['Class'])

        fig_map.update_layout(mapbox_style = 'carto-positron', showlegend=False)
        fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig_map.add_annotation(x=2, y=2, text="No data for this selection",showarrow=False, font=dict(size=20))

    else:
        fig_map = px.scatter_mapbox(data_frame=dff, lat=dff['Latitude'], lon=dff['Longitude'], color=dff['L3_EcoReg'],
                                    center={"lat": 39.5, "lon": -111.6}, zoom=5.3, color_discrete_map=reg_col_dict,
                                    labels={"L3_EcoReg": "UT EcoRegion", 'Class': 'UDAF Class'},
                                    hover_data=['Class'])
        fig_map.update_layout(mapbox_style="carto-positron", showlegend=False)
        fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig_map

# -----------------ALL WEEDS BAR-----------------ALL WEEDS BAR-----------------ALL WEEDS BAR----------

@app.callback(
    output = Output(component_id='all_weed_bar', component_property='figure'),
    inputs= [Input(component_id='year-slider', component_property='value')]
)

def update_graph(selected_year):
    if selected_year == my_value:
        dff = edd_mini.groupby(['Genus_sp', 'L3_EcoReg', 'Class'])['objectid'].count().reset_index(name='count')
        all_fig_bar = px.bar(dff, x='Genus_sp', y='count',
                             color='L3_EcoReg',
                             color_discrete_map=reg_col_dict,
                             category_orders={'Genus_species': species, 'L3_EcoReg': regions},
                             labels={"L3_EcoReg": "UT EcoRegion","count": "Number of Records", "ObsYr": 'Year', 'Class': 'UDAF class'},
                             hover_data=['Class']
                             )
        all_fig_bar.update_xaxes(categoryorder='category ascending')
        all_fig_bar.update_layout(xaxis=dict(title='', dtick=1.0, showticklabels=True), showlegend=False,
                                  title_text='All years selected.',title_font=dict(size=18)
                                  )
    else:
        selected_year = int(selected_year)
        dff = edd_mini[edd_mini['ObsYr'] == selected_year]
        dff2 = dff.groupby(['Genus_sp', 'L3_EcoReg','Class'])['objectid'].count().reset_index(name='count')
        in_list = dff2['Genus_sp'].unique().tolist()
        not_list = list(set(species) - set(in_list))
        new_df = pd.DataFrame(data=not_list)
        new_df['L3_EcoREg'] = 'x'
        new_df['count'] = 0
        new_df.columns = ['Genus_sp', 'L3_EcoReg', 'count']
        bigdata = new_df.append(dff2, ignore_index=True)

        all_fig_bar = px.bar(bigdata, x='Genus_sp', y='count',
                             color='L3_EcoReg',
                             color_discrete_map=reg_col_dict,
                             category_orders={'Genus_species':species, 'L3_EcoReg':regions},
                             range_y=[0,1500],
                             labels={"L3_EcoReg": "UT EcoRegion", "count": "Number of Records", "ObsYr": 'Year', 'Class': 'UDAF class'},
                             hover_data=['Class']
                             )
        # range_y=[0,7000]
        all_fig_bar.update_xaxes(categoryorder='category ascending')
        all_fig_bar.update_layout(xaxis=dict(title='', dtick=1.0, showticklabels=True), showlegend=False,
                                  title_text='Select year below. Records cut-off is 1,500. See above graph for larger values.',
                                  title_font=dict(size=18))
#        all_fig_bar.update_layout(transition_duration=500)

    return all_fig_bar


if __name__ == '__main__':
    app.run_server(debug=False)
