import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os
import pandas as pd
import numpy as np
from xbtutils.utilities import get_current_fy_range, FYClass

# Plotly library https://plotly.com/python/bar-charts/
# Plotly color scales https://plotly.com/python/discrete-color/

# Create bar plot by soopline
# Input: list of dictionaries with keys: date, soopLine, callSign, profiles
def make_plot_by_soopline(statsDictList, outputDir="test_output", fname = "plot_by_soopline_bar.html", w=900, h=600):
    # convert dictionary list to pandas dataframe    
    df = pd.DataFrame(statsDictList)
    try:
        # group by year-month and soopline, summing profiles
        df['yearMonth'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
        df = df.groupby(['yearMonth', 'soopLine', 'callSign'], as_index=False)['profiles'].sum()
        # simple and works well (alternative):
        fig = px.bar(df, x='yearMonth', y='profiles', color='soopLine', color_discrete_sequence=px.colors.qualitative.Light24,
                    title='XBT Profiles by SOOP Line', labels={'yearMonth':'Year-Month', 'profiles':'Number of Profiles', 'soopLine':'SOOP Line', 'callSign':'Call Sign'},
                    barmode='group', height=h, width=w, hover_data=['callSign'])
        
        fig.update_layout( legend=dict(
            orientation="h", # Horizontal orientation
            yanchor="top",
            y=1.1, 
            xanchor="left",
            x=0.1 ), title_x=0.5 )

        # Save the plot as an HTML file
        os.makedirs(outputDir, exist_ok=True)
        file_path = os.path.join(outputDir, fname)
        fig.write_html(file_path)

    except Exception as e:
        print(f"> Error creating stats plot bar by soopline: {e}")


# Create pie plot by soopline for current and previous fiscal year
# Input: list of dictionaries with keys: date, soopLine, callSign, profiles
def make_plot_by_soopline_pie(statsDictList, outputDir="test_output", fname = "plot_by_soopline_pie.html", w=900, h=600):
    # convert dictionary list to pandas dataframe    
    df = pd.DataFrame(statsDictList)
    try:
        # get current and previous fiscal year ranges
        fycurrent = get_current_fy_range(0)
        fyprev = get_current_fy_range(-1)
        # filter dataframe for current and previous fiscal years
        dfcurrent = df[(df['date'] >= fycurrent.startDate) & (df['date'] <= fycurrent.endDate)]
        dfprev = df[(df['date'] >= fyprev.startDate) & (df['date'] <= fyprev.endDate)]

        # create a pie plot with two subplots
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])

        # aggregate profiles by soopline for previous fiscal year
        df_agg_prev = dfprev.groupby('soopLine', as_index=False)['profiles'].sum()
        trace_prev = go.Pie(labels=df_agg_prev['soopLine'], values=df_agg_prev['profiles'],
                                 name=f'FY{fyprev.fiscalYear}', hole=0.4)
        # aggregate profiles by soopline for current fiscal year
        df_agg_current = dfcurrent.groupby('soopLine', as_index=False)['profiles'].sum()
        trace_current = go.Pie(labels=df_agg_current['soopLine'], values=df_agg_current['profiles'],
                                 name=f'FY{fycurrent.fiscalYear}', hole=0.4)
        # add traces to figure
        fig.add_trace(trace_prev, row=1, col=1)
        fig.add_trace(trace_current, row=1, col=2)  
        # update traces and layout
        fig.update_traces(textinfo='percent')
        fig.update_layout(title_text=f'XBT Profiles by SOOP Line FY{fyprev.fiscalYear} vs FY{fycurrent.fiscalYear}', height=h, width=w, title_x=0.5)
        # move labels closer to the pie
        fig.update_layout( legend=dict(
                orientation="h", # Horizontal orientation
                yanchor="top",
                y=1.1, 
                xanchor="left",
                x=0.1 ) )

        # Save the plot as an HTML file
        os.makedirs(outputDir, exist_ok=True)
        file_path = os.path.join(outputDir, fname)
        fig.write_html(file_path)

    except Exception as e:
        print(f"> Error creating stats pie plot by soopline: {e}")


# Extract SST from profile data string
# The data string is assumed to be a comma-separated list of values and SST is the first value
def extract_sst(data):    
    try:
        sst = data.split(",")[0]  # assuming SST is the first value
        return float(sst)
    except:
        return np.nan

# Create density map plot by map temperature
# Input: list of dictionaries with keys: latitude, longitude, data
def make_plot_by_map_temperature(statsDictList, outputDir="test_output", fname = "plot_by_map_temperature.html", w=1200, h=600):
    # convert dictionary list to pandas dataframe    
    df = pd.DataFrame(statsDictList)
    # extract SST data from the profile dictionary
    df['sst'] = df['data'].apply(extract_sst)
    try:
        fig = px.density_map(df, lat='latitude', lon='longitude', z='sst', radius=10,
                        center=dict(lat=0, lon=180), zoom=0,
                        map_style="open-street-map", width=w, height=h,
                        labels={'sst':'Sea Surface Temperature (°C)'},
                        hover_data={'sst':':.2f', 'latitude':':.2f', 'longitude':':.2f'})

        # Save the plot as an HTML file
        os.makedirs(outputDir, exist_ok=True)
        file_path = os.path.join(outputDir, fname)
        fig.write_html(file_path)

    except Exception as e:
        print(f"> Error creating stats plot by map temperature: {e}")


# Create bar plot by agency
# Input: list of dictionaries with keys: date, agencyName, soopLine, profiles
def make_plot_by_agency_bar(dictlist_agency, outputDir="test_output", fname = "plot_by_agency.html", w=900, h=600):
    # convert dictionary list to pandas dataframe    
    df = pd.DataFrame(dictlist_agency)
    try:
        fig = px.bar(df, x='date', y='profiles', color='agencyName',
                    title='XBT Profiles by Agency', labels={'date':'Date', 'profiles':'Number of Profiles', 'agency':'Agency'},
                    barmode='stack', height=h, width=w, hover_data=['soopLine'])
        # relocate the legend to the top
        fig.update_layout( legend=dict(
                orientation="h", # Horizontal orientation
                yanchor="top",
                y=1.1, 
                xanchor="left",
                x=0.1 ), title_x=0.5 )
        
        # Save the plot as an HTML file
        os.makedirs(outputDir, exist_ok=True)
        file_path = os.path.join(outputDir, fname)
        fig.write_html(file_path)

    except Exception as e:
        print(f"> Error creating stats plot by agency: {e}")


# Create pie plot by agency for current and previous fiscal year
# Input: list of dictionaries with keys: date, agencyName, soopLine, profiles
def make_plot_by_agency_pie(dictlist_agency, outputDir="test_output", fname = "plot_by_agency_pie.html", w=900, h=600):
    # convert dictionary list to pandas dataframe    
    df = pd.DataFrame(dictlist_agency)
    try:
        # get current and previous fiscal year ranges
        fycurrent = get_current_fy_range(0)
        fyprev = get_current_fy_range(-1)
        # filter dataframe for current and previous fiscal years
        dfcurrent = df[(df['date'] >= fycurrent.startDate) & (df['date'] <= fycurrent.endDate)]
        dfprev = df[(df['date'] >= fyprev.startDate) & (df['date'] <= fyprev.endDate)]

        # create a pie plot with two subplots
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])

        # aggregate profiles by agency for previous fiscal year
        df_agg_prev = dfprev.groupby('agencyName', as_index=False)['profiles'].sum()
        trace_prev = go.Pie(labels=df_agg_prev['agencyName'], values=df_agg_prev['profiles'],
                                 name=f'FY{fyprev.fiscalYear}', hole=0.4)
        # aggregate profiles by agency for current fiscal year
        df_agg_current = dfcurrent.groupby('agencyName', as_index=False)['profiles'].sum()
        trace_current = go.Pie(labels=df_agg_current['agencyName'], values=df_agg_current['profiles'],
                                 name=f'FY{fycurrent.fiscalYear}', hole=0.4)
        
        fig.add_trace(trace_prev, row=1, col=1)
        fig.add_trace(trace_current, row=1, col=2)  
        
        fig.update_traces(textinfo='percent')
        fig.update_layout(title_text=f'XBT Profiles by Agency FY{fyprev.fiscalYear} vs FY{fycurrent.fiscalYear}', height=h, width=w, title_x=0.5)
        # move labels closer to the pie
        fig.update_layout( legend=dict(
                orientation="h", # Horizontal orientation
                yanchor="top",
                y=1.1, 
                xanchor="left",
                x=0.1 ) )

        # Save the plot as an HTML file
        os.makedirs(outputDir, exist_ok=True)
        file_path = os.path.join(outputDir, fname)
        fig.write_html(file_path)

    except Exception as e:
        print(f"> Error creating stats pie plot by agency: {e}")