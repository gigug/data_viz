import pdb

import plotly.express as px
import dash
import os
import pandas as pd
import plotly.graph_objs as go
import geojson

def plot_popular_breeds(df):
    """
    Create a Plotly bar chart showing the most popular dog breeds in Zurich.

    Parameters:
    df (pandas.DataFrame): The Dogs of Zurich dataset as a pandas DataFrame.

    Returns:
    None
    """
    # Count the number of dogs for each breed and sort in descending order
    breed_counts = df['RASSE1'].value_counts().sort_values(ascending=False)

    # Create a Plotly bar chart with the breed names as x-axis and the counts as y-axis
    data = [go.Bar(x=breed_counts.index, y=breed_counts.values)]

    # Set the layout of the chart
    layout = go.Layout(
        title='Most Popular Dog Breeds in Zurich',
        xaxis=dict(title='Breed'),
        yaxis=dict(title='Number of Dogs'),
    )

    # Create a Figure object that combines the data and layout
    fig = go.Figure(data=data, layout=layout)

    # Show the plot in a web browser
    fig.show()


def plot_age_vs_breed(df):
    # Filter for top 20 dog breeds
    top_breeds = df['RASSE1'].value_counts().nlargest(20).index
    filtered_df = df[df['RASSE1'].isin(top_breeds)]

    # Group by age and breed and count occurrences
    grouped_df = filtered_df.groupby(['ALTER', 'RASSE1']).size().reset_index(name='count')

    # Create plot
    fig = px.scatter(grouped_df, x='ALTER', y='RASSE1', size='count', color='RASSE1', hover_name='RASSE1',
                     title='Age of Dog Owners vs Breed of Dog Owned')

    fig.update_layout(xaxis_title='Age of Dog Owner', yaxis_title='Breed of Dog',
                      legend_title='Breed of Dog', font=dict(family='Arial', size=12))

    fig.show()


def plot_dog_breed_district(gj, df):
    df_dog_by_district = get_dog_by_district(df)

    filename_population = 'data/population.csv'
    df_population = load_ds(filename_population)

    fig = px.choropleth(df_dog_by_district,
                        geojson=gj,
                        locations='QuarLang',
                        color='Count',
                        featureidkey="properties.name",
                        color_continuous_scale="Oranges",
                        labels={'Count': 'unemployment rate'}
                        )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()


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


def correct_geojson(gj):

    # Define a dictionary of misspelled district names and their correct spelling
    misspelled_to_correct = {
        'MÃ¼hlebach': 'Mühlebach',
        'HÃ¶ngg': 'Höngg',
        # Add more misspelled and correct district names as necessary
    }

    # Loop through the features in the GeoJSON file
    for feature in gj['features']:
        # Get the district name from the feature's properties
        district_name = feature['properties']['name']
        # Check if the district name is in the misspelled_to_correct dictionary
        if district_name in misspelled_to_correct:
            # If it is, replace the district name with its correct spelling
            feature['properties']['name'] = misspelled_to_correct[district_name]

    # Save the modified GeoJSON file
    with open('data/zurich-city.geojson', 'w') as f:
        geojson.dump(gj, f)


def fix_ds(df):
    # Define the list of districts to remove
    districts_to_remove = ['Unbekannt (Kreis 4)', 'Unbekannt (Kreis 6)', 'Unbekannt (Kreis 8)', 'Unbekannt (Kreis 1)',
                           'Unbekannt (Stadt Zürich)']

    # Drop the rows with the corresponding districts
    df = df[~df['QuarLang'].isin(districts_to_remove)]

    # Save the resulting DataFrame to a new CSV file
    df.to_csv(filename_ds, index=False)


def get_dog_by_district(df):
    district_counts = df["QuarLang"].value_counts()
    df_district = pd.DataFrame({'QuarLang': district_counts.index, 'Count': district_counts.values})

    return df_district


if __name__ == "__main__":
    filename_ds = 'data/ds.csv'
    filename_geojson = 'data/zurich-city.geojson'

    df = load_ds(filename_ds)
    gj = load_geojson(filename_geojson)

    # First question: what are the most popular dog breeds in Zurich?
    #plot_popular_breeds(df)

    # Second question: how does the age of dog owners relate to the breed of dog they own?
    #plot_age_vs_breed(df)

    # Third question: how does the breed of dogs vary by district in Zurich?
    plot_dog_breed_district(gj, df)