# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 23:11:11 2024

@author: Yunus
"""

import pandas as pd
import requests
from plotly import offline
import plotly.express as px
from io import StringIO
import os

# URL for the data source
url = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"

# Fetch the HTML content
try:
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    html_content = response.text
except requests.RequestException as e:
    print(f"Error fetching data: {e}")
    exit()

# Extract tables using pandas
try:
    tables = pd.read_html(StringIO(html_content))
    
    # Dynamic selection of tables based on column names
    market_data = next(
        table for table in tables 
        if "Kod" in table.columns and "Sektör" in table.columns and "Piyasa Değeri (mn $)" in table.columns
    )
    
    return_data = next(
        table for table in tables 
        if "Kod" in table.columns and "Günlük Getiri (%)" in table.columns
    )
except (ValueError, StopIteration) as e:
    print(f"Error parsing HTML tables: {e}")
    exit()

# Create DataFrames
try:
    sector_df = pd.DataFrame({
        "Hisse": market_data["Kod"],
        "Sektör": market_data["Sektör"],
        "Piyasa Değeri (mn $)": market_data["Piyasa Değeri (mn $)"]
    })

    return_df = pd.DataFrame({
        "Hisse": return_data["Kod"],
        "Getiri (%)": return_data["Günlük Getiri (%)"] / 100
    })

    # Merge DataFrames
    df = pd.merge(sector_df, return_df, on="Hisse")
except KeyError as e:
    print(f"Error creating DataFrames: {e}")
    exit()

# Clean "Piyasa Değeri" column
try:
    df["Piyasa Değeri (mn $)"] = (
        df["Piyasa Değeri (mn $)"]
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype('float64')
    )
except ValueError as e:
    print(f"Error processing 'Piyasa Değeri': {e}")
    exit()

# Define color bins
return_bins = [-10, -5, -0.01, 0, 0.01, 5, 10]
return_labels = ["red", "indianred", "lightpink", "lightgreen", "lime", "green"]

df["Renk"] = pd.cut(df["Getiri (%)"], bins=return_bins, labels=return_labels)

# Generate treemap visualization
fig = px.treemap(
    df,
    path=[px.Constant("Borsa İstanbul"), "Sektör", "Hisse"],
    values="Piyasa Değeri (mn $)",
    color="Renk",
    custom_data=["Getiri (%)", "Sektör"],
    color_discrete_map={
        "(?)": "#262931", "red": "red", "indianred": "indianred",
        "lightpink": "lightpink", "lightgreen": "lightgreen",
        "lime": "lime", "green": "green"
    }
)

# Customize hover and text templates
fig.update_traces(
    hovertemplate="<br>".join([
        "Hisse: %{label}",
        "Piyasa Değeri (mn $): %{value}",
        "Getiri: %{customdata[0]}",
        "Sektör: %{customdata[1]}"
    ])
)
fig.data[0].texttemplate = "<b>%{label}</b><br>%{customdata[0]} %"

# Save the figure to the Desktop
desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
output_file = os.path.join(desktop_path, "grafik.html")

offline.plot(fig, filename=output_file)
print(f"Visualization saved at: {output_file}")
