#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 2017

@authors: Ilya Kats, Nnaemezue Obi-Eyisi Pavan Akula
"""

from app import app, db
from .models import Team, Player, Country, League, Team_Attributes, Player_Attributes, Match
import pandas as pd
import datetime
import time
from sqlalchemy import func, desc
from sqlalchemy.sql.expression import label
import numpy as np
from dateutil.relativedelta import relativedelta
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression
from bs4 import BeautifulSoup

def get_teams():
    
    result = db.session.query(Team).all()
    df = pd.DataFrame()
    for row in result:
        data = {'Team ID': row.team_short_name, 'Team': row.team_long_name}
        df = df.append(data, ignore_index=True)
    return df

def get_leagues():
    result = League.query.with_entities(League.name, League.id).distinct()
    df = pd.DataFrame()
    for row in result:
        data = {'League': row.name,'LeagueId': str(row.id), 'Lid': int(row.id)}
        df = df.append(data, ignore_index=True)
    
    
    df = df.sort_values(by='Lid', ascending=True)
    df = df.set_index('Lid')
    lid = League.query.with_entities(League.id).order_by(League.id).first()
    lid = str(lid).replace(',','').replace('(','').replace(')','')
    return df, lid

def get_seasons(league):
    result = Match.query.with_entities(Match.league_id, Match.season).filter(Match.league_id == int(league)).distinct()
    df = pd.DataFrame()
    for row in result:
        data = {'LeagueId':'L' + str(row.league_id), 'Season': row.season, 'SeasonId': str(row.season).replace('/','-')}
        df = df.append(data, ignore_index=True)
    if df.shape[0]>0:
        df = df.sort_values(by='Season', ascending=False)
    return df

def get_league_details(league):
    result = db.session.query(label('Country',Country.name), League.name, League.Founded, League.Confederation, League.Number_of_teams, League.Relegation_to, \
                              League.Current_champions, League.Most_championships, League.TV_partners, League.Domestic_cup, \
                              League.International_cup, League.Infomation_source, League.Status, label('LeagueId',League.id)  \
                              ).join(League, Country.id == League.country_id).filter(League.id == int(league))
    
    df = pd.DataFrame()
    for row in result:
        data = {'LeagueId':'L' + str(row.LeagueId), 'Country': row.Country, 'Name': row.name, 'Founded': str(row.Founded), 'Confederation': row.Confederation, \
                'Number of Teams': str(row.Number_of_teams), 'Relegation To': row.Relegation_to, 'Current Champions': row.Current_champions, \
                'Most Championships': row.Most_championships, 'TV Partners': row.TV_partners, 'Domestic Cup': row.Domestic_cup, \
                'International Cup': row.International_cup, 'Infomation Source': row.Infomation_source, 'Status': row.Status}
        df = df.append(data, ignore_index=True)
    
    return df

def get_league_teams(league):
    result1 = Match.query.with_entities(Match.league_id, Match.season, label('team_api_id',Match.home_team_api_id)).filter(Match.league_id == int(league))
    result2 = Match.query.with_entities(Match.league_id, Match.season, label('team_api_id',Match.away_team_api_id)).filter(Match.league_id == int(league))
    result = result1.union(result2)
    
    df = pd.DataFrame()
    for row in result:
        teams = db.session.query(Team).filter(Team.team_api_id == row.team_api_id).all()
        for team in teams:
            data = {'LeagueId':'L' + str(row.league_id), 'Season':row.season, 'Team Id': team.team_short_name, \
                    'Team Name': team.team_long_name, 'TeamApiId': str(row.team_api_id)
                    }
            df = df.append(data, ignore_index=True)
    if df.shape[0]>0:
        df = df.sort_values(by='Season', ascending=False)
    return df

def get_team_name(team):
    result = Team.query.with_entities(Team.team_long_name).filter(Team.team_api_id == team).first()
    teamName = ' '
    for row in result:
        teamName = row
    return(teamName)

def get_team_shortname(team):
    result = Team.query.with_entities(Team.team_short_name).filter(Team.team_api_id == team).first()
    teamName = ' '
    for row in result:
        teamName = row
    return(teamName)

def get_team_details(league, season, team):
    league = league.replace('L','')
    season = season.replace('-','/')

    
    result1 = Match.query.with_entities(label('team_api_id',Match.home_team_api_id), \
                                        label('player1',Match.home_player_1), \
                                        label('player2',Match.home_player_2), \
                                        label('player3',Match.home_player_3), \
                                        label('player4',Match.home_player_4), \
                                        label('player5',Match.home_player_5), \
                                        label('player6',Match.home_player_6), \
                                        label('player7',Match.home_player_7), \
                                        label('player8',Match.home_player_8), \
                                        label('player9',Match.home_player_9), \
                                        label('player10',Match.home_player_10), \
                                        label('player11',Match.home_player_11)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.home_team_api_id == int(team))
    
    result2 = Match.query.with_entities(label('team_api_id',Match.away_team_api_id), \
    									  label('player1',Match.away_player_1), \
    									  label('player2',Match.away_player_2), \
                                        label('player3',Match.away_player_3), \
                                        label('player4',Match.away_player_4), \
                                        label('player5',Match.away_player_5), \
                                        label('player6',Match.away_player_6), \
                                        label('player7',Match.away_player_7), \
                                        label('player8',Match.away_player_8), \
                                        label('player9',Match.away_player_9), \
                                        label('player10',Match.away_player_10), \
                                        label('player11',Match.away_player_11)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.away_team_api_id == int(team))
    
    result = result1.union(result2)
    
    df = pd.DataFrame()
    for row in result:
        data = {'TeamID': row.team_api_id, \
                'player1': row.player1, \
                'player2': row.player2, \
                'player3': row.player3, \
                'player4': row.player4, \
                'player5': row.player5, \
                'player6': row.player6, \
                'player7': row.player7, \
                'player8': row.player8, \
                'player9': row.player9, \
                'player10': row.player10, \
                'player11': row.player11
                }
        df = df.append(data, ignore_index=True)
    
    df = pd.melt(df, id_vars=['TeamID'], var_name='playerCol', value_name="playerId")
    df.drop('playerCol', axis=1, inplace=True)
    df = df.drop_duplicates()
    playerList = df['playerId'].tolist()

    players = Player.query.filter(Player.player_api_id.in_(playerList)).all()
    playerDetails = Player_Attributes.query.filter(Player_Attributes.player_api_id.in_(playerList)).all()
    
    #Get players
    playersDf = pd.DataFrame()
    for row in players:
        bday = pd.to_datetime(row.birthday)
        bday = str(bday.month) + '/' + str(bday.day) + '/' + str(bday.year)
        data = {'Name': row.player_name, 'Birth Day': bday, \
                'Height': ("%.2f" % row.height), 'Weight': ("%.2f" % row.weight), 'playerID': str(row.player_api_id)
                }
        playersDf = playersDf.append(data, ignore_index=True)

    if (playersDf.shape[0] > 0):
        cols = ['Name','Birth Day','Height','Weight', 'playerID']
        playersDf = playersDf[cols]
        
    #Get Player latest stats
    playerDetailsDf = pd.DataFrame()
    for row in playerDetails:
        lastStatsDt = pd.to_datetime(row.date)
        lsd = str(lastStatsDt.month) + '/' + str(lastStatsDt.day) + '/' + str(lastStatsDt.year)
        
        data = {'playerID': str(row.player_api_id), 'lastStatsDt': lastStatsDt, 'lsd': lsd, 'Overall Rating': row.overall_rating, 
                'Potential': row.potential, 'Preferred Foot': str(row.preferred_foot).title(),
                'Attacking Work Rate': str(row.attacking_work_rate).title(),
                'Defensive Work Rate': str(row.defensive_work_rate).title(),
                'Crossing': row.crossing, 'Finishing Rate': row.finishing, 'Heading Accuracy': row.heading_accuracy, 
                'Short Passing': row.short_passing, 'Volleys': row.volleys, 'Dribbling Rate': row.dribbling, 
                'Curve': row.curve, 'Free Kick Accuracy': row.free_kick_accuracy, 'Long Passing': row.long_passing, 
                'Ball Control': row.ball_control, 'Acceleration': row.acceleration, 'Sprint Speed': row.sprint_speed,
                'Agility': row.agility, 'Reactions': row.reactions, 'Balance': row.balance, 
                'Shot Power': row.shot_power, 'Jumping': row.jumping, 'Stamina': row.stamina, 
                'Strength': row.strength, 'Long Shots': row.long_shots, 'Aggression': row.aggression, 
                'Interception': row.interceptions, 'Vision': row.vision, 'Positioning': row.positioning,
                'Penalties': row.penalties, 'Marking': row.marking, 'Standing Tackle': row.standing_tackle, 
                'Sliding Tackle': row.sliding_tackle, 'Goalkeeping Driving': row.gk_diving, 
                'Goalkeeping Handling': row.gk_handling, 'Goalkeeping Kicking': row.gk_kicking, 
                'Goalkeeping Positioning': row.gk_positioning, 'Goalkeeping Reflexes': row.gk_reflexes
                }
        playerDetailsDf = playerDetailsDf.append(data, ignore_index=True)

 
    # groupby first two columns, then get the maximum value in the third column
    idx = playerDetailsDf.groupby(['playerID'])['lastStatsDt'].transform(max) == playerDetailsDf['lastStatsDt']
    
    # use the index to fetch correct rows in dataframe
    playerLatest = playerDetailsDf[idx]
    
    teamName = get_team_name(team)
    
    return playersDf, playerLatest, teamName


def get_player_details(player):
    playerDetails = Player_Attributes.query.filter(Player_Attributes.player_api_id == (int(player))).all()
    #Get Player latest stats
    playerDetailsDf = pd.DataFrame()
    for row in playerDetails:
        lastStatsDt = pd.to_datetime(row.date)
        lsd = str(lastStatsDt.month) + '/' + str(lastStatsDt.day) + '/' + str(lastStatsDt.year)
        
        data = {'playerID': str(row.player_api_id), 'lastStatsDt': lastStatsDt, 'lsd': lsd, 'Overall Rating': row.overall_rating, 
                'Potential': row.potential, 'Preferred Foot': str(row.preferred_foot).title(),
                'Attacking Work Rate': str(row.attacking_work_rate).title(),
                'Defensive Work Rate': str(row.defensive_work_rate).title(),
                'Crossing': row.crossing, 'Finishing Rate': row.finishing, 'Heading Accuracy': row.heading_accuracy, 
                'Short Passing': row.short_passing, 'Volleys': row.volleys, 'Dribbling Rate': row.dribbling, 
                'Curve': row.curve, 'Free Kick Accuracy': row.free_kick_accuracy, 'Long Passing': row.long_passing, 
                'Ball Control': row.ball_control, 'Acceleration': row.acceleration, 'Sprint Speed': row.sprint_speed,
                'Agility': row.agility, 'Reactions': row.reactions, 'Balance': row.balance, 
                'Shot Power': row.shot_power, 'Jumping': row.jumping, 'Stamina': row.stamina, 
                'Strength': row.strength, 'Long Shots': row.long_shots, 'Aggression': row.aggression, 
                'Interception': row.interceptions, 'Vision': row.vision, 'Positioning': row.positioning,
                'Penalties': row.penalties, 'Marking': row.marking, 'Standing Tackle': row.standing_tackle, 
                'Sliding Tackle': row.sliding_tackle, 'Goalkeeping Driving': row.gk_diving, 
                'Goalkeeping Handling': row.gk_handling, 'Goalkeeping Kicking': row.gk_kicking, 
                'Goalkeeping Positioning': row.gk_positioning, 'Goalkeeping Reflexes': row.gk_reflexes
                }
        playerDetailsDf = playerDetailsDf.append(data, ignore_index=True)
    return playerDetailsDf

def get_team_winlose(league, season, team):
    league = league.replace('L','')
    season = season.replace('-','/')
    
    result1 = Match.query.with_entities(Match.league_id, Match.goal, Match.date,
                                        Match.season, label('team_api_id',Match.home_team_api_id), label('opponent',Match.away_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.home_team_api_id == int(team))
    
    result2 = Match.query.with_entities(Match.league_id, Match.goal, Match.date,
                                        Match.season, label('team_api_id',Match.away_team_api_id), label('opponent',Match.home_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.away_team_api_id == int(team))
    result = result1.union(result2)
    
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    for row in result:
        g = 0
        og = 0
        goalText = row.goal
        if not goalText == None:
            soup = BeautifulSoup(goalText,'xml')
            goals = soup.find_all('goals')
            teamId = soup.find_all('team')
            for i in range(0, len(goals)):
                if int(teamId[i].get_text()) == int(team):
                    g = g + int(goals[i].get_text())
                else:
                    og = og + int(goals[i].get_text())
        outcome = 'D'
        if g > og:
            outcome = 'W'
        if (g < og):
            outcome = 'L'
        
        data = {'Opponent': get_team_name(row.opponent),
                'OpponentId': get_team_shortname(row.opponent),
                'Outcome': outcome,
                'Goals': str(g) + ' - ' + str(og),
                'date1': pd.to_datetime(row.date)
                }
        data1 = {'Opponent': get_team_shortname(row.opponent),
                'Outcome': outcome,
                'GoalsMade': str(g),
                'GoalsGiven': str(og),
                'Diff': (g - og),
                'date1': pd.to_datetime(row.date)
                }
        
        df = df.append(data, ignore_index=True)
        df1 = df1.append(data1, ignore_index=True)
        
    if (df.shape[0] > 0):
        df = df.sort_values(by='date1', ascending=True)
        df1 = df1.sort_values(by='date1', ascending=True)
        df['Date'] = df['date1'] .apply(lambda x: datetime.datetime.strftime(x, '%m/%d/%Y'))
        df = df.set_index('date1')
        df1 = df1.set_index('date1')
        cols = ['Date','Opponent','OpponentId','Outcome','Goals']
        df = df[cols]
    return df, df1

def get_team_shoton(league, season, team):
    league = league.replace('L','')
    season = season.replace('-','/')
    
    result1 = Match.query.with_entities(Match.league_id, Match.shoton, Match.date,
                                        Match.season, label('team_api_id',Match.home_team_api_id), label('opponent',Match.away_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.home_team_api_id == int(team))
    
    result2 = Match.query.with_entities(Match.league_id, Match.shoton, Match.date,
                                        Match.season, label('team_api_id',Match.away_team_api_id), label('opponent',Match.home_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.away_team_api_id == int(team))
    result = result1.union(result2)
    
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    for row in result:
        s = 0
        os = 0
        s1 = 0
        os1 = 0
        shotonText = row.shoton
        if not shotonText == None:
            soup = BeautifulSoup(shotonText,'xml')
            shot = soup.find_all('type')
            teamId = soup.find_all('team')
            for i in range(0, len(shot)):
                if shot[i].get_text() == 'shoton':
                    if len(teamId) > i:
                        if int(teamId[i].get_text()) == int(team):
                            s = s + 1
                        else:
                            os = os + 1
        totalShots = s + os
        if totalShots > 0:
            s1 = (s/totalShots) * 100
            os1 = (os/totalShots) * 100
        
        data = {'Opponent': get_team_name(row.opponent),
                'OpponentId': get_team_shortname(row.opponent),
                'Shot On Goal Ratio': '(' + ("%d" % s) + ')' +  ("%.2f" % s1) + ' : ' + ("%.2f" % os1) + '(' + ("%d" % os) + ')' ,
                'date1': pd.to_datetime(row.date)
                }
        data1 = {'Opponent': get_team_shortname(row.opponent),
                 'SOGT': s,
                 'SOGO': os,
                 'date1': pd.to_datetime(row.date)
                }
        
        df = df.append(data, ignore_index=True)
        df1 = df1.append(data1, ignore_index=True)

    if (df.shape[0] > 0):
        df = df.sort_values(by='date1', ascending=True)
        df1 = df1.sort_values(by='date1', ascending=True)
        df['Date'] = df['date1'] .apply(lambda x: datetime.datetime.strftime(x, '%m/%d/%Y'))
        df = df.set_index('date1')
        df1 = df1.set_index('date1')
        cols = ['Date','Opponent','OpponentId','Shot On Goal Ratio']
        df = df[cols]
    return df, df1

def get_team_shotoff(league, season, team):
    league = league.replace('L','')
    season = season.replace('-','/')
    
    result1 = Match.query.with_entities(Match.league_id, Match.shotoff, Match.date,
                                        Match.season, label('team_api_id',Match.home_team_api_id), label('opponent',Match.away_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.home_team_api_id == int(team))
    
    result2 = Match.query.with_entities(Match.league_id, Match.shotoff, Match.date,
                                        Match.season, label('team_api_id',Match.away_team_api_id), label('opponent',Match.home_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.away_team_api_id == int(team))
    result = result1.union(result2)
    
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    for row in result:
        s = 0
        os = 0
        s1 = 0
        os1 = 0
        shotoffText = row.shotoff
        if not shotoffText == None:
            soup = BeautifulSoup(shotoffText,'xml')
            shot = soup.find_all('type')
            teamId = soup.find_all('team')
            for i in range(0, len(shot)):
                if shot[i].get_text() == 'shotoff':
                    if len(teamId) > i:
                        if int(teamId[i].get_text()) == int(team):
                            s = s + 1
                        else:
                            os = os + 1
        totalShots = s + os
        if totalShots > 0:
            s1 = (s/totalShots) * 100
            os1 = (os/totalShots) * 100
        
        data = {'Opponent': get_team_name(row.opponent),
                'OpponentId': get_team_shortname(row.opponent),
                'Shot On Goal Ratio': '(' + ("%d" % s) + ')' +  ("%.2f" % s1) + ' : ' + ("%.2f" % os1) + '(' + ("%d" % os) + ')' ,
                'date1': pd.to_datetime(row.date)
                }
        data1 = {'Opponent': get_team_shortname(row.opponent),
                 'SOGT': s,
                 'SOGO': os,
                 'date1': pd.to_datetime(row.date)
                }
        
        df = df.append(data, ignore_index=True)
        df1 = df1.append(data1, ignore_index=True)

    if (df.shape[0] > 0):
        df = df.sort_values(by='date1', ascending=True)
        df1 = df1.sort_values(by='date1', ascending=True)
        df['Date'] = df['date1'] .apply(lambda x: datetime.datetime.strftime(x, '%m/%d/%Y'))
        df = df.set_index('date1')
        df1 = df1.set_index('date1')
        cols = ['Date','Opponent','OpponentId','Shot On Goal Ratio']
        df = df[cols]
    return df, df1


def get_team_foulcommits(league, season, team):
    league = league.replace('L','')
    season = season.replace('-','/')
    
    result1 = Match.query.with_entities(Match.league_id, Match.foulcommit, Match.date,
                                        Match.season, label('team_api_id',Match.home_team_api_id), label('opponent',Match.away_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.home_team_api_id == int(team))
    
    result2 = Match.query.with_entities(Match.league_id, Match.foulcommit, Match.date,
                                        Match.season, label('team_api_id',Match.away_team_api_id), label('opponent',Match.home_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.away_team_api_id == int(team))
    result = result1.union(result2)
    
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    for row in result:
        s = 0
        os = 0
        foulcommitText = row.foulcommit
        if not foulcommitText == None:
            soup = BeautifulSoup(foulcommitText,'xml')
            foul = soup.find_all('type')
            teamId = soup.find_all('team')
            for i in range(0, len(foul)):
                if foul[i].get_text() == 'foulcommit':
                    if len(teamId) > i:
                        if int(teamId[i].get_text()) == int(team):
                            s = s + 1
                        else:
                            os = os + 1
        totalFouls = s + os
        if totalFouls > 0:
            s = (s/totalFouls) * 100
            os = (os/totalFouls) * 100
        
        data = {'Opponent': get_team_name(row.opponent),
                'OpponentId': get_team_shortname(row.opponent),
                'Foul Commit Ratio': ("%.2f" % s)+ ' : ' + ("%.2f" % os),
                 'date1': pd.to_datetime(row.date)
                }
        data1 = {'Opponent': get_team_shortname(row.opponent),
                 'FoulT': s,
                 'FoulO': os,
                 'date1': pd.to_datetime(row.date)
                }
        
        df = df.append(data, ignore_index=True)
        df1 = df1.append(data1, ignore_index=True)
    
    if (df.shape[0] > 0):
        df = df.sort_values(by='date1', ascending=True)
        df1 = df1.sort_values(by='date1', ascending=True)
        df['Date'] = df['date1'] .apply(lambda x: datetime.datetime.strftime(x, '%m/%d/%Y'))
        df = df.set_index('date1')
        df1 = df1.set_index('date1')
        cols = ['Date','Opponent','OpponentId','Foul Commit Ratio']
        df = df[cols]
    return df, df1


def get_correlation(league, season):
    league = league.replace('L','')
    season = season.replace('-','/')
    
    result1 = Match.query.with_entities(label('team_api_id',Match.away_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season)
    
    result2 = Match.query.with_entities(label('team_api_id',Match.home_team_api_id)
                                        ).filter(Match.league_id == int(league)).filter(Match.season == season)
    teams = result = result1.union(result2)

    
    result = Team_Attributes.query.with_entities(Team_Attributes.buildUpPlaySpeed, \
                                                Team_Attributes.buildUpPlayDribbling, \
                                                Team_Attributes.buildUpPlayPassing, \
                                                Team_Attributes.chanceCreationPassing, \
                                                Team_Attributes.chanceCreationCrossing, \
                                                Team_Attributes.chanceCreationShooting, \
                                                Team_Attributes.defencePressure, \
                                                Team_Attributes.defenceAggression, \
                                                Team_Attributes.defenceTeamWidth, \
                                                Team_Attributes.date, Team_Attributes.team_api_id
                                                ).filter(Team_Attributes.team_api_id.in_(teams)).all()
    
    df = pd.DataFrame()
    for row in result:
        lastStatsDt = pd.to_datetime(row.date)
        lsd = str(lastStatsDt.month) + '/' + str(lastStatsDt.day) + '/' + str(lastStatsDt.year)
        
        data = {'Play Speed': row.buildUpPlaySpeed,
                'Dribbling': row.buildUpPlayDribbling,
                'Play Passing': row.buildUpPlayPassing,
                'Creative Passing': row.chanceCreationPassing,
                'Creative Crossing': row.chanceCreationCrossing,
                'Creative Shooting': row.chanceCreationShooting,
                'Defence Pressure': row.defencePressure,
                'Defence Aggression': row.defenceAggression,
                'Defence Team Width': row.defenceTeamWidth,
                'lastStatsDt': lastStatsDt,
                'Lastest Stats Date': lsd,
                'TeamId': row.team_api_id
                }
        df = df.append(data, ignore_index=True)
    
    idx = df.groupby(['TeamId'])['lastStatsDt'].transform(max) == df['lastStatsDt']
    
    # use the index to fetch correct rows in dataframe
    teamLatestStats = df[idx]
    teamLatestStats.fillna(0)
    
    df = pd.DataFrame()
    for team in teams:
        teamapiId = team.team_api_id
        w = 0
        l = 0
        d = 0
        f = 0
        s = 0
        result1 = Match.query.with_entities(Match.league_id, Match.goal, Match.foulcommit, Match.shoton, Match.date,
                                            Match.season, label('team_api_id',Match.home_team_api_id), label('opponent',Match.away_team_api_id)
                                            ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.home_team_api_id == int(teamapiId))
        
        result2 = Match.query.with_entities(Match.league_id, Match.goal, Match.foulcommit, Match.shoton, Match.date,
                                            Match.season, label('team_api_id',Match.away_team_api_id), label('opponent',Match.home_team_api_id)
                                            ).filter(Match.league_id == int(league)).filter(Match.season == season).filter(Match.away_team_api_id == int(teamapiId))
        result = result1.union(result2)
    
        for row in result:
            g = 0
            og = 0
            goalText = row.goal
            if not goalText == None:
                soup = BeautifulSoup(goalText,'xml')
                goals = soup.find_all('goals')
                teamId = soup.find_all('team')
                for i in range(0, len(goals)):
                    if len(teamId) > i:
                        if int(teamId[i].get_text()) == int(teamapiId):
                            g = g + int(goals[i].get_text())
                        else:
                            og = og + int(goals[i].get_text())
                        
            foulcommit = row.foulcommit
            if not foulcommit == None:
                soup = BeautifulSoup(foulcommit,'xml')
                foul = soup.find_all('foulcommit')
                teamId = soup.find_all('team')
                for i in range(0, len(foul)):
                    if len(teamId) > i:
                        if int(teamId[i].get_text()) == int(teamapiId):
                            f = f + 1
                        
            shoton = row.shoton
            if not shoton == None:
                soup = BeautifulSoup(shoton,'xml')
                shot = soup.find_all('shoton')
                teamId = soup.find_all('team')
                for i in range(0, len(shot)):
                    if len(teamId) > i:
                        if int(teamId[i].get_text()) == int(teamapiId):
                            s = s + 1

            outcome = 'D'
            if g > og:
                outcome = 'W'
            if (g < og):
                outcome = 'L'
    
            w = w + 1 if outcome == 'W' else w
            l = l + 1 if outcome == 'L' else l
            d = d + 1 if outcome == 'D' else d
        
        data = {'TeamId': teamapiId, 'Wins': w, 'Loses': l, 'Draws': d, 'Foul Commit': f, 'Shot On Goal': s}
        df = df.append(data, ignore_index=True)
        
    df = pd.merge(df, teamLatestStats, on='TeamId', how='inner')
    
    cols = ['Play Speed','Dribbling','Play Passing','Creative Passing','Creative Crossing','Creative Shooting', \
            'Defence Pressure','Defence Aggression','Defence Team Width', 'Wins', 'Loses', 'Draws', 'Foul Commit', 'Shot On Goal']
    df = df[cols]
    
    outcome = ['Wins', 'Draws', 'Loses']
    df = df.corr().filter(outcome).drop(outcome)
    return df
                


def get_teamStats(league, season, team):
    league = league.replace('L','')
    season = season.replace('-','/')
    
    result = db.session.query(Team_Attributes).filter(Team_Attributes.team_api_id == int(team)).all()
    
    df = pd.DataFrame()
    df1 = pd.DataFrame()    
    for row in result:
        lastStatsDt = pd.to_datetime(row.date)
        lsd = str(lastStatsDt.month) + '/' + str(lastStatsDt.day) + '/' + str(lastStatsDt.year)
        
        data = {'Play Speed': row.buildUpPlaySpeed,
                'Dribbling': row.buildUpPlayDribbling,
                'Play Passing': row.buildUpPlayPassing,
                'Creative Passing': row.chanceCreationPassing,
                'Creative Crossing': row.chanceCreationCrossing,
                'Creative Shooting': row.chanceCreationShooting,
                'Defence Pressure': row.defencePressure,
                'Defence Aggression': row.defenceAggression,
                'Defence Team Width': row.defenceTeamWidth,
                'lastStatsDt': lastStatsDt,
                'Lastest Stats Date': lsd,
                'TeamId': row.team_api_id
                }
        data1 = {'Play Speed': str(row.buildUpPlaySpeedClass).title(),
                'Dribbling': str(row.buildUpPlayDribblingClass).title(),
                'Play Passing': str(row.buildUpPlayPassingClass).title(),
                'Creative Passing': str(row.chanceCreationPassingClass).title(),
                'Creative Crossing': str(row.chanceCreationCrossingClass).title(),
                'Creative Shooting': str(row.chanceCreationShootingClass).title(),
                'Defence Pressure': str(row.defencePressureClass).title(),
                'Defence Aggression': str(row.defenceAggressionClass).title(),
                'Defence Team Width': str(row.defenceTeamWidthClass).title(),                                          
                'Defence Line': str(row.defenceDefenderLineClass).title(),
                'lastStatsDt': lastStatsDt,
                'Lastest Stats Date': lsd,
                'TeamId': row.team_api_id
                }
        
        
        df = df.append(data, ignore_index=True)
        df1 = df1.append(data1, ignore_index=True)
    
    print(df)
    print(df1)
    idx = df.groupby(['TeamId'])['lastStatsDt'].transform(max) == df['lastStatsDt']
    df = df[idx]
    df1 = df1[idx]
    df.fillna('NA')
    df.fillna('NA')
    cols = ['Play Speed','Dribbling','Play Passing','Creative Passing','Creative Crossing','Creative Shooting', \
            'Defence Pressure','Defence Aggression','Defence Team Width', 'TeamId']
    df = df[cols]
    
    cols = ['Play Speed','Dribbling','Play Passing','Creative Passing','Creative Crossing','Creative Shooting', \
            'Defence Pressure','Defence Aggression','Defence Team Width', 'Defence Line', 'TeamId']
    df1 = df1[cols]
    
    df = pd.melt(df, id_vars=['TeamId'], var_name='Attribute', value_name="Rating")
    df1 = pd.melt(df1, id_vars=['TeamId'], var_name='Attribute', value_name="Class")
    
    cols = ['Attribute','Rating']
    df = df[cols]
    
    cols = ['Attribute','Class']
    df1 = df1[cols]
    
    print(df)
    print(df1)
    
    return df, df1

