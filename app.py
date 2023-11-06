import pandas as pd
import openai
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request, render_template

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
RulesReformSheet = pd.read_csv("RulesReformMasterCleaned - TitleCleaned.csv", lineterminator='\n') # pd.read_csv("Rules Reform Scraping Freshsheet - Sheet1 - Combined.csv")


### Look up variables
Rule = RulesReformSheet["Rule"].unique()

Titles = RulesReformSheet["Title"].unique()
Titles = [str(t).strip() for t in Titles]
Titles = [t.replace("\n,", " ") for t in Titles]

Congress = ['118th', '117th', '116th', '115th', '114th', '113th', '112th', '111th', '110th', '109th', '108th', '107th', '106th', '105th', '104th', '103rd', '102nd', '101st', '100th', '99th', '98th', '97th', '96th', '95th', '94th', '93rd', '92nd', '91st', '90th', '89th', '88th', '87th', '86th', '85th', '84th', '83rd', '82nd', '81st', '80th', '79th', '78th']

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
    RulesReformSheet = pd.read_csv("RulesReformMasterCleaned - TitleCleaned.csv", lineterminator='\n')

    RulesReformSheet["Rule"] = RulesReformSheet["Rule"].fillna(method="ffill")
    RulesReformSheet["Title"] = RulesReformSheet["Title"].str.strip() 

    RulesReformSheet = RulesReformSheet.query("Title == @title")
    RulesReformSheet = RulesReformSheet.query(f"Congress == @congress")


    result = {"Result": list(RulesReformSheet["Text"])[0]} 
    
    return jsonify(result)

@app.route('/api/openai', methods = ['POST', 'GET'])
def openapi_api_route():

    data = request.json

    old_rule = data.get("old_rule")
    new_rule = data.get("new_rule")

    congress_1 = data.get("congress_1")
    congress_2 = data.get("congress_2")

    rule_title = data.get("rule_title")

    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-16k-0613",
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

@app.route('/api/generate_lists', methods = ['POST', 'GET'])
def list_generation_route():
    congress = request.args.get('congress')

    RulesReformSheet = pd.read_csv("RulesReformMasterCleaned - TitleCleaned.csv", lineterminator='\n')
    RulesReformSheet = RulesReformSheet.query(f"Congress == @congress")

    nested_json_full = {}
    nested_json_short = {}

    for index, row in RulesReformSheet.iterrows():
        rule = row["Rule"]
        title = row['Title']

        if rule not in nested_json_full:
            nested_json_full[rule] = []
        
        if rule not in nested_json_short:
            nested_json_short[rule] = []
        
        nested_json_full[rule].append(title)

        if "Full Rule" in title:
            nested_json_short[rule].append(title)

    result = {
        "short_rules": nested_json_short,
        "long_rules": nested_json_full
    }

    return jsonify(result) 

if __name__ == '__main__':
    app.run(host="localhost", port=3000, debug=True)