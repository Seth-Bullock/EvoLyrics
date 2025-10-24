import streamlit as st
import pandas as pd

from lyric_ga import do_the_ga

do_the_ga()                         # this calls the Python code that runs the GA
#exit()                              # this halts the execution of code in this file

st.write("""
# My second app
Hello *world!*
""")

df = pd.read_csv("my_data.csv")

st.line_chart(df)

