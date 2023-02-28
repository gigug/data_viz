import pdb
import joypy
import matplotlib
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from plotly.graph_objs import *
import plotly.graph_objs as go
import geojson
from matplotlib import pyplot as plt, ticker
from seaborn import cm
import cmocean as cmo
import matplotlib as mpl
import seaborn as sns
import calendar


def plot_popular_breeds(df):
    """
    Create a Plotly bar chart showing the most popular dog breeds in Zurich.

    Parameters:
    df (pandas.DataFrame): The Dogs of Zurich dataset as a pandas DataFrame.

    Returns:
    None
    """
    # Remove all rows where breed is "unbekannt"
    df = df[df['Rasse1Text'] != 'Unbekannt']

    # Count the number of dogs for each breed and sort in descending order
    all_breed_count = df['Rasse1Text'].value_counts().sort_values(ascending=False)

    num_breeds = 20

    # Select only the 10 most common breeds
    top_breed_count = all_breed_count[:num_breeds]
    other_breed_count = all_breed_count.iloc[num_breeds:].sum()

    # Sort the breed_counts DataFrame in descending order
    top_breed_count = top_breed_count.sort_values(ascending=True)

    # Create a Plotly bar chart with the breed names as y-axis and the counts as x-axis
    #data = [go.Bar(y=['Other Breeds'], x=[other_breed_count], orientation='h'),
    #        go.Bar(y=top_breed_count.index, x=top_breed_count.values, orientation='h')]
    data = [go.Bar(y=top_breed_count.index, x=top_breed_count.values, orientation='h')]

    # Set the layout of the chart
    layout = go.Layout(
        title='10 Most Popular Dog Breeds in Zurich',
        yaxis=dict(title='Breed'),
        xaxis=dict(title='Number of Dogs'),
    )

    # Create a Figure object that combines the data and layout
    fig = go.Figure(data=data, layout=layout)

    # Show the plot in a web browser
    fig.show()


def plot_popular_breeds2(df):
    # Remove all rows where breed is "unbekannt"
    df = df[df['Rasse1Text'] != 'Unbekannt']

    # Count the number of dogs for each breed and sort in descending order
    all_breed_count = df['Rasse1Text'].value_counts().sort_values(ascending=False)

    num_breeds = 15

    # Select only the 10 most common breeds
    top_breed_count = all_breed_count[:num_breeds]

    # Sort the breed_counts DataFrame in descending order
    top_breed_count = top_breed_count.sort_values(ascending=False)

    # convert to list of dictionaries
    categories = [{"name": breed, "value": count} for breed, count in top_breed_count.items()]

    subplots = make_subplots(
        rows=len(categories),
        cols=1,
        subplot_titles=[x["name"] for x in categories],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.45 / len(categories)),
    )
    subplots['layout'].update(
        width=550,
        plot_bgcolor='#fff',
    )

    # add bars for the categories
    for k, x in enumerate(categories):
        subplots.add_trace(dict(
            type='bar',
            orientation='h',
            y=[x["name"]],
            x=[x["value"]],
            text=["{:,.0f}".format(x["value"])],
            hoverinfo='text',
            textposition='auto',
            marker=dict(
                color="#E87461",
            ),
        ), k + 1, 1)

    # update the layout
    subplots['layout'].update(
        showlegend=False,
    )
    for x in subplots["layout"]['annotations']:
        x['x'] = 0
        x['xanchor'] = 'left'
        x['align'] = 'left'
        x['font'] = dict(
            size=12,
        )

    # hide the axes
    for axis in subplots['layout']:
        if axis.startswith('yaxis') or axis.startswith('xaxis'):
            subplots['layout'][axis]['visible'] = False

    # update the margins and size
    subplots['layout']['margin'] = {
        'l': 0,
        'r': 0,
        't': 20,
        'b': 1,
    }
    height_calc = 45 * len(categories)
    height_calc = max([height_calc, 350])
    subplots['layout']['height'] = height_calc
    subplots['layout']['width'] = height_calc

    subplots['layout'].update(
        title={
            'text': 'Chihuahua is the most common single breed in Zurich',
            'xanchor': 'left',
            'yanchor': 'top',
            'font': {
                'size': 20,
            },
        },
    )

    subplots.show()

def plot_age_vs_breed(df):
    # Filter for top 20 dog breeds
    top_breeds = df['Rasse1Text'].value_counts().nlargest(20).index
    filtered_df = df[df['Rasse1Text'].isin(top_breeds)]

    # Group by age and breed and count occurrences
    grouped_df = filtered_df.groupby(['ALTER', 'Rasse1Text']).size().reset_index(name='count')

    # Create plot
    fig = px.scatter(grouped_df, x='ALTER', y='Rasse1Text', size='count', color='Rasse1Text', hover_name='Rasse1Text',
                     title='Age of Dog Owners vs Breed of Dog Owned')

    fig.update_layout(xaxis_title='Age of Dog Owner', yaxis_title='Breed of Dog',
                      legend_title='Breed of Dog', font=dict(family='Arial', size=12))

    fig.show()


def get_ratio_dog_people(df_dog_by_district, df_population):
    df_ratio = df_dog_by_district.merge(df_population, on='QuarLang')
    df_ratio['ratio'] = df_ratio['Count'] / df_ratio['AnzBestWir']
    return df_ratio[['QuarLang', 'ratio']]


def plot_dog_breed_district(gj, df):
    df_dog_by_district = get_dog_by_district(df)

    filename_population = 'data/population.csv'
    df_population = load_ds(filename_population)

    df_ratio_dog_people = get_ratio_dog_people(df_dog_by_district, df_population)

    fig = px.choropleth(df_ratio_dog_people,
                        geojson=gj,
                        locations='QuarLang',
                        color='ratio',
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


def plot_age_correlation(df):
    # create a new dataframe with the count of each combination of owner and dog age
    df_counts = df.groupby(['AlterV10Cd', 'AlterVHundCd']).size().reset_index(name='counts')

    # create a scatter plot with size based on the count
    fig = px.scatter(df_counts, x='AlterV10Cd', y='AlterVHundCd', size='counts', trendline='ols')

    # add a title
    fig.update_layout(title='Relationship between dog age and owner age')

    # show the plot
    fig.show()

def plot_age_correlation2(df):
    # Create a violin plot for each owner age
    fig = px.violin(df, y='AlterVHundCd', x='AlterV10Cd', box=True, hover_data=df.columns, range_y=[0, 20])
    fig.update_traces(meanline_visible=True)

    # Add a title
    fig.update_layout(title='Distribution of dog age for each owner age')

    # Show the plot
    fig.show()

# joyplot with joypy, can't add colors
def plot_age_correlation4(df):

    df = df.sort_values("AlterV10Cd", ascending=False)
    df = df.groupby("AlterV10Cd", sort=False)

    dogs_ages = range(0, 25)

    # Define colormap
    original_cmap = plt.cm.viridis

    # Plot the joyplot
    fig, axes = joypy.joyplot(df,
                              column='AlterVHundCd',
                              by='AlterV10Cd',
                              range_style='own',
                              grid='both',
                              linewidth=1,
                              figsize=(10, 6),
                              x_range=[0, 25],
                              legend=False,
                              #colormap=original_cmap,
                              fade=True)

    # Set labels and title
    plt.xlabel('Dog Age')
    plt.ylabel('Owner Age')
    plt.title('Distribution of dog age for each owner age')

    plt.show()

# working
def plot_age_correlation5(df):
    COLOR = 'white'
    mpl.rcParams['text.color'] = COLOR
    mpl.rcParams['axes.labelcolor'] = COLOR
    mpl.rcParams['xtick.color'] = COLOR
    mpl.rcParams['ytick.color'] = COLOR
    plt.rcParams["font.family"] = "Merriweather"
    ages = range(90, 0, -10)

    fig, axs = plt.subplots(nrows=9, figsize=(6, 7), sharex=True, sharey=True, gridspec_kw={'left': 0.4})
    fig.set_facecolor("none")

    x = np.linspace(0, 1, 100)
    for i, ax in enumerate(axs, 1):
        sns.kdeplot(df.query(f"AlterV10Cd=={ages[i-1]}")["AlterVHundCd"],
                    fill=True,
                    color="#212121",  # contour color
                    alpha=0,
                    linewidth=2,
                    legend=False,
                    ax=ax)

        ax.set_xlim(0, 20)

        # >>> 밀도함수에 gradient 추가
        im = ax.imshow(np.vstack([x, x]),
                       cmap="copper_r",
                       aspect="auto",
                       extent=[*ax.get_xlim(), *ax.get_ylim()]
                       )
        path = ax.collections[0].get_paths()[0]
        patch = mpl.patches.PathPatch(path, transform=ax.transData)
        im.set_clip_path(patch)
        # <<< 밀도함수에 gradient 추가
        ax.text(-2.2, 0.015, f"{ages[i-1]}s", fontdict=font_dict_light_gray)

        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        if i != 9:
            ax.tick_params(axis="x", length=0)
        else:
            ax.tick_params(axis="x",
                           direction="inout",
                           color=light_gray,
                           length=5,
                           width=2,
                           labelsize="large")
            ax.set_xticklabels(ax.get_xticklabels(), fontweight='light', color=light_gray)

            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x)}" if int(x) in [0, 5, 10, 15, 20] else ""))
            ax.xaxis.set_ticks([0, 5, 10, 15, 20])

        ax.set_yticks([])
        ax.set_ylabel("Age of owner",  fontdict={"fontsize": "large"},  rotation=0)
        ax.set_xlabel("Age of dog", fontdict={"fontsize": "large"})
        ax.yaxis.set_label_coords(-0.4, -0.97)

        ax.axhline(0, color=light_gray)
        ax.set_facecolor("none")

    fig.subplots_adjust(hspace=-0.75, top=0.99)#-0.57)
    plt.savefig('filename.png', dpi=300)
    plt.show()

if __name__ == "__main__":

    light_gray = "#F3F3F3"
    font_dict_light_gray = {"fontsize": "large", 'weight': 'light', "color": f"{light_gray}"}

    filename_ds = 'data/ds.csv'
    filename_geojson = 'data/zurich-city.geojson'

    df = load_ds(filename_ds)
    gj = load_geojson(filename_geojson)

    # First question: what are the most popular dog breeds in Zurich?
    #plot_popular_breeds2(df)

    # Second question: how does the age of dog owners relate to the breed of dog they own?
    #plot_age_vs_breed(df)

    # Third question: how does the breed of dogs vary by district in Zurich?
    #plot_dog_breed_district(gj, df)
    
    # Fourth question: is age of dog correlated to age of owner?
    plot_age_correlation5(df)