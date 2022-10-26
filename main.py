import streamlit as st
import pandas as pd
import numpy as np
from gensim.models.word2vec import Word2Vec
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt

#
# Read Data, Parse Data
#
with open('keyword.txt', 'r') as kw:
    keywords = [line.strip() for line in kw.readline().split(',')]
corpus = pd.read_csv('scrap.csv')

stop_words = '등 것 이 말 명 전 그 고 위 때문 마련 저 라고 수 기자'
stop_words = stop_words.split(' ')

model = dict()
cloud = dict()

for kw in keywords:
    kw_corpus = [line.strip('"').split(',') for line
                 in corpus[corpus['Keyword'] == kw]['Article'].tolist() if isinstance(line, str)]
    model[kw] = Word2Vec(kw_corpus, min_count=1, workers=4)

    #

    word_list = sum(kw_corpus, [])
    counts = Counter(word_list)
    tags = counts.most_common(40)

    wc = WordCloud(background_color='White', font_path='MaruBuri-Regular.ttf')
    cloud[kw] = wc.generate_from_frequencies(dict(tags))

#
# Main Page
#
st.title('공명: 에브리타임 여론 청취 대시보드')


st.write('키워드별 빅데이터 분석')
option_kw = st.selectbox(
    '조회할 키워드를 선택해주세요',
    pd.Series(keywords)
)

st.write('{0} 키워드와 가장 유사한 단어 10개'.format(option_kw))
st.write(model[option_kw].wv.most_similar(option_kw + ('생회' if option_kw == '총학' else ''), topn=10))


fig = plt.figure(figsize=(10, 8))
plt.axis('off')
plt.imshow(cloud[option_kw])
plt.show()

st.pyplot(fig)






