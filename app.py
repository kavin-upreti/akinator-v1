import random

import pandas as pd
import streamlit as st

from main import best_questions, update_scores


def new_game() -> None:
    """Reset session state to the same starting point as the terminal game."""
    friends = pd.read_csv("fake.csv")
    friends["score"] = 1.0
    st.session_state.friends = friends
    st.session_state.done_questions = []
    st.session_state.question = None
    st.session_state.result = None


def answer(reply: str) -> None:
    """One pass of the original while-loop body, after input()."""
    question = st.session_state.question
    st.session_state.done_questions.append(question["text"])
    st.session_state.friends = update_scores(st.session_state.friends, question, reply)
    st.session_state.question = None  # why: forces a fresh best_questions pick on the next rerun


st.title("Guess the friend")

if "friends" not in st.session_state:
    new_game()

# why: Streamlit reruns the whole script on every click, so each rerun is one
# iteration of the original while-loop; state lives in session_state instead of locals.
if st.session_state.result is None:
    friends = st.session_state.friends.sort_values("score", ascending=False)
    st.session_state.friends = friends
    top = friends.iloc[0]
    second = friends.iloc[1]
    if top["score"] >= second["score"] * 2:
        st.session_state.result = f"{top['name']} is the answer"
    else:
        if st.session_state.question is None:
            questions = best_questions(friends, st.session_state.done_questions)
            if questions == []:
                st.session_state.result = f"I'm out of questions! Best guess: {top['name']}"
            else:
                # why: pick once and store it, otherwise every rerun would show a different random question
                st.session_state.question = random.choice(questions)

if st.session_state.result is not None:
    st.success(st.session_state.result)
    st.button("Play again", icon=":material/replay:", on_click=new_game)
else:
    st.caption(f"Question {len(st.session_state.done_questions) + 1}")
    st.subheader(st.session_state.question["text"] + "?")
    with st.container(horizontal=True):
        st.button("Yes", icon=":material/check:", on_click=answer, args=("yes",))
        st.button("No", icon=":material/close:", on_click=answer, args=("no",))

with st.expander("Scores"):
    st.dataframe(st.session_state.friends[["name", "score"]], hide_index=True)
