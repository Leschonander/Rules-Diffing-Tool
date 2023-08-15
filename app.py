import pandas as pd
import openai
import os
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
RulesReformSheet = pd.read_csv("Rules_combined_df_master.csv", lineterminator='\n') # pd.read_csv("Rules Reform Scraping Freshsheet - Sheet1 - Combined.csv")


### Look up variables
Rule = RulesReformSheet["Rule"].unique()

Titles = RulesReformSheet["Title"].unique()
Titles = [str(t).strip() for t in Titles]
Titles = [t.replace("\n,", " ") for t in Titles]

RulesReformSheet["Congress"] = RulesReformSheet["Congress"].astype(str)
RulesReformSheet["Congress"] = RulesReformSheet["Congress"].apply(lambda x: x.strip())
Congress = RulesReformSheet["Congress"].unique()
Congress = [str(c).strip() for c in Congress]
Congress = [c for c in Congress if c != 'nan']
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
    RulesReformSheet = pd.read_csv("Rules_combined_df_master.csv", lineterminator='\n')

    RulesReformSheet["Rule"] = RulesReformSheet["Rule"].fillna(method="ffill")
    RulesReformSheet["Title"] = RulesReformSheet["Title"].str.strip() 

    RulesReformSheet = RulesReformSheet.query("Title == @title")
    RulesReformSheet = RulesReformSheet.query(f"Congress == @congress")


    result = {"Result": list(RulesReformSheet["Text"])[0]} 
    
    return jsonify(result)

@app.route('/api/openai')
def openapi_api_route():
    old_rule = request.args.get('rule_1')
    new_rule = request.args.get('rule_2')

    congress_1 = request.args.get('congress_1')
    congress_2 = request.args.get('congress_2')

    rule_title = request.args.get('rule_title')

    '''
    print(congress_1)
    print(old_rule)
    print("---")
    print(congress_2)
    print(new_rule)
    print("---")
    print(rule_title)
    '''

    completion = openai.ChatCompletion.create(
        model = "gpt-4",
        temperature = 0.8,
        max_tokens = 2000,
        messages = [
        {"role": "system", "content": f"Explain the differences between the two following sets of rules for the {rule_title}. The first is from the {congress_1} congress , the second is from the {congress_2} Congress. Do not note changes in formatting. If the rules are the same, just note that they are unchanged."},
        {"role": "system", "content": old_rule},
        {"role": "system", "content": new_rule},
        ]
    )

    result = {"Result": completion.choices[0].message["content"]} 

    return jsonify(result) 

if __name__ == '__main__':
    app.run(host="localhost", port=3000, debug=True)