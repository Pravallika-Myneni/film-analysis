
from pickle import encode_long
import streamlit as st

import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from wordcloud import ImageColorGenerator


st.write("""
# Movies X Data Science
Understanding the movies
""")


movie_ratings = pd.read_csv("https://raw.githubusercontent.com/meishinlee/film-analysis/master/datasets/filmtv_movies%20-%20ENG.csv")

netflix_titles = pd.read_csv("https://raw.githubusercontent.com/meishinlee/film-analysis/master/datasets/netflix_titles_nov_2019.csv")

merged = movie_ratings.merge(netflix_titles, left_on=['title','year'], right_on=['title','release_year'])

merged_copy = merged.copy()
merged_copy = merged_copy.drop(["filmtv_id", "country_x","actors","directors","total_votes","show_id","director","cast","country_y","date_added","release_year","duration_y"], axis=1)

category_cols = []
for cat in list(set(merged['listed_in'])):
    cats = cat.strip("'").split(",")
    for ca in cats:
        if ca in category_cols:
            pass
        else:
            category_cols.append(ca.strip())

category_cols=[cat.strip() for cat in category_cols]
# category_cols.sort()
category_set = list(set(category_cols))

data = merged.copy()
for col in category_set:
    data[col] = data['listed_in'].apply(lambda x: 1 if col in x else 0)

numerical_columns = data.select_dtypes(include=np.number).columns.tolist()

st.write("### What genres are represented the most? ")
text = " ".join(i for i in merged.listed_in)
wordcloud = WordCloud(background_color="white").generate(text)
fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")
st.pyplot(fig)

genre_cat = st.selectbox('Genre', category_set, index = 13 )
numerical_column = 'avg_vote'#st.selectbox('Select a numeric column', numerical_columns)

output = data.groupby(genre_cat)[numerical_column].mean()
output = output.reset_index() # can we rename the first column? 
output[genre_cat] = output[genre_cat].apply(lambda x: "Selected genre" if x==1 else "Other genre") 


st.write("### Let's see the average ratings for a specific genre")

genre_vs_col = alt.Chart(output).mark_bar().encode(
    x=str(genre_cat),
    y=numerical_column,
    tooltip = ["avg_vote"]
).properties(
    width=650,
    height=500,
    title="Average Ratings of "+str(genre_cat)+" Categorized Films vs Non "+str(genre_cat) + " Categorized Films"
).interactive()

st.altair_chart(genre_vs_col)

st.write("The genre with highest average ratings is **Classic & Cult TV** with an average rating of", 8.40 )

st.write("### Scatterplot to compare any two characteristics of the movie")

data = data.drop(columns = [col for col in data.columns if '_y' in col])
x1_columns = data.columns
x1 = st.selectbox('X1', x1_columns, index = 2)

y1_columns = [i for i in  data.columns if i!=x1]
y1 =  st.selectbox('Y1',y1_columns, index = 7)


year_avg_vote = alt.Chart(data).mark_point().encode(
    alt.X(x1,
        scale=alt.Scale(zero=False)
    ),
    # x=x1,
    y=y1,
    color='genre',
    tooltip=['title','avg_vote']
).properties(
    title= str(x1) + str(" vs ") + str(y1), 
    width=600,
    height=500
).interactive()

st.altair_chart(year_avg_vote)



cr_pv = alt.Chart(data).mark_circle().encode(
    alt.X('critics_vote', bin=True, scale=alt.Scale(zero=False)),
    alt.Y('public_vote', bin=True),
    size='count()',
    color='genre',
    # color=alt.Color('genre', legend=alt.Legend(
    #     orient='none',
    #     legendX=520, legendY=0,
    #     direction='vertical',
    #     titleAnchor='middle')),
    tooltip=['genre','public_vote','count()']
).properties(
    title= "How do Critic Reviews Compare to Public Reviews?",
    width=200,
    height=650
).interactive()

st.altair_chart(cr_pv, use_container_width=True)


st.write("### Check out how the popularity of genres varies over the years")
df = data.groupby(by=["year", "genre"]).size().reset_index(name="counts")
genre_year = alt.Chart(data).mark_bar().encode(
    x='year',
    y='count(genre)',
    color = 'genre',
    tooltip=['year','genre','count()']
).properties(
    title="Count of Records by Genre and Year", 
    width=600,
    height=500
).interactive()

st.altair_chart(genre_year)



st.markdown("# Inclusive Movie Recommedations")
st.markdown('In Progress')
