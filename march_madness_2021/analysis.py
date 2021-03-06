#%%
import pycost as ct
import pandas as pd
import numpy as np
import hvplot.pandas

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV, LinearRegression, LassoCV, RidgeCV
from sklearn import metrics

# %%
teams = pd.read_csv('data/season.csv')
tourny = pd.read_csv('data/tournament.csv')

#%%
df = pd.read_csv("data/march_madness_history.csv")
df['Winner'] =np.where(df['Winner'] =="TEAM_1", 1,0)
df.head()
# %%
# Build models
meta_data = dict(
    title="NCAA March Madness 2021",
    description="Very simple Estimate",
    analyst = "Kevin Joy",
    tags=["NCAA", "Basketball", "March Madness"]
)

model = ct.Models(
    df = df[~df.isnull()],
    formulas = ['Winner~Round+Favorite', 'Winner~Round + Favorite + Seed_diff','Winner~Round + Favorite * Seed_diff + np.square(Seed_diff)' ],
    models = [LogisticRegression(), LogisticRegressionCV(cv=5), RandomForestClassifier(), AdaBoostClassifier()],
    test_split=.10,
    **meta_data,
    Type ="classifier"
    )

model_reg = ct.Models(
    df = df,
    formulas = ['Spread~Round+Favorite', 'Spread~Round + Favorite + Seed_diff','Spread~Round + Favorite * Seed_diff + np.square(Seed_diff)' ],
    models = [LinearRegression(), LassoCV(), RidgeCV(), RandomForestRegressor()],
    test_split=.10,
    **meta_data,
   Type = 'regression'
    )


#%%
model.db.head()

# %%
model_reg.db.head()
# %%
# Fit Model and store results
results = pd.DataFrame()
for index,row in model.db.iterrows():
    row.Model.fit()
    tmp_df = pd.DataFrame(
        dict(
            Model = [row.ModelType],
            Formula = [row.Formula],
            Test_Score = [metrics.accuracy_score(row.Model.y_test,row.Model.predict(row.Model.X_test))],
            Train_Score = [metrics.accuracy_score(row.Model.y_train,row.Model.predict(row.Model.X_train))],
            All_Score = [metrics.accuracy_score(row.Model.y,row.Model.predict(row.Model.X))]
        )
    )
    results = pd.concat([results, tmp_df], ignore_index=True)

results.sort_values('Test_Score', ascending=False)
    
# %%
#model.db.Model[10].model_show_transformation()

# %%
from pycost import process
big_formula = 'Winner~`- Team - Team_1 - Score - Score_1 - Upset'
df_2015 = process.MakeFormula("` -1 - Team - Team_1 - Score - Score_1 - Upset - Spread", handle_na=True).fit_transform(df.query('Year >=2015'))
big_model = ct.Models(df_2015, 'Winner ~ ` ', models=[LogisticRegression(), LogisticRegressionCV(cv=5), RandomForestClassifier(), AdaBoostClassifier()], test_split=.5)
big_model.fit()
# %%

for index,row in big_model.db.iterrows():
    row.Model.fit()
    tmp_df = pd.DataFrame(
        dict(
            Model = [row.ModelType],
            Formula = [row.Formula],
            Test_Score = [metrics.accuracy_score(row.Model.y_test,row.Model.predict(row.Model.X_test))],
            Train_Score = [metrics.accuracy_score(row.Model.y_train,row.Model.predict(row.Model.X_train))],
            All_Score = [metrics.accuracy_score(row.Model.y,row.Model.predict(row.Model.X))]
        )
    )
    results = pd.concat([results, tmp_df], ignore_index=True)

results.sort_values('Test_Score', ascending=False)
# %%
