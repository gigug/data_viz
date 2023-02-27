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


def plot_dog_breed_district(df):
    # Select the top 15 most common dog breeds
    top_breeds = df['RASSE1'].value_counts().nlargest(15).index.tolist()

    # Filter the data to include only the top 15 breeds
    filtered_df = df[df['RASSE1'].isin(top_breeds)]

    # Group the data by district and breed
    grouped_df = filtered_df.groupby(['STADTKREIS', 'RASSE1']).size().reset_index(name='count')

    # Create a plotly scatter plot
    fig = px.scatter(grouped_df, x='STADTKREIS', y='RASSE1', size='count',
                     hover_data={'STADTKREIS': True, 'RASSE1': True, 'count': True},
                     labels={'STADTKREIS': 'District', 'RASSE1': 'Breed', 'count': 'Count'},
                     title='Most Common Dog Breeds by District in Zurich',
                     color='count',
                     color_continuous_scale='Blues')

    fig.update_layout(xaxis={'tickmode': 'linear'})
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


def plot_geojson(gj):
    fig = px.choropleth_mapbox(gj,
                               geojson=gj,
                               locations=[1],
                               color_discrete_sequence=['blue'],
                               opacity=0.5,
                               center={"lat": 47.36667, "lon": 8.55},
                               mapbox_style="carto-positron",
                               zoom=9)

    fig.show()


if __name__ == "__main__":
    filename_ds = 'data/2017hund.csv'
    filename_geojson = 'data/zurich.geojson'
    filename_geojson_city = 'data/zurich-city.geojson'

    df = load_ds(filename_ds)
    gj = load_geojson(filename_geojson)
    gj_city = load_geojson(filename_geojson_city)

    plot_geojson(gj)
    plot_geojson(gj_city)

    # First question: what are the most popular dog breeds in Zurich?
    #plot_popular_breeds(df)

    # Second question: how does the age of dog owners relate to the breed of dog they own?
    #plot_age_vs_breed(df)

    # Third question: how does the breed of dogs vary by district in Zurich?
    #plot_dog_breed_district(df)