# %%
import pandas as pd
import numpy as np
from sportsreference.ncaab.teams import Teams
import difflib
import os


class MakeData:
    def __init__(self, years=range(2015, 2022)):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.years=years
        try:
            self.season = pd.read_csv(os.path(self.path, "data", "season.csv"))
            self.tournament = pd.read_csv(os.path.join(self.path, 'data', 'tournament.csv'))
            self.march_madness_history = pd.read_csv(os.path.join(self.path, 'data', 'march_madness_history.csv'))
        except:
            print("No data found. Run add_data()")
    
    def add_data(self):
        self.season = self.get_season_data(self.years)
        self.tournament = self.get_tournament_data()
        self.march_madness_history = self.make_analysis_data()
        #self.analysis_data = self.combine_data()

    @staticmethod
    def get_season_data(years):
        # Get historical season data
        df = pd.DataFrame()
        for year in years:
            for team in Teams(year):
                try:
                    df = pd.concat([df,team.dataframe.assign(Year = year) ])
                except:
                    print(team.name,year, "Not in Available")

        return df
    
    @staticmethod
    def get_tournament_data():
        url = r'''https://apps.washingtonpost.com/sports/search/?pri_school_id=&pri_conference=&pri_coach=&pri_seed_from=1&pri_seed_to=16&pri_power_conference=&pri_bid_type=&opp_school_id=&opp_conference=&opp_coach=&opp_seed_from=1&opp_seed_to=16&opp_power_conference=&opp_bid_type=&game_type=7&from=1985&to=2020&submit='''     
        df = pd.read_html(url)[0] # should be first table
        df.columns = [col.replace('.', "_") for col in df.columns]
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].apply(lambda x: x[0:int(len(x)/2)].strip())

        df['Favorite'] = np.where(
            df['Seed_1'] == df['Seed'],
                "EQUAL",
                np.where(
                    df['Seed_1'] > df['Seed'],
                    "TEAM_2",
                    "TEAM_1"))
        df['Seed_diff'] =  df['Seed_1'] - df['Seed']
        df['Spread'] = df['Score'] - df['Score_1']
        df['Winner'] = np.where(df['Score'] >df['Score_1'] ,"TEAM_1","TEAM_2")
        df['Upset'] = df.Winner != df.Favorite
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype('category')

        return df


    

    def add_season_features(self, data, team_1_col="Team", team_2_col="Team_1"):
        if data is None: data = self.tournament
        df  = data.copy()
        team_names = [n.strip() for n in pd.concat([df[team_1_col], df[team_2_col]], axis=0,ignore_index=True).sort_values().unique()]
        
                
        self.season['key_name'] = self.season['name'].apply(lambda x: self.closest_name(x,team_names))
        cols = self.season.columns
        #cols = ['Year','key_name','away_losses', 'away_wins', 'conference','win_percentage', 'true_shooting_percentage', 'offensive_rating', 'pace', 'strength_of_schedule', 'opp_offensive_rating' ]


        #meta = data[['Winner', 'Spread', 'Favorite', 'Upset', 'Year', 'Round']]
        team_1 = df[['Year',team_1_col]].merge(self.season[cols], how='left', left_on=['Year', team_1_col], right_on=['Year','key_name'] ,suffixes=("", "TEAM_1"))
        team_2 = df[['Year',team_2_col]].merge(self.season[cols], how='left', left_on=['Year', team_2_col], right_on=['Year','key_name'] ,suffixes=("", "TEAM_2"))
        #df =pd.DataFrame()
        df[team_1_col +"_conference"] = team_1['conference']
        df[team_2_col + "_conference"] = team_2['conference']
        for col in team_1.select_dtypes(include=np.number).columns:
            col_name = col + "_diff"
            df[col_name] = team_1[col] - team_2[col]

        return df
    
    def make_analysis_data(self):
        return self.add_season_features(self.tournament, "Team", "Team_1")

    def save_data(self, path=None, overwrite=True):
        if path is None:
            import os
            path = os.path.dirname(os.path.abspath(__file__))
        atr = dir(self)
        for atr in dir(self):
            obj = getattr(self, atr)
            if isinstance(obj, pd.DataFrame):
                fName = os.path.join(path, "data", atr + ".csv")
                if overwrite | (not os.path.exists(fName)) :
                    obj.to_csv(fName,index=False )
                else:
                    print(fName, "already exists and did not overwrite")
        

        #for self.season.to_csv('')

    def get_team_names(self, df=None, team_1_col="Team", team_2_col="Team_1"):
        if df is None: df = self.tournament.copy()

        team_names = [n.strip() for n in pd.concat([df[team_1_col], df[team_2_col]], axis=0,ignore_index=True).sort_values().unique()]
    
    @staticmethod
    def closest_name(x, team_names):
            matches = difflib.get_close_matches(x, team_names)
            if len(matches) >0: 
                return matches[0]
            else:
                return None

#%%
if __name__ =="__main__":
    import os
    print(__file__)
    print(__path__)
    loc = os.path.join(__path__, "data")
    data = MakeData()
    data.add_data()
    data.add_features()
    data.save_data(overwrite=False)
    #data.season.to_csv(os.path.join(loc, 'season.csv') )
    #data.tournament.to_csv(os.path.join('./data/tournament.csv')