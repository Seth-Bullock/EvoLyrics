import streamlit as st
import pandas as pd

st.write("""
# Evolving Lyrics
""")

from lyric_ga import do_the_ga

#do_the_ga()                         # this calls the Python code that runs the GA
#exit()                              # this halts the execution of code in this file

do_the_ga(author="taylor", target=None, length=25, elitism=True, crossover=0.5, pressure=3)
#exit() # this exits the code - nothing below this line will be executed


st.write("""
# Finished!
""")

#df = pd.read_csv("my_data.csv")

#st.line_chart(df)



