#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 2017

@authors: Ilya Kats, Nnaemezue Obi-Eyisi Pavan Akula
"""

from flask import render_template, make_response, flash, request
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import matplotlib.dates as mdates #import DateFormatter
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.finance import candlestick_ohlc
import matplotlib.ticker as mticker
import matplotlib.mlab as mlab
from scipy.stats import norm
from app import app

from .dbfunctions import get_teams, get_leagues, get_league_teams, get_seasons, get_league_details, get_team_details, get_player_details, \
get_team_winlose, get_team_name, get_team_shoton, get_team_shotoff, get_team_foulcommits, get_correlation, get_teamStats



def bytespdate2num(fmt, encoding='utf-8'):
    strconverter = mdates.strpdate2num(fmt)
    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)
    return bytesconverter

def pd_to_html_num_formatters(df):
    keys=[]
    values=[]
    float_format2 = lambda x: '{:,.2f}'.format(x)
    float_format4 = lambda x: '{:,.4f}'.format(x)
    num_format = lambda x: '{:,}'.format(x)
    for (column, dtype) in df.dtypes.iteritems():
        if (dtype in [np.dtype('int64'), np.dtype('float64')]):
            keys.append(column)
            if (column == 'Daily Returns'):
                values.append(float_format4)
            else:
                values.append(num_format if dtype == np.dtype('int64') else float_format2)
    return(dict(zip(keys, values)))

@app.route('/', methods=['GET', 'POST'])
@app.route('/home/<league>', methods=['GET', 'POST'])
def home(league=None):
    leaugeTable,lid = get_leagues()
    lid = str(lid)
    if league==None:
        league = lid
    leaugeTeams = get_league_teams(league)
    leaugeSeasons = get_seasons(league)
    leaugeDetails = get_league_details(league)
#                           leaugeTeams=leaugeTeams,
#                           leaugeSeasons = leaugeSeasons,
#                           leaugeDetails = leaugeDetails,
    return render_template('home.html', 
                           leaugeTable=leaugeTable, 
                           leaugeSeasons=leaugeSeasons,
                           leaugeDetails=leaugeDetails,
                           leaugeTeams=leaugeTeams,
                           league = league,
                           home = 'class=active data-toggle=pill',
                           team='', 
                           game='')


@app.route('/team/<league>/<season>/<team>', methods=['GET', 'POST'])
def team(league=None,season=None,team=None):
    print(league, season, team)  
    
    teamDetails, playerLatest, teamName = get_team_details(league, season, team)
    gameoutcome, other = get_team_winlose(league, season, team)
    #teamDetails = get_team_details()
    num_formatters = pd_to_html_num_formatters(gameoutcome)
    gameoutcome = [gameoutcome.to_html(formatters = num_formatters, classes="table table-striped table-bordered table-sm", index=False)]
    
    shoton, other = get_team_shoton(league, season, team)
    num_formatters = pd_to_html_num_formatters(shoton)
    shoton = [shoton.to_html(formatters = num_formatters, classes="table table-striped table-bordered table-sm", index=False)]
    
    shotoff, other = get_team_shotoff(league, season, team)
    num_formatters = pd_to_html_num_formatters(shotoff)
    shotoff = [shotoff.to_html(formatters = num_formatters, classes="table table-striped table-bordered table-sm", index=False)]
    
    foulcommit, other = get_team_foulcommits(league, season, team)
    num_formatters = pd_to_html_num_formatters(foulcommit)
    foulcommit = [foulcommit.to_html(formatters = num_formatters, classes="table table-striped table-bordered", index=False)]
    
    corrDf = get_correlation(league, season)
    num_formatters = pd_to_html_num_formatters(corrDf)
    corrDf = [corrDf.to_html(formatters = num_formatters, classes="table table-striped table-bordered", index=True)]
    
    teamStats1, teamStats2 = get_teamStats(league, season, team)
    #print(teamStats1.dtype)
    #teamStats1 = num_formatters = pd_to_html_num_formatters(teamStats1)
    #teamStats1 = [teamStats1.to_html(formatters = num_formatters, classes="table table-striped table-bordered", index=True)]
    
    
    skills = ['Overall Rating','Potential','Preferred Foot','Attacking Work Rate','Defensive Work Rate','Crossing', 'Finishing Rate', 'Heading Accuracy', 
              'Short Passing', 'Volleys', 'Dribbling Rate','Curve', 'Free Kick Accuracy', 'Long Passing','Ball Control', 'Acceleration', 'Sprint Speed',
              'Agility', 'Reactions', 'Balance', 'Shot Power', 'Jumping', 'Stamina', 'Strength', 'Long Shots', 'Aggression', 'Interception', 'Vision', 'Positioning',
              'Penalties', 'Marking', 'Standing Tackle', 'Sliding Tackle', 'Goalkeeping']

    nskills = ['Preferred Foot','Attacking Work Rate','Defensive Work Rate','Crossing', 'Heading Accuracy', 
              'Short Passing', 'Volleys', 'Dribbling Rate','Curve', 'Long Passing', 'Sprint Speed',
              'Agility', 'Reactions', 'Balance', 'Jumping', 'Strength', 'Long Shots', 'Interception', 'Vision', 'Positioning',
              'Marking', 'Standing Tackle', 'Sliding Tackle', 'Goalkeeping']



    return render_template('team.html', 
                           teamDetails=teamDetails,
                           playerLatest=playerLatest,
                           teamName=teamName,
                           skills=skills,
                           nskills=nskills,
                           season=season,
                           gameoutcome = gameoutcome,
                           shoton=shoton,
                           shotoff=shotoff,
                           foulcommit=foulcommit,
                           corrDf=corrDf,
                           teamStats1=teamStats1,
                           league=league,
                           teamid=team,
                           home = '',
                           team='class=active data-toggle=pill',
                           game='')

@app.route("/graph_display1.png/<playerID>/<playerfeature>/<player>")
def graph_display1(playerID, playerfeature, player):
    
    playerID = int(playerID)
    plt.close('all')
    
    playerDf = get_player_details(playerID)
    playerDf = playerDf.dropna()
    #Convert text to date
    playerDf['Date_pd'] = pd.to_datetime(playerDf.lsd)
    playerDf = playerDf.sort_values(by='Date_pd', ascending=True)
    
    #Convert date to string format
    playerDf['date1'] = playerDf['Date_pd'] .apply(lambda x: datetime.datetime.strftime(x, '%m/%d/%Y'))
    
    skills = ['Preferred Foot','Attacking Work Rate','Defensive Work Rate','Crossing', 'Heading Accuracy', 
              'Short Passing', 'Volleys', 'Dribbling Rate','Curve', 'Long Passing', 'Sprint Speed',
              'Agility', 'Reactions', 'Balance', 'Jumping', 'Strength', 'Long Shots', 'Interception', 'Vision', 'Positioning',
              'Marking', 'Standing Tackle', 'Sliding Tackle', 'Goalkeeping']
    
    if (playerfeature not in skills):
        playerDf['data'] = playerDf.date1.str.cat(playerDf[playerfeature].astype("str"), sep=',')

        resultList = playerDf.data.tolist()
        
        x, y = np.loadtxt(resultList,
                          delimiter=',',
                          unpack=True,
                          converters={0: bytespdate2num('%m/%d/%Y')})

    
    plt.close('all')
    fig, ax = plt.subplots()
    ax.grid(True)
    ax.plot(x, y)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.xlabel('Date')
    plt.ylabel(playerfeature)
    plt.title('Change in ' + playerfeature + ' Skill - ' + player)
    fig.autofmt_xdate()
    fig = plt.gcf()
    fig.tight_layout()
    canvas = FigureCanvas(fig) 
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    plt.clf()
    return response

@app.route("/graph_display2.png/<playerID>/<playerfeature>/<player>")
def graph_display2(playerID, playerfeature, player):
    
    playerID = int(playerID)
    plt.close('all')
    
    playerDf = get_player_details(playerID)
    playerDf = playerDf.dropna()
    #Convert text to date
    playerDf['Date_pd'] = pd.to_datetime(playerDf.lsd)
    playerDf = playerDf.sort_values(by='Date_pd', ascending=True)
    
    #Convert date to string format
    playerDf['date1'] = playerDf['Date_pd'] .apply(lambda x: datetime.datetime.strftime(x, '%m/%d/%Y'))
    
    if (playerfeature == 'Goalkeeping'):
        playerDf['data'] = playerDf.date1.astype("str") + ',' + playerDf['Goalkeeping Driving'].astype("str") \
                    + ',' + playerDf['Goalkeeping Handling'].astype("str") + ',' + playerDf['Goalkeeping Kicking'].astype("str") \
                    + ',' + playerDf['Goalkeeping Positioning'].astype("str") + ',' + playerDf['Goalkeeping Reflexes'].astype("str")
    

        resultList = playerDf.data.tolist()
        
        x, y1, y2, y3, y4, y5 = np.loadtxt(resultList,
                          delimiter=',',
                          unpack=True,
                          converters={0: bytespdate2num('%m/%d/%Y')})

    
    plt.close('all')
    fig, ax = plt.subplots()
    #ax.grid(True)
       
    ax.plot(x, y1, color='navy', alpha=.50, label='Driving')
    ax.plot(x, y2, color='blue', alpha=.50, label='Handling')
    ax.plot(x, y3, color='cyan', alpha=.50, label='Kicking')
    ax.plot(x, y4, color='green', alpha=.50, label='Positioning')
    ax.plot(x, y5, color='red', alpha=.50, label='Reflexes')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.xlabel('Date')
    plt.ylabel(playerfeature)
    
    fig.autofmt_xdate()
    fig = plt.gcf()
    plt.legend(loc='best', fancybox=True)
    leg = plt.gca().get_legend()
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    
    # see text.Text, lines.Line2D, and patches.Rectangle for more info on
    # the settable properties of lines, text, and rectangles
    frame.set_facecolor('0.90')      # set the frame face color to light gray
    plt.setp(ltext, fontsize='x-small')    # the legend text fontsize
    plt.setp(llines, linewidth=1)      # the legend linewidth
    leg.get_frame().set_alpha(0.5)
        
    fig.tight_layout()
    canvas = FigureCanvas(fig) 
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    plt.clf()
    return response

@app.route("/graph_display3.png/<league>/<season>/<team>")
def graph_display3(league=None,season=None,team=None):
    other, df = get_team_winlose(league, season, team)
    teamName = get_team_name(team)
    
    labels = df.Opponent.tolist()
    x = np.arange(len(labels))
    y = df.GoalsMade.tolist()
    
    plt.close('all')
    fig, ax = plt.subplots()
    #ax.grid(True)
    ax.set_xlim([0,len(labels)])
    ax.bar(x, y, color='navy', align='center', edgecolor='white',alpha=.80)
    ax.set_xticklabels(labels)
    ax.set_xticks(x, minor = True)
    plt.xticks(x, labels)
    
    ax.set_xticklabels(labels, rotation=90)
    
    plt.xlabel('Opponent')
    plt.ylabel('Goals')
    plt.title(teamName + ' - Goals Made During The Season ' + season)
    fig = plt.gcf()
    fig.tight_layout()
    canvas = FigureCanvas(fig) 
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    plt.clf()
    return response

@app.route("/graph_display4.png/<league>/<season>/<team>")
def graph_display4(league=None,season=None,team=None):
    other, df = get_team_shoton(league, season, team)
    teamName = get_team_name(team)
    
    #df['shoton50T'] = 50.00 - df['SOGT']
    #df['shoton50O'] = 50.00 - df['SOGO']
    
    labels = df.Opponent.tolist()
    x = np.arange(len(labels))
    y1 = df.SOGT.tolist()
    y2 = df.SOGO.tolist()
  
    
    plt.close('all')
    fig, ax = plt.subplots()
    #ax.grid(True)
    ax.set_xlim([0,len(labels)])
    ax.bar(x, y1, color='#d62728', label=teamName)
    ax.bar(x, y2, label='Opponent', bottom=y1)
    #ax.axhline(y=50.00, color='k',linewidth=1,linestyle='-')
    ax.legend()
    ax.set_xticks(x, minor = True)
    plt.xticks(x, labels)
    
    ax.set_xticklabels(labels, rotation=90)

    #plt.xticks(rotation=90)
#    for label in ax.xaxis.get_ticklabels():
#        label.set_rotation(90)
    
    plt.xlabel('Opponent')
    plt.ylabel('Shoton Goal')
    plt.title(teamName + ' - Shot On Goal During The Season ' + season)
    fig = plt.gcf()
    fig.tight_layout()
    canvas = FigureCanvas(fig) 
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    plt.clf()
    return response
    
@app.route("/graph_display5.png/<league>/<season>/<team>")
def graph_display5(league=None,season=None,team=None):
    other, df = get_team_shotoff(league, season, team)
    teamName = get_team_name(team)
    
    #df['shotoff50T'] = 50.00 - df['SOGT']
    #df['shotoff50O'] = 50.00 - df['SOGO']
    
    labels = df.Opponent.tolist()
    x = np.arange(len(labels))
    y1 = df.SOGT.tolist()
    y2 = df.SOGO.tolist()
  
    
    plt.close('all')
    fig, ax = plt.subplots()
    #ax.grid(True)
    ax.set_xlim([0,len(labels)])
    ax.bar(x, y1, color='#d62728', label=teamName)
    ax.bar(x, y2, label='Opponent', bottom=y1)
    #ax.axhline(y=50.00, color='k',linewidth=1,linestyle='-')
    ax.legend()
    ax.set_xticks(x, minor = True)
    plt.xticks(x, labels)
    
    ax.set_xticklabels(labels, rotation=90)

    #plt.xticks(rotation=90)
#    for label in ax.xaxis.get_ticklabels():
#        label.set_rotation(90)
    
    plt.xlabel('Opponent')
    plt.ylabel('Shotoff Goal')
    plt.title(teamName + ' - Shot Off Goal During The Season ' + season)
    fig = plt.gcf()
    fig.tight_layout()
    canvas = FigureCanvas(fig) 
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    plt.clf()
    return response

@app.route("/graph_display6.png/<league>/<season>/<team>")
def graph_display6(league=None,season=None,team=None):
    other, df = get_team_foulcommits(league, season, team)
    teamName = get_team_name(team)
    
    df['foul50T'] = 50.00 - df['FoulT']
    df['foul50O'] = 50.00 - df['FoulO']
    
    labels = df.Opponent.tolist()
    x = np.arange(len(labels))
    y1 = df.foul50T.tolist()
    y2 = df.foul50O.tolist()
  
    
    plt.close('all')
    fig, ax = plt.subplots()
    #ax.grid(True)
    ax.set_xlim([0,len(labels)])
    ax.bar(x, y1, color='green', label='Opponent', bottom=50.00, alpha=.80)
    ax.bar(x, y2, color='red', label=teamName, bottom=50.00, alpha=.80)
    ax.axhline(y=50.00, color='k',linewidth=1,linestyle='-')
    ax.legend()
    ax.set_xticks(x, minor = True)
    plt.xticks(x, labels)
    
    ax.set_xticklabels(labels, rotation=90)

    #plt.xticks(rotation=90)
#    for label in ax.xaxis.get_ticklabels():
#        label.set_rotation(90)
    
    plt.xlabel('Opponent')
    plt.ylabel('Fouls %')
    plt.title(teamName + ' - Fouls Commited During The Season ' + season)
    fig = plt.gcf()
    fig.tight_layout()
    canvas = FigureCanvas(fig) 
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    plt.clf()
    return response

@app.route("/graph_display7.png/<league>/<season>/<team>")
def graph_display7(league=None,season=None,team=None):
    other, df = get_team_winlose(league, season, team)
    teamName = get_team_name(team)

    labels = df.Opponent.tolist()    
    df = df.reset_index()
    #x = np.arange(len(labels))
    #y = df.Diff.tolist()

    x = df.index.values
    y = df['Diff']


    d = df['Diff'] == 0
    w = df['Diff'] > 0
    l = df['Diff'] < 0
    
    plt.close('all')
    fig, ax = plt.subplots()
    #ax.grid(True)
    ax.set_xlim([0,len(labels)])
    ax.bar(x[w], y[w], color='green', align='center', edgecolor='white',alpha=.80,label='Won By Goals')
    ax.bar(x[l], abs(y[l]), color='red', align='center', edgecolor='white',alpha=.80,label='Lost By Goals')
    plt.scatter(x[d], y[d], s=30,c='navy',alpha=.80,label='Draw')
    ax.set_xticklabels(labels)
    ax.set_xticks(x, minor = True)
    plt.xticks(x, labels)
    ax.legend()
    ax.set_xticklabels(labels, rotation=90)
    
    plt.xlabel('Opponent')
    plt.ylabel('Win/Lost By')
    plt.title(teamName + ' - Matches Outcome - Season ' + season)
    fig = plt.gcf()
    fig.tight_layout()
    canvas = FigureCanvas(fig) 
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    plt.clf()
    return response

@app.route("/graph_display8.png/<league>/<season>/<team>")
def graph_display8(league=None,season=None,team=None):
    #https://pythonprogramming.net/stock-price-correlation-table-python-programming-for-finance/
    plt.close('all')

    corrDf = get_correlation(league, season)

    corrMatrix = corrDf.as_matrix()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    heatmap1 = ax.pcolor(corrDf.values, cmap=plt.cm.RdYlGn)
    for y in range(corrMatrix.shape[0]):
        for x in range(corrMatrix.shape[1]):
            plt.text(x + 0.5, y + 0.5, '%.2f' % corrMatrix[y, x],
                     horizontalalignment='center',
                     verticalalignment='center',
                     )
    fig.colorbar(heatmap1)

    ax.set_xticks(np.arange(corrDf.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(corrDf.shape[0]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    column_labels = corrDf.columns
    row_labels = corrDf.index
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    #plt.xticks(rotation=45)
    #plt.yticks(rotation=45)
    heatmap1.set_clim(-1,1)
    plt.tight_layout()
    fig = plt.gcf()
    fig.tight_layout()
    canvas = FigureCanvas(fig)
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response
