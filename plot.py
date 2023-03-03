import plotly.express as px
import pandas as pd
import geojson
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

def load_ds(file_path):
    """
    Load the dogs of Zurich dataset from a CSV file.

    Parameters:
    file_path: The file path to the CSV file.

    Returns:
    pandas.DataFrame: A pandas DataFrame containing the data.
    """
    df = pd.read_csv(file_path)
    return df


def load_geojson(filename_geojson):
    with open(filename_geojson) as f:
        gj = geojson.load(f)
    return gj



def get_dog_by_neighbourhood(df):
    nb_counts = df["QuarLang"].value_counts()
    df_nb = pd.DataFrame({'QuarLang': nb_counts.index, 'Count': nb_counts.values})

    return df_nb

def get_dog_by_district(df):
    district_counts = df["KreisLang"].value_counts()
    df_district = pd.DataFrame({'KreisLang': district_counts.index, 'Count': district_counts.values})

    return df_district

def get_ratio_dog_people(df_dog_by_district, df_population, nb):
    if nb==True:
        df_ratio = df_dog_by_district.merge(df_population, on='QuarLang')
        df_ratio['ratio'] = df_ratio['Count'] / df_ratio['AnzBestWir']
        return df_ratio[['QuarLang', 'ratio', 'Count', 'AnzBestWir']]
    else:
        df_kreis = get_kreis_data(df_population)
        df_ratio = df_dog_by_district.merge(df_kreis, on='KreisLang')
        df_ratio['ratio'] = df_ratio['Count_x'] / df_ratio['Count_y']
        return df_ratio[['KreisLang', 'ratio', 'Count_x', 'Count_y']]

def get_kreis_data(df_population):
    dict_kreis = {
        "Kreis 1": ["Rathaus", "Hochschulen", "Lindenhof", "City"],
        "Kreis 2": ["Wollishofen", "Leimbach", "Enge"],
        "Kreis 3": ["Alt-Wiedikon", "Friesenberg", "Sihlfeld"],
        "Kreis 4": ["Werd", "Langstrasse", "Hard"],
        "Kreis 5": ["Gewerbeschule", "Escher Wyss"],
        "Kreis 6": ["Unterstrass", "Oberstrass"],
        "Kreis 7": ["Fluntern", "Hottingen", "Hirslanden", "Witikon"],
        "Kreis 8": ["Seefeld", "Mühlebach", "Weinegg"],
        "Kreis 9": ["Albisrieden", "Altstetten"],
        "Kreis 10": ["Höngg", "Wipkingen"],
        "Kreis 11": ["Affoltern", "Oerlikon", "Seebach"],
        "Kreis 12": ["Saatlen", "Schwamendingen-Mitte", "Hirzenbach"]
    }

    # Create a new dataframe to store the population data by kreis
    df_kreis = pd.DataFrame(columns=['KreisLang', 'Count'])

    # Iterate over the dict_kreis and sum the population for each neighborhood in the kreis
    for kreis, neighborhoods in dict_kreis.items():
        kreis_population = 0
        for neighborhood in neighborhoods:
            # Find the row in population_df that corresponds to the neighborhood
            neighborhood_df = df_population[df_population['QuarLang'] == neighborhood]
            # Add the population of the neighborhood to the kreis_population
            kreis_population += neighborhood_df['AnzBestWir'].sum()
        # Add a row to dg_kreis with the kreis name and the sum of the population for its inner neighborhoods
        df_kreis = df_kreis.append({'KreisLang': kreis, 'Count': kreis_population}, ignore_index=True)

    return df_kreis

def plot():
    app = dash.Dash(__name__)

    # Define the layout of the app
    app.layout = html.Div([
        html.H1("Dog Population in Zurich", style={'color': light_gray, 'font-family': 'Merriweather','backgroundColor': dark_gray}),

        # Add two buttons to switch between nb/kreis and ratio/absolute
        html.Div([
            dcc.RadioItems(
                id='level-selector',
                options=[{'label': 'Neighbourhood', 'value': 'nb'},
                         {'label': 'District', 'value': 'kreis'}],
                value='nb',
                labelStyle={'display': 'inline-block'}
            ),
        ], style={'background-color': dark_gray, 'margin': '10px', 'color': light_gray, 'font-family': 'Merriweather'}),

        # Add the choropleth map figure
        dcc.Graph(id='choropleth', style={'background-color': dark_gray})
    ], style={'background-color': dark_gray})

    # Define the callback to update the choropleth map figure based on the button selections
    @app.callback(
        Output('choropleth', 'figure'),
        Input('level-selector', 'value')
    )
    def update_choropleth(level):
        filename_population = 'data/population.csv'
        df_population = load_ds(filename_population)
        color_continuous_scale = [[0, "rgb(255, 255, 255)"], [1, young_dog_rgb]]
        if level == 'nb':
            df_dog_by_nb = get_dog_by_neighbourhood(df)
            df_ratio_dog_people = get_ratio_dog_people(df_dog_by_nb, df_population, nb=True)
            fig = px.choropleth(df_ratio_dog_people,
                                 geojson=gj,
                                 locations='QuarLang',
                                 color='ratio',
                                 featureidkey="properties.name",
                                 color_continuous_scale=color_continuous_scale,#"YlOrBr",
                                 labels={'ratio': 'Dog to <br>human ratio'},
                                 range_color=[0, 0.04],
                                 custom_data=['QuarLang', 'AnzBestWir', 'Count', 'ratio']
                                 )
            fig.update_traces(hovertemplate="<br>".join([
                "Neighbourhood: %{customdata[0]}",
                "Population: %{customdata[1]}",
                "Dogs: %{customdata[2]}",
                "Dog ratio: %{customdata[3]:.3f}"
            ]))

        if level == "kreis":
            df_dog_by_district = get_dog_by_district(df)
            df_ratio_dog_people = get_ratio_dog_people(df_dog_by_district, df_population, nb=False)
            fig = px.choropleth(df_ratio_dog_people,
                                 geojson=gj_kreis,
                                 locations='KreisLang',
                                 color='ratio',
                                 featureidkey="properties.bezeichnung",
                                 color_continuous_scale=color_continuous_scale,
                                 labels={'ratio': 'Dog to <br>human ratio'},
                                 range_color=[0, 0.04],
                                 custom_data=['KreisLang', 'Count_y', 'Count_x',  'ratio']
                                 )
            fig.update_traces(hovertemplate="<br>".join([
                "District: %{customdata[0]}",
                "Population: %{customdata[1]}",
                "Dogs: %{customdata[2]}",
                "Dog ratio: %{customdata[3]:.3f}"
            ]))

        fig.update_geos(fitbounds="locations",
                        visible=False  # invisible background
                        )

        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          geo=dict(center=dict(lat=47.3769, lon=8.5417), projection_scale=250000),
                          title_font_family="Merriweather",
                          title_font_size=24,
                          title_font_color=light_gray,
                          title_xanchor="center",
                          title_yanchor="top",
                          title_pad=dict(b=10),
                          paper_bgcolor=dark_gray,
                          plot_bgcolor=dark_gray,
                          font=dict(
                              family="Merriweather",
                              size=14,
                              color=light_gray
                          )
                          )

        fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'))
        fig.update_traces(marker_line_width=0.1)

        return fig

    app.run_server(debug=False)

if __name__ == "__main__":
    male_color = "#617DFA"
    female_color = "#FA6191"
    total_color = "#878787"
    dark_gray = '#212121'
    light_gray = "#F3F3F3"
    young_dog = "#F58700"  # F9A743"
    young_dog_rgb = "rgb(230, 99, 0)"
    old_dog = "#6E6E6E"  # B3B3B3"#633803"
    bar_color = "#400202"
    font_dict_light_gray = {"fontsize": "large", 'weight': 'light', "color": f"{light_gray}"}

    filename_ds = 'data/ds.csv'
    filename_geojson = 'data/zurich-city.geojson'
    filename_geojson_kreis = 'data/zurich-kreis.geojson'

    df = load_ds(filename_ds)
    gj = load_geojson(filename_geojson)
    gj_kreis = load_geojson(filename_geojson_kreis)

    plot()
