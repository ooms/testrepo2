# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

site_options = [
    {'label': 'All Sites', 'value': 'ALL'}
] + [
    {'label': site, 'value': site}
    for site in spacex_df['Launch Site'].unique()
]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',  
                                                options=site_options,
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                dcc.Graph(id='success-pie-chart'),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',2500: '2500', 5000: '5000',7500: '7500', 10000: '10000'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df
        title = 'Success Launches for All Sites'
        fig = px.pie(filtered_df,values='class',
            names='Launch Site', 
            title=title)

    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        title = f'Success Launches for Site {entered_site}'


        fig = px.pie(filtered_df,
            names='class', 
            title=title)
        
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value')])
def get_scatter_plot(entered_site, payload_range):
    min_payload = payload_range[0]
    max_payload = payload_range[1]

    print("selections: ", entered_site, payload_range)
    title= 'Payload Mass vs Launch Outcome'
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= min_payload) &
        (spacex_df['Payload Mass (kg)'] <= max_payload)
    ]

    if entered_site != 'ALL':
        # return the outcomes piechart for a selected site
        filtered_df = filtered_df[filtered_df['Launch Site']==entered_site]


    fig = px.scatter(filtered_df,
        x='Payload Mass (kg)',
        y='class', 
        color='Booster Version Category',
        title = title)
        
    return fig

# Successful launches by site
successful_by_site = (
    spacex_df[spacex_df['class'] == 1]
    .groupby('Launch Site')
    .size()
    .sort_values(ascending=False)
)

# Launch success rate by site
site_success_rate = (
    spacex_df.groupby('Launch Site')['class']
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("Successful by site: ",successful_by_site)
print("Site success rate: " ,site_success_rate)

booster_success_rate = (
    spacex_df.groupby('Booster Version Category')['class']
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

launch_count = (
    spacex_df['Booster Version Category']
    .value_counts()
)

print("launch count:",launch_count)
print("booster success rate: ",booster_success_rate)

spacex_df['Payload Range'] = pd.cut(
    spacex_df['Payload Mass (kg)'],
    bins=[0, 2500, 5000, 7500, 10000, float('inf')],
    include_lowest=True
)

payload_success_rate = (
    spacex_df.groupby('Payload Range', observed=False)['class']
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("Payload success rate: ",payload_success_rate)



# Run the app
if __name__ == '__main__':
    app.run()