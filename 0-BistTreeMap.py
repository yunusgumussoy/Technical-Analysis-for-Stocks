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
url="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"

# Fetch the HTML content
r=requests.get(url).text

# Extract tables using pandas
tablo=pd.read_html(StringIO(r))[2]

# Create DataFrames
sektör=pd.DataFrame({"Hisse":tablo["Kod"],"Sektör":tablo["Sektör"],"Piyasa Değeri (mn $)":tablo["Piyasa Değeri (mn $)"]})
tablo2=pd.read_html(StringIO(r))[7]
getiri=pd.DataFrame({"Hisse":tablo2["Kod"],"Getiri (%)":tablo2["Günlük Getiri (%)"]/100})
df=pd.merge(sektör,getiri,on="Hisse")

# Clean "Piyasa Değeri" column
df["Piyasa Değeri (mn $)"]=df["Piyasa Değeri (mn $)"].str.replace('.', '').str.replace(',', '.').astype('float64')

# Define color bins
renkaralık=[-10,-5,-0.01,0,0.01,5,10]
df["Renk"]=pd.cut(df["Getiri (%)"],bins=renkaralık,labels=["red","indianred","lightpink","lightgreen","lime","green"])

# Generate treemap visualization
fig=px.treemap(df,path=[px.Constant("Borsa İstanbul"),"Sektör","Hisse"],values="Piyasa Değeri (mn $)",
               color="Renk",custom_data=["Getiri (%)","Sektör"],
               color_discrete_map ={"(?)":"#262931","red":"red", "indianred":"indianred","lightpink":"lightpink", 'lightgreen':'lightgreen','lime':'lime','green':'green'})

# Customize hover and text templates
fig.update_traces(
    hovertemplate="<br>".join([
        "Hisse: %{label}",
        "Piyasa Değeri (mn $): %{value}",
        "Getiri: %{customdata[0]}",
        "Sektör: %{customdata[1]}"
    ]))
fig.data[0].texttemplate="<b>%{label}</b><br>%{customdata[0]} %"

# Save the figure to the Desktop
masaustu=os.path.join(os.path.expanduser('~'),"Desktop")
offline.plot(fig,filename=masaustu+"/grafik.html")