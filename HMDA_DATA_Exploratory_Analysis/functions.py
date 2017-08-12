
# coding: utf-8

# In[2]:

import bokeh
#bokeh.sampledata.download()
from bokeh.sampledata.us_counties import data as counties
from bokeh.sampledata.us_states import data as states

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import math
import sklearn as sk
import collections

import seaborn as sns
import bokeh
from bokeh import mpl
from bokeh.plotting import figure, ColumnDataSource, show
from bokeh.charts import Scatter, Bar, BoxPlot, Histogram
from bokeh.io import output_notebook, push_notebook, gridplot
from bokeh.models import HoverTool, Range1d, LabelSet
from bokeh.layouts import column, gridplot, row

import warnings
from collections import Counter
import copy


# In[4]:

def stateYearSummary(df1):
    
    #groupby at the level of year and state for loan_amount, applicant_income
    x1 = df1.groupby(['As_of_Year', 'State']).agg({'Applicant_Income_000': ['median']})
    x2 = df1.groupby(['As_of_Year', 'State']).agg({'Loan_Amount_000': ['count', 'median', 'sum']})
    x1.columns = x1.columns.droplevel(0)
    x1.columns = ["Median_applicant_income_000"]
    x2.columns = x2.columns.droplevel(0)
    x2.columns = ['No_of_loans', 'Median_loan_amount_000', 'Total_loan_amount_000']
    state_summary = x2.join(x1, how = 'left')
    
    #Obtaining percentage share of each state in a year
    state_summary['Prcnt_no_of_loans_year'] = state_summary[['No_of_loans']].groupby(level=0).apply(lambda x: 100*x/float(x.sum()))['No_of_loans']
    state_summary['Prcnt_total_loan_amount_year'] = state_summary[['Total_loan_amount_000']].groupby(level=0).apply(lambda x: 100*x/float(x.sum()))['Total_loan_amount_000']
    state_summary.reset_index(inplace = True)
    state_summary.columns = ['Year', 'State',  'noofloans', 'medianloanamount000', 'totalloanamount000','medianincome000', 'prcntnoofloans', 'prcnttotalloanamount']
    
    #Obtaining percent change in business (total amount lent) from previous year
    state_summary['prcntchange_in_amount_lent'] = state_summary.groupby('State').totalloanamount000.pct_change()*100
    state_summary = state_summary.round(2)
    state_summary = state_summary.fillna("not available")
    
    return state_summary


#Funtion to summarise yearwise overall business
def yearSummary(df):
    
    #groupby at the level of year for loan_amount, applicant_income
    x1 = df.groupby(['As_of_Year']).agg({'Applicant_Income_000': ['median']})
    x2 = df.groupby(['As_of_Year']).agg({'Loan_Amount_000': ['count', 'median', 'sum']})
    
    x1.columns = x1.columns.droplevel(0)
    x1.columns = ["Median_applicant_income_000"]
    x2.columns = x2.columns.droplevel(0)
    x2.columns = ['No_of_loans', 'Median_loan_amount_000', 'Total_loan_amount_000']
    
    yearwise_summary = x1.join(x2, how = 'left')
    yearwise_summary.reset_index(inplace = True)
    yearwise_summary.columns = ['Year', 'median_applicant_income', 'no_of_loans', 'median_loan_amount', 'Total_amount_lent']
    
    #Obtaining percent change in overall business (amount lent) from previous year
    yearwise_summary['prcnt_change_amount_lent'] = yearwise_summary[['Total_amount_lent']].pct_change()*100
    yearwise_summary = yearwise_summary.round(2)
    yearwise_summary = yearwise_summary.fillna("not available")
    
    return yearwise_summary

def plotSummaryStateYear(df1):
    
    #importing required modules as these function are copiled from a different ipython notebook
    import bokeh
    from bokeh.plotting import figure, ColumnDataSource
    from bokeh.models import HoverTool
    from bokeh.charts import BoxPlot, Histogram, Bar


    #summarising the dataframe for plotting
    state_summary = stateYearSummary(df1)
    yearwise_summary = yearSummary(df1)

    #Plots showing marketshare across states for different years
    plots = {}
    for year in set(state_summary.Year):
        
        df = state_summary[state_summary.Year == year]
        df = df.sort(['prcnttotalloanamount'])
        
        df.noofloans = df.noofloans/1000

        
        #transparency proportional to the median income
        alphas = 1*df.medianincome000/max(df.medianincome000)

        colors = 'forestgreen'
        
        #pasaing dataframe as source
        s = ColumnDataSource(data = df)
        
        #tooltips for showing other details
        hover = HoverTool(tooltips=[("Marketshare: ", "@prcnttotalloanamount"),
                                    ("Prcnt Change in Business:", "@prcntchange_in_amount_lent"),
                                    ("Median_loan_amount: ", "@medianloanamount000"),
                                    ("Median_applicant_income:", "@medianincome000"),
                                    ])
        
        sizes = 50 * df.medianloanamount000/ max(df.medianloanamount000)
        
        #figure layout
        p = figure(title = "Business Summary across states in"+str(year), plot_height = 300, tools = [hover],
                    plot_width = 400,y_range = list(df.State), x_axis_label = "Market share (Percent of Total Amount Lent that Year)")
        
        #circles for lillipop chart
        p.circle(y = 'State', x = 'prcnttotalloanamount', size = sizes, color = colors, alpha = alphas, source = s)
    
        plots["marketshare_"+str(year)] = p
        
    #plot of median income across different states for different years    
    medianincome = bokeh.charts.Bar(state_summary, label = 'Year', values = 'medianincome000', group = 'State',
                                    plot_width = 400, plot_height = 400, title = "Median Income (in USD 1000s)",
                                    legend='top_right')
    
    #plot of median loan amount
    medianloanamount = bokeh.charts.Bar(state_summary, label = 'Year', values = 'medianloanamount000', group = 'State',
                          plot_height = 400,  plot_width = 400, title = "Median Amount Lent (in USD 1000s)", 
                                        legend='top_right')
    #plot of number of loans
    noofloans = bokeh.charts.Bar(state_summary, label = 'Year', values = 'noofloans', group = 'State',
                                 plot_height = 400, plot_width = 400, title = "Number of loans", legend='top_right')
    
    
    plots["medianincome"] = medianincome
    plots["medianamountlent"] = medianloanamount
    plots["noofloans"] = noofloans
        
    
    #plots showing business across years
    
    df = yearwise_summary

    df.Total_amount_lent = df.Total_amount_lent/1000
    df.no_of_loans = df.no_of_loans/1000
        

    colors = 'red'
     
    #passing data as source    
    s = ColumnDataSource(data = df)
        
    #toltips for showing other details
    hover = HoverTool(tooltips=[("Total aount lent (in millions): ", "@Total_amount_lent"),
                                ("Prcnt Change in Business:", "@prcnt_change_amount_lent"),
                                ("Median_loan_amount: ", "@median_loan_amount"),
                                ("Median_applicant_income:", "@median_applicant_income"),
                                ])
    #figure layout
    p = figure(title = "Business Summary across years", plot_height = 400, tools = [hover],
                plot_width = 400, x_axis_label = "Year", y_axis_label = "Total amount lent in millions of USD")
   
    #bar graph for lollipop chart
    p.vbar(x = 'Year' , width = 0.02,  top = 'Total_amount_lent', color = colors,  source = s)
    
    #circles for lollipop chart
    p.circle(y = 'Total_amount_lent', x = 'Year', size = 10, color = colors,  source = s)
    
    
    
    plots["amountlentVSyear"] = p
   
    
          


    #Passing data as source
    s = ColumnDataSource(data = df)
    
    #tooltips for showing other details
    hover = HoverTool(tooltips= [("No. of loans (in 1000s): ", "@no_of_loans"),
                                ("Median_loan_amount: ", "@median_loan_amount"),
                                ("Median_applicant_income:", "@median_applicant_income"),
                                ])
    
    #figure layout
    p = figure(title = "Business Summary across years", plot_height = 400, tools = [hover],
                plot_width = 400, x_axis_label = "Year", y_axis_label = "No. of Loans (in 1000s)")
    
    #bar graph for lollipop chart
    p.vbar(x = 'Year' , width = 0.02,  top = 'no_of_loans', color = colors, source = s)
    
    #circles for lollipop chart
    p.circle(y = 'no_of_loans', x = 'Year', size = 10, color = colors,  source = s)
    
    plots["Numberofloans"] = p
    
    
        
        
    return plots
       
        


# In[9]:

#Function to summarise a variable based on other important parameters:

def summariseColumn(data, by, column):
      
    if by == 'year':
        by1 = "As_of_Year"
        
    elif by == 'state':
        by1 = "State"
        
    else:
        print("invalid argument, can group by either state or year")
        return None
    
    x1 = data.groupby([by1, column]).agg({"Applicant_Income_000": ["median"]})
    x2 = data.groupby([by1, column]).agg({"Loan_Amount_000": ["count", "median", "sum"]})   
            
    x1.columns = x1.columns.droplevel(0)
    x1.columns = ["Median_applicant_income_000"]
    x2.columns = x2.columns.droplevel(0)
    x2.columns = ['No_of_loans', 'Median_loan_amount_000', 'Total_loan_amount_000']
    
    data = x1.join(x2, how = 'left')
    data.reset_index(inplace = True)
    data.columns = [ by, column, "medianincome000", "noofloans", "medianloanamount000", "totalloanamount000"]
    data['prcnt_amount_lent'] = data.groupby(by).totalloanamount000.apply(lambda x: 100*x/float(x.sum()))
    df = data.round(2)
    
    return df


# In[10]:

#Function to plot summary of a vaiable
def plotSummary(df, column):
    from bokeh.plotting import ColumnDataSource
    from bokeh.charts import BoxPlot, Histogram, Bar

    d1 = summariseColumn(df, 'year', column)
    d1.noofloans = d1.noofloans/1000
    d1.totalloanamount000 = d1.totalloanamount000/1000
    
    d2 = summariseColumn(df, 'state', column)
    d2.noofloans = d2.noofloans/1000
    
    s1 = ColumnDataSource(d1)
    s2 = ColumnDataSource(d2)
    
    plots = {}
    
    year = Bar(d1, label='year', values='prcnt_amount_lent', group = column, plot_width = 450,
                title = "Market Share (prcnt amount lent)",
                legend='top_right')  
    
    plots['year'] = year
    

    
    state = Bar(d2, label='state', values='prcnt_amount_lent', group=column ,y_range = list(d2.state), 
                plot_width = 450,
                title="Market Share (prcnt amount lent)", legend='top_right')
              
    plots['state'] = state
    
    
    medianincome = Bar(d2, label = 'state', values = 'medianincome000', group = column, plot_width = 300,
                       plot_height = 400, title = "Median Income (in USD 1000s)", legend='top_right')
    plots['medianincome'] = medianincome
    
    
    medianloanamount = Bar(d2, label = 'state', values = 'medianloanamount000', group = column, plot_width = 300,
                         plot_height = 400, title = "Median Loan Amount(in USD 1000s)", legend='top_right')
    
    plots['medianloanamount'] = medianloanamount
    
    
    noofloans = Bar(d1, label = 'year', values = 'noofloans', group = column, plot_width = 300,
                          plot_height = 400, title = "Noofloans(in 1000s)", legend='top_right')
    
    plots['noofloansyear'] = noofloans
    
    
    noofloans = Bar(d2, label = 'state', values = 'noofloans', group = column, plot_width = 300,
                          plot_height = 400, title = "Noofloans(in 1000s)", legend='top_right') 
    
    plots['noofloansstate'] = noofloans
    
    amountlent = Bar(d1, label = 'year', values = 'totalloanamount000', group = column, plot_width = 300,
                          plot_height = 400, title = "Total amount lent(in USD millions)", legend='top_right')
    
    plots['amountlent'] = amountlent
    
    return(plots)


# In[11]:

def parentSummary(masterdata):
    Parent_Summary = masterdata.groupby(['As_of_Year','State', 'Parent_Name_TS']).agg(
                                        {'Loan_Amount_000':['count', 'median', 'sum']})

    Parent_Summary.columns = Parent_Summary.columns.droplevel(0)
    Parent_Summary.reset_index(inplace = True)

    Parent_Summary.columns = ['year', 'state', 'parent_Institution', 'noofloans', 'medianloanamount', 'totalamountlent']

    Parent_Summary['prcnttotalamountlent'] = Parent_Summary.groupby(['year', 'state']).totalamountlent.apply(
                                            lambda x: 100*x/float(x.sum()))
    
    return Parent_Summary


# In[1]:

def mapsummary(column, year):
    
    import bokeh
    #bokeh.sampledata.download()
    from bokeh.sampledata.us_counties import data as counties
    from bokeh.sampledata.us_states import data as states
    

    for code in counties:
        counties[code]["name"] = counties[code]["name"].lower()

    county_name = [counties[code]["name"] for code in counties if counties[code]["state"] in ['dc','de','md', 'va', 'wv']]
    state_name = [counties[code]["state"] for code in counties if counties[code]["state"] in ['dc','de','md', 'va', 'wv']]

    masterdata = pd.read_csv("masterdata.csv")
    
    masterdata = masterdata[masterdata.County_Name.notnull()]
    masterdata = masterdata[['As_of_Year', 'State', 'County_Name', 'Loan_Amount_000', 'Applicant_Income_000']]
    masterdata.State = [i.lower() for i in list(masterdata.State)]
    masterdata.County_Name = [i.lower() for i in list(masterdata.County_Name)]
    masterdata['id'] = masterdata.State+"_"+masterdata.County_Name
    masterdata['id'] = [i[:10] for i in list(masterdata.id)]
    masterdata.Applicant_Income_000 = masterdata.Applicant_Income_000*1000

    ids = [state_name[i]+"_"+county_name[i] for i in range(len(county_name))]
    ids = [i[:10] for i in ids]

    x1 = masterdata.groupby(['As_of_Year', 'id']).agg({"Loan_Amount_000":["count", "median", "sum"]})
    x1.columns = x1.columns.droplevel(0)
    x1.columns = ["noofloans", "medianloanamount", "totalloanamount"]

    x2 = masterdata.groupby(['As_of_Year', 'id']).agg({"Applicant_Income_000":["median"]})
    x2.columns = x2.columns.droplevel(0)
    x2.columns = ["medianincome"]
    x1 = x1.join(x2, how = 'left')
    x1.reset_index(inplace = True)

    summary = x1
    summary.columns = ['year', 'id', "noofloans", "medianloanamount", "totalloanamount", "medianincome" ]
    
    summary = summary[summary.year == year]
    rate = [int(summary[summary.id == ids[i]][column]) if ids[i] in list(summary.id) else 0 for i in range(len(ids))]
    
    return rate

