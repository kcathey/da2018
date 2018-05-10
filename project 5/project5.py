from appJar import gui
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.ticker as ticker
from pathlib import Path
import pandas as pd
import seaborn as sns; sns.set() # for plot styling
from sklearn import tree, linear_model, svm
from sklearn.preprocessing import LabelEncoder
from sklearn.externals import joblib

all_columns = ['Channel', 'Platform', 'GameType', 'ReserveType','ReleaseYear', 'ReleaseMonth',
         'RelativeWeek', 'Version', 'FinalPrice']

label_cols = ['Channel', 'Platform', 'GameType', 'ReserveType','ReleaseYear', 'ReleaseMonth']
encoders = {}

columns = [['Channel'],['ReserveType'],['Platform'],['Version','Series Version'],
           ['ReleaseYear','Release Year'],['ReleaseMonth','Release Month'],['RelativeWeek','Relative Week'],
           ['FinalPrice','Final Price'],['GameType','Game Type']]

def train_encoders(df):
    for c in label_cols:
        encoders[c] = LabelEncoder().fit(df[c])

def load_data():
    df = pd.read_csv("fixed.csv")

    df['ReleaseMonth'] = df['ReleaseMonth'].astype('str')
    df['ReleaseYear'] = df['ReleaseYear'].astype('str')
    df['RelativeWeek'] = df['RelativeWeek'].astype('int')
    df['Version'] = df['Version'].astype('int')
    df['ReservesLevel'] = df['ReservesLevel'].astype('int')

    train_encoders(df)
    y = df['ReservesLevel']
    X = pd.DataFrame(columns=all_columns)

    for col in X.columns:
        if col in label_cols:
            X[col] = encoders[col].transform(df[col])
        else:
            X[col] = df[col]
        X[col].astype(df[col].dtype)

    return df, X, y

data, X, y = load_data()

clf = None


clf = tree.DecisionTreeRegressor()
# clf = linear_model.ARDRegression()
if Path('model.pickle').exists():
    model = clf = joblib.load('model.pickle')
else:
    model = clf.fit(X,y)
    joblib.dump(model,'model.pickle')

print(model)

app = gui()
app.addLabel("title", "Predict Reserves")
for c in columns:
    if len(c) > 1:
        name = c[1]
    else:
        name = c[0]
    if name == 'Relative Week' or name == 'Final Price':
        app.addLabelNumericEntry(name)
    else:
        if name == 'Release Month':
            app.addLabelOptionBox(name, range(2,13))
        else:
            app.addLabelOptionBox(name, sorted(data[c[0]].unique()))
app.addLabel("Prediction", "Prediction Soon...")
fig = app.addPlot("p1",[],[])

def press(button):
    global model
    if button == "Cancel":
        app.stop()
    else:
        if button == "Retrain":
            model = clf.fit(X, y)
        size = int(app.getEntry("Relative Week"))+1
        smpl = pd.DataFrame(index = range(0,size), columns=all_columns)
        for c in columns:
            if c[0] == 'RelativeWeek':
                for i in range(0, size):
                    smpl['RelativeWeek'][i] = i
            else:
                if len(c) > 1:
                    name = c[1]
                else:
                    name = c[0]
                if name == 'Final Price':
                    smpl[c[0]] = app.getEntry(name)
                else:
                    smpl[c[0]] = app.getOptionBox(name)
                if c[0] in label_cols:
                    smpl[c[0]] = encoders[c[0]].transform(smpl[c[0]])

        ypnew = model.predict(smpl)
        smpl['ReservesLevel'] = ypnew
        print(smpl)
        app.setLabel("Prediction","Total Reserves: {:,.0f}".format(int(smpl.loc[smpl['RelativeWeek'] == 0]['ReservesLevel'].iloc[0])))
        app.updatePlot('p1',smpl['RelativeWeek'],smpl['ReservesLevel'])
        fig.set_xticks(range(0,size,2))
        fig.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        app.refreshPlot('p1')
app.addButtons(["Submit","Retrain", "Cancel"], press)

app.go()