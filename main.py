# Junseo Kang, invalidid56@snu.ac.kr
# Streamlit Main Page
#

import streamlit as st
import configparser
import pandas as pd
from konlpy.tag import Okt
from gensim.models.word2vec import Word2Vec
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Config
st.set_page_config(
    page_title='제 63대 선거운동본부, 공명'
)
config = configparser.ConfigParser()
config.read('config.ini')

# Read Data
database = pd.read_csv('db.csv')


# Set Max Width
def _max_width_():
    max_width_str = f"max-width: 1400px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


_max_width_()

# Set Title
st.image('ico.png')
st.title("제 63대 선거운동본부 공명: 에브리타임 여론 청취 대시보드")
st.header("")

# Articles Dashboard
st.write("")
st.markdown("# Articles Dashboard")
keyword_to_display = st.selectbox('키워드를 선택하세요', config['APP']['Keywords'].split(','))
db_to_display = database[database['keyword'] == keyword_to_display].drop(['keyword'], axis=1)
st.dataframe(db_to_display)
st.write("")

# Analysis
st.write("")
st.markdown("# Analysis Dashboard")
keyword_to_anal = st.radio('키워드를 선택하세요', config['APP']['Keywords'].split(','))
db_to_anal = database[database['keyword'] == keyword_to_anal].drop(['keyword'], axis=1)
target_to_anal = st.radio('분석 대상을 선택하세요', ('Article', 'Comment', 'Both'))

#   0. Pre-Process
stop_words = config['APP']['Stopwords'].split(',')
tagger = Okt()

if target_to_anal == 'Article':
    corpus_articles = db_to_anal[db_to_anal['comment_type'] == 'article']['content'].tolist()
    corpus = [[word for word in tagger.nouns(line) if word not in stop_words] for line in corpus_articles]
elif target_to_anal == 'Comment':
    corpus_comments = db_to_anal[db_to_anal['comment_type'] == 'comment']['content'].tolist()
    corpus = [[word for word in tagger.nouns(line) if word not in stop_words] for line in corpus_comments]
else:
    corpus_both = db_to_anal['content'].tolist()
    corpus = [[word for word in tagger.nouns(line) if word not in stop_words] for line in corpus_both]


#   1. Cos-Sim Analysis
st.markdown("## 1. Cos-Sim Analysis")
model = Word2Vec(corpus, min_count=1, workers=4)
most_similar = model.wv.most_similar(keyword_to_anal, topn=15)
st.write("{0}와 가장 유사한 단어는 다음과 같습니다".format(keyword_to_anal))
st.table(pd.DataFrame(most_similar))

#   2. Wordcloud Analysis
st.markdown("## 2. WordCloud Analysis")
word_list = sum(corpus, [])
counts = Counter(word_list)
tags = counts.most_common(40)

wc = WordCloud(background_color='Black', width=1300, height=650, scale=2.0, max_font_size=250,
               font_path=config['APP']['Font'], colormap='PuBu')

try:
    cloud = wc.generate_from_frequencies(dict(tags))
except OSError:
    wc = WordCloud(background_color='Black', width=1300, height=650, scale=2.0, max_font_size=250,
                   colormap='PuBu')
    cloud = wc.generate_from_frequencies(dict(tags))

fig = plt.figure(figsize=(10, 8))
plt.axis('off')
plt.imshow(cloud)

st.pyplot(fig)

#   3. Time-Series Articles / Comments
st.markdown("## 3. Time Series Mentions")
db_to_anal['time'] = db_to_anal['time'].map(int)
if target_to_anal == 'Article':
    count_per_time = db_to_anal[db_to_anal['comment_type'] == 'article'].groupby('time')['content'].count()
elif target_to_anal == 'Comment':
    count_per_time = db_to_anal[db_to_anal['comment_type'] == 'comment'].groupby('time')['content'].count()
else:
    count_per_time = db_to_anal.groupby('time')['content'].count()

st.line_chart(count_per_time)
