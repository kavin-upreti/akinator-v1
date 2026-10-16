import random

import pandas as pd

CONTENDER_RATIO = 5 

def parse(str):
    pieces = str.split("$")
    str_options = pieces[1::2]
    for j in range(len(str_options)):
        str_options[j] = str_options[j].split("~")
    return str_options
    
def get_all_valid_questions(id):
    df = pd.read_csv("questions.csv", low_memory=False)
    rows = df[df["id"]==id].iloc[0]
    if "$" not in rows["text"]:
        return [{
            "text": rows["text"],
            "column": rows["column"],
            "operator": rows["operator"],
            "compareto": rows["compareto"],
            "sureness": rows["sureness"]
        }]
    text_options = parse(rows["text"])
    operator_options = parse(rows["operator"])[0]
    compareto_options = parse(rows["compareto"])[0]
    all_options = []
    for i in range(len(text_options[0])):
        text_all = []
        for option in text_options:
            text_all.append(option[i])
        pieces = rows["text"].split("$")
        pieces[1::2] = text_all
        final_text = "".join(pieces)
        all_options.append({
            "text": final_text,
            "column": rows["column"],
            "operator": operator_options[i],
            "compareto": compareto_options[i],
            "sureness": rows["sureness"]
        })
    return all_options

def best_questions(remaining_characters, done_texts):
    qdf = pd.read_csv("questions.csv", low_memory=False)
    all_questions = []
    for qid in qdf["id"]:
        all_questions.extend(get_all_valid_questions(qid))
    questions = []
    for question in all_questions:
        if question["text"] in done_texts:
            continue
        next_valid, out_of = get_valid_for_question(remaining_characters, question)
        if next_valid == 0 or next_valid == out_of: continue
        rem = abs(next_valid - out_of / 2)
        questions.append([question, rem])
    questions.sort(key = lambda x: x[1])
    if questions == []:
        return []
    best_rem = questions[0][1]
    return [question for question, rem in questions if rem <= best_rem + 2]

def check(friend, qn) -> bool | None:
    # [{'text': 'is their height strictly above 175 cm', 'operator': '>', 'compareto': '175'}]
    # [
    #   {'text': 'is their weight below 70 kg', 'operator': '<', 'compareto': '70'}, 
    #   {'text': 'is their weight above 75 kg', 'operator': '>', 'compareto': '75'}
    # ]
    friend_val = friend[qn["column"]]
    qn_val = qn["compareto"]
    op = qn["operator"]
    if pd.isna(friend_val): return None
    if op == "==": return str(friend_val) == qn_val
    if op == ">": return friend_val > float(qn_val)
    if op == ">=": return friend_val >= float(qn_val)
    if op == "<": return friend_val < float(qn_val)
    if op == "<=": return friend_val <= float(qn_val)
    if op == "!=": return str(friend_val) != qn_val
    if op == "in": return str(friend_val) in qn_val.split("|")
    if op == "!in": return str(friend_val) not in qn_val.split("|")

def get_valid_for_question(friends, qn):
    top = friends["score"].max()
    top_friends = friends[friends["score"] * CONTENDER_RATIO >= top]
    s = 0
    for _, friend in top_friends.iterrows():
        res = check(friend, qn)
        if res: s += int(res)
    return s, len(top_friends)

def update_scores(friends, qn, answer):
    s = min(qn["sureness"], 0.99)
    mismatch = 1 - s
    unknown = 1 - (s - 0.5) / 4
    answer_is_yes = (answer == "yes")
    for i, friend in friends.iterrows():
        res = check(friend, qn)
        if res is None:
            friends.at[i, "score"] *= unknown
        elif res != answer_is_yes:
            friends.at[i, "score"] *= mismatch
    return friends

if __name__ == "__main__":
    friends = pd.read_csv("fake.csv")
    friends["score"] = 1.0
    done_questions = []
    while True:
        friends = friends.sort_values("score", ascending=False)
        top = friends.iloc[0]
        second = friends.iloc[1]
        if top["score"] >= second["score"] * 2:
            print(top["name"], "is the answer")
            break
        questions = best_questions(friends, done_questions)
        if questions == []:
            print("I'm out of questions! Best guess:", top["name"])
            break
        question = random.choice(questions)
        answer = input(question["text"] + "? (yes/no) ")
        done_questions.append(question["text"])
        friends = update_scores(friends, question, answer)