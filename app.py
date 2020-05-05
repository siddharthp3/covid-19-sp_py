import requests
import json
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from itertools import zip_longest
from flask import Flask
import os

# Getting latest country data
r_latest_stats = requests.get('https://api.rootnet.in/covid19-in/stats/latest')
latest_stats = r_latest_stats.json()

# Statewise history and total cases for each day
r_statewise_history = requests.get('https://api.rootnet.in/covid19-in/unofficial/covid19india.org/statewise/history')
statewise_history = r_statewise_history.json()

# Parsing JSON response for country data
total_summary = latest_stats['data']['summary']
regional_data = latest_stats['data']['regional']
last_referenced = latest_stats['lastRefreshed']
last_referenced_str = str(last_referenced)

states = [eachstate['loc'] for eachstate in regional_data]
confirmed_cases = [confcases['confirmedCasesIndian'] for confcases in regional_data]
discharged = [discharg['discharged'] for discharg in regional_data]
deaths = [deaths['deaths'] for deaths in regional_data]
foreign_cases = [foreign_cases['confirmedCasesForeign'] for foreign_cases in regional_data]
all_regional_data = list(zip(states,confirmed_cases,discharged,deaths,foreign_cases))

# Parsing JSON response for Statewise history and total cases for each day
history_data = statewise_history['data']['history']

# Creating a pandas data frame for country data
df_latest_stats = pd.DataFrame(all_regional_data, columns = ['State', 'Confirmed cases', 'Discharged','Deaths','Foreign cases'])
df_latest_stats['Active Cases'] = df_latest_stats['Confirmed cases']-df_latest_stats['Discharged']
df_latest_stats['% Death'] = (df_latest_stats['Deaths'] / df_latest_stats['Confirmed cases']) * 100

# Creating a pandas data frame for Statewise history and total cases for each day
df_history_data = pd.DataFrame(history_data)

df_cases = df_history_data.total.apply(pd.Series)
df_cases['Date'] = df_history_data['day']
df_cases['Rise in confirmed cases'] = df_cases['confirmed'].diff(periods = 1)
#df_cases = df_cases.set_index('Date')
#print(df_cases.head(5))

# Saving data to a csv file
#df.to_csv('Covid-19_India.csv')



#Dash App to dsiplay tables and graphs on web
server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name = __name__, server = server)



app.layout = html.Div(children=[

        html.H3(children="COVID-19 Summary-India"),

        #Table display
        html.Div(
            children=[
                dash_table.DataTable(
                id="Table",
                columns=[{"name":i, "id": i} for i in df_latest_stats.columns],
                data = df_latest_stats.to_dict('records'),
                #filter_action="native",
                sort_action="native",)
                ]
        ),

        #Graphs
        dcc.Graph(
            id = "covid_graph-1",
            figure={
                'data': [
                    {'x': df_latest_stats['State'], 'y':df_latest_stats['Confirmed cases'], 'type':'line', 'name': 'Confirmed cases'},
                    {'x': df_latest_stats['State'], 'y':df_latest_stats['Active Cases'], 'type':'bar', 'name': 'Active Cases'}
                ],
                'layout':{
                    'title' : 'Confirmed and Active cases by state',
                    'yaxis':{
                        'title':'Confirmed and Active cases'
                    }
                }
            }
        ),

        dcc.Graph(
            id = "covid_graph-2",
            figure={
                'data': [
                    {'x': df_cases['Date'], 'y':df_cases['Rise in confirmed cases'], 'type':'bar', 'name': 'Rise in confirmed cases'},
                ],
                'layout':{
                    'title' : 'Rise in confirmed cases',
                    'xaxis':{
                        'title':'Day'
                    }
                }
            }
        ),

         dcc.Graph(
            id = "covid_graph-3",
            figure={
                'data': [
                    {'x': df_cases['Date'], 'y':df_cases['confirmed'], 'type':'line', 'name': 'Confirmed cases'},
                    {'x': df_cases['Date'], 'y':df_cases['recovered'], 'type':'line', 'name': 'Recovered Cases'},
                ],
                'layout':{
                    'title' : 'Confirmed and Recovered cases daily',
                    'xaxis':{
                        'title':'Day'
                    }
                }
            }
        ),
    
        dcc.Graph(
            id = "covid_graph-4",
            figure={
                'data': [
                    {'x': df_latest_stats['State'], 'y':df_latest_stats['Deaths'], 'type':'line', 'name': 'Deaths'},
                    {'x': df_latest_stats['State'], 'y':df_latest_stats['Discharged'], 'type':'line', 'name': 'Discharged'},
                    #{'x': df_latest_stats['State'], 'y': df_latest_stats['% Death'], 'type':'line', 'name': 'Percentage of deaths for each State'}
                ],
                'layout':{'title': 'Deaths vs Discharged by state'},
            }
        ),

        dcc.Graph(
            id = "covid_graph-5",
            figure={
                'data': [
                    {'x': df_latest_stats['State'], 'y': df_latest_stats['% Death'], 'type':'line', 'name': 'Percentage of deaths for each State'}
                ],
                'layout':{'title': 'Percentage of deaths for each State'},
            }
        ),

        dcc.Markdown('''
            
            **COVID-19 Summary-India.**

            ***Created by*** : Siddharthp8

            ***Created using*** : Python (Dash, Pandas)

            *API's used* : 
            * [https://api.rootnet.in/covid19-in/stats/latest]
            * [https://api.rootnet.in/covid19-in/unofficial/covid19india.org/statewise/history]

           ''' )

        
    ])


if __name__==__name__ == "__main__":
    app.run_server(debug=True)
