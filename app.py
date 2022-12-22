import pandas as pd
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

RulesReformSheet = pd.read_csv("Rules Reform Scraping Freshsheet - Sheet1 - Combined.csv")


### Look up variables
Rule = RulesReformSheet["Rule"].unique()

Titles = RulesReformSheet["Title"].unique()
Titles = [str(t).strip() for t in Titles]
Titles = [t.replace("\n,", " ") for t in Titles]

RulesReformSheet["Congress"] = RulesReformSheet["Congress"].apply(lambda x: x.strip())
Congress = RulesReformSheet["Congress"].unique()
Congress = [str(c).strip() for c in Congress]
Congress = [c for c in Congress if c != 'nan']
Congress = [c for c in Congress if c != '105th']
Congress = [c for c in Congress if "https" not in c]



@app.route('/')
def hello_world():

    return render_template('index.html', Congress_List = Congress, Titles_List = Titles)

@app.route("/about")
def about():

    return render_template("about.html")

@app.route('/api')
def api_route():
    title = request.args.get('title')
    congress = request.args.get('congress')
    RulesReformSheet = pd.read_csv("Rules Reform Scraping Freshsheet - Sheet1 - Combined.csv")

    RulesReformSheet["Rule"] = RulesReformSheet["Rule"].fillna(method="ffill")
    RulesReformSheet["Title"] = RulesReformSheet["Title"].str.strip() 

    RulesReformSheet = RulesReformSheet.query("Title == @title")
    RulesReformSheet = RulesReformSheet.query(f"Congress == @congress")

    result = {"Result": list(RulesReformSheet["Text"])[0]} 
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="localhost", port=3000, debug=True)