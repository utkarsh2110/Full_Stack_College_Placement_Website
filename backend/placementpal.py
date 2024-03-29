# -*- coding: utf-8 -*-
"""PlacementPal.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VCFJx9nGEl8sKZRQwAbe0-9E01pecEv3
"""

from pyngrok import ngrok

# Set up the ngrok tunnel
public_url = ngrok.connect(port='3000', options={'bind_tls': True})
print(public_url)

import pathlib
import textwrap
import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

from google.colab import userdata
GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
gen_model = genai.GenerativeModel('gemini-pro')

def ask_gemini(ques):
    response = gen_model.generate_content(ques)
    to_markdown(response.text)
    return response.text

ask_gemini("How can I prepare for Infosys Interview?")

import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter

##### Read Data
data=pd.read_csv("Questions.csv", encoding = "ISO-8859-1")

##### Visualize your Data
print ("Let's explore our question set",data["Question"])
print ("Length of training set",len(data["Question"]))
print ("Unique answers are",set(data["Classes"])," and number of unique answers are ", len(set(data["Classes"])))

##### Now let's create a wordcloud to get a better understanding of our corpus
import matplotlib.pyplot as plt
from wordcloud import WordCloud
##### Download using conda install -c conda-forge wordcloud

def show_wordcloud(data, title = None):
    wordcloud = WordCloud(background_color='black',).generate(str(data))
    fig = plt.figure(1, figsize=(12, 12))
    plt.axis('off')
    plt.imshow(wordcloud)
    plt.show()


show_wordcloud(data['Question'])

##### Let's change the list of questions into list of words for better visualization
word_list=[]
list_question=list(data["Question"])
for sentence in list_question:
	words_sentence=sentence.split()
	for words in words_sentence:
		word_list.append(words)


word_list=[word for sentence in list(data["Question"]) for word in sentence.split()]
print(word_list)

##### Now let's find the frequency of each word and the most common words in the corpus
frequency=Counter(word_list)
print (frequency)
print (frequency.most_common(5))

import numpy as np

labels,values = zip(*frequency.items())
labels=[]
values=[]
for T in frequency.most_common(5):
    labels.append(T[0])
    values.append(T[1])

indexes = np.arange(len(labels))
width = 1

plt.bar(indexes, values, width)
plt.xticks(indexes + width * 0.05, labels)
plt.show()

### Remove Punctuations and change words to lower case
def remove_punctuations(text):
    words=[word.lower() for word in text.split()]
    words=[w for word in words for w in re.sub(r'[^\w\s]','',word).split()]
    return words

data["question_punctuation_removed"]=data["Question"].apply(remove_punctuations)
print (data["question_punctuation_removed"])

### Remove StopWords
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stop = set(stopwords.words('english'))
print (stop)
def remove_stopwords(text):
	modified_word_list=[word for word in text if word not in stop]
	return modified_word_list

data["question_stopword_removed"]=data["question_punctuation_removed"].apply(remove_stopwords)
print (data["question_stopword_removed"])

def negation_handling(words):
    counter=False
    wlist=[]
    negations=["no","not","cant","cannot","never","less","without","barely","hardly","rarely","no","not","noway","didnt"]
    #for words in wordlist:
    for i,j in enumerate(words):
            if j in negations and i<len(words)-1:
                wlist.append(str(words[i]+'-'+words[i+1]))
                counter=True
            else:
                if counter is False:
                    wlist.append(words[i])
                else:
                    counter=False
    return wlist

data["question_negated"]=data["question_punctuation_removed"].apply(negation_handling)
print (data["question_negated"])

import nltk
from nltk.tag import pos_tag
nltk.download('averaged_perceptron_tagger')


def descriptive_words(words):
    meaningful_words=[]
    tags=['VB','VBP','VBD','VBG','VBN','JJ','JJR','JJS','RB','RBR','RBS','UH',"NN",'NNP']
    tagged_word=pos_tag(words)
    for word in tagged_word:
        if word[1] in tags:
            meaningful_words.append(word[0])
    return meaningful_words
data["question_descriptive"]=data["question_negated"].apply(descriptive_words)
# print (data["question_descriptive"])

### Stemming of Words
from nltk.stem.porter import PorterStemmer
st=PorterStemmer()
def Stemming(text):
	stemmed_words=[st.stem(word) for word in text]
	return stemmed_words

data["question_stemmed"]=data["question_descriptive"].apply(Stemming)
print (data["question_stemmed"])

### Recreating the sentence
def Recreate(text):
	word=" ".join(text)
	return word

data["modified_sentence"]=data["question_stemmed"].apply(Recreate)
# print (data["modified_sentence"])

def Cleaning(text):
    text_punctuation_removed=remove_punctuations(text)
    text_stopword_removed=remove_stopwords(text_punctuation_removed)
    text_unnegated=negation_handling(text_punctuation_removed)
    text_descriptive=descriptive_words(text_unnegated)
    text_stemmed=Stemming(text_descriptive)
    final_text=Recreate(text_stemmed)
    return final_text
data["modified_sentence"]=data["Question"].apply(Cleaning)
# print (data["modified_sentence"])

### Let's change the sentence into a bag of word model
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data["Question"]).toarray()
print(X)
# print(vectorizer.get_feature_names())

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

###### Extra Tf-idf transformation and DataPipelines
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
model = Pipeline([('vectoizer', CountVectorizer()),
 ('tfidf', TfidfTransformer())])

X = model.fit_transform(data["modified_sentence"]).toarray()
print(X)

Y=data["Classes"]
question="How can I prepare for PayPal's Hackerrank Test for the role of Software Engineer?"

type(Y)

"""### Code for Testing Purpose"""

testing = pd.read_csv("Testing.csv", encoding = "ISO-8859-1")

X_test = testing["Question"]

y_test = testing['Classes']
print(type(y_test))

"""### Logistic Regression"""

### Let's create our first Classification model

from sklearn.linear_model import LogisticRegression
clf1 = LogisticRegression().fit(X, Y) #X-train, y_train


P=model.transform([Cleaning(question)])
predict1=clf1.predict(P)
print (predict1)

''' Logistic Regression '''

y_pred_lr = []
for test_q in X_test:
   P=model.transform([Cleaning(test_q)])
   predict1=clf1.predict(P)
   y_pred_lr.append(predict1)



# Calculate accuracy, precision, recall, and f1-score
accuracy_lr = accuracy_score(y_test, y_pred_lr)
precision_lr = precision_score(y_test, y_pred_lr, average='weighted')
recall_lr = recall_score(y_test, y_pred_lr, average='weighted')
f1_lr = f1_score(y_test, y_pred_lr, average='weighted')

# Print the results
print(f'Accuracy Score: {accuracy_lr*100:.2f}%')
print(f'Precision: {precision_lr*100:.2f}%')
print(f'Recall: {recall_lr*100:.2f}%')
# print(f'F1-Score: {f1_lr*100:.2f}%')

"""### Multinomial Naive Bayes"""

from sklearn.naive_bayes import MultinomialNB
clf2 = MultinomialNB().fit(X, Y)

P=model.transform([Cleaning(question)])
predict2=clf2.predict(P)
print (predict2)

''' Multinomial NB '''

y_pred_mnb = []
for test_q in X_test:
   P=model.transform([Cleaning(test_q)])
   predict2=clf2.predict(P)
   y_pred_mnb.append(predict2)


# Calculate accuracy, precision, recall, and f1-score
accuracy_mnb = accuracy_score(y_test, y_pred_mnb)
precision_mnb = precision_score(y_test, y_pred_mnb, average='weighted')
recall_mnb = recall_score(y_test, y_pred_mnb, average='weighted')
f1_mnb = f1_score(y_test, y_pred_mnb, average='weighted')

# Print the results
print(f'Accuracy Score: {accuracy_mnb*100:.2f}%')
print(f'Precision: {precision_mnb*100:.2f}%')
print(f'Recall: {recall_mnb*100:.2f}%')
# print(f'F1-Score: {f1_mnb*100:.2f}%')

"""### Decision Tree Classifier"""

from sklearn.tree import DecisionTreeClassifier
clf3 = DecisionTreeClassifier().fit(X, Y)

P=model.transform([Cleaning(question)])
predict3=clf3.predict(P)
print (predict3)

''' Decision Tree Classifier '''

y_pred_dt = []
for test_q in X_test:
   P=model.transform([Cleaning(test_q)])
   predict3=clf3.predict(P)
   y_pred_dt.append(predict3)



# Calculate accuracy, precision, recall, and f1-score
accuracy_dt = accuracy_score(y_test, y_pred_dt)
precision_dt = precision_score(y_test, y_pred_dt, average='weighted')
recall_dt = recall_score(y_test, y_pred_dt, average='weighted')
f1_dt = f1_score(y_test, y_pred_dt, average='weighted')

# Print the results
print(f'Accuracy Score: {accuracy_dt*100:.2f}%')
print(f'Precision: {precision_dt*100:.2f}%')
print(f'Recall: {recall_dt*100:.2f}%')
# print(f'F1-Score: {f1_dt*100:.2f}%')

"""### Linear SVC"""

from sklearn.svm import LinearSVC
clf4 = LinearSVC().fit(X, Y)

P=model.transform([Cleaning(question)])
predict4 = clf4.predict(P)
print(predict4)

''' Linear SVC '''

y_pred_lvc = []
for test_q in X_test:
   P=model.transform([Cleaning(test_q)])
   predict4=clf4.predict(P)
   y_pred_lvc.append(predict4)



# Calculate accuracy, precision, recall, and f1-score
accuracy_lvc = accuracy_score(y_test, y_pred_lvc)
precision_lvc = precision_score(y_test, y_pred_lvc, average='weighted')
recall_lvc = recall_score(y_test, y_pred_lvc, average='weighted')
f1_lvc = f1_score(y_test, y_pred_lvc, average='weighted')

# Print the results
print(f'Accuracy Score: {accuracy_lvc*100:.2f}%')
print(f'Precision: {precision_lvc*100:.2f}%')
print(f'Recall: {recall_lvc*100:.2f}%')
# print(f'F1-Score: {f1_lvc*100:.2f}%')

"""### Random Forest Classifier"""

from sklearn.ensemble import RandomForestClassifier
clf5 = RandomForestClassifier().fit(X, Y)

P=model.transform([Cleaning(question)])
predict5 = clf5.predict(P)
print(predict5)

''' Random Forest Classifier '''

y_pred_rf = []
for test_q in X_test:
   P=model.transform([Cleaning(test_q)])
   predict5=clf5.predict(P)
   y_pred_rf.append(predict5)


# Calculate accuracy, precision, recall, and f1-score
accuracy_rf = accuracy_score(y_test, y_pred_rf)
precision_rf = precision_score(y_test, y_pred_rf, average='weighted')
recall_rf = recall_score(y_test, y_pred_rf, average='weighted')
f1_rf = f1_score(y_test, y_pred_rf, average='weighted')

# Print the results
print(f'Accuracy Score: {accuracy_rf*100:.2f}%')
print(f'Precision: {precision_rf*100:.2f}%')
print(f'Recall: {recall_rf*100:.2f}%')
# print(f'F1-Score: {f1_rf*100:.2f}%')

final_predict=[]
final_predict=list(predict1)+list(predict2)+list(predict3)+list(predict4)+list(predict5)
final_predict = Counter(final_predict)
print ("Thus answer to your question is",final_predict.most_common(1)[0][0])

from sklearn import tree
from six import StringIO
from sklearn.tree import export_graphviz
import pydotplus

dot_data = StringIO()
export_graphviz(clf3, out_file=dot_data,
                filled=True, rounded=True,
                special_characters=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())

print (graph)
graph.write_pdf("iris.pdf")
from IPython.display import Image

Image(graph.create_png())

def Predict(text):
    P=model.transform([Cleaning(text)])
    predict1=clf1.predict(P)
    #print (predict1)

    predict2=clf2.predict(P)
    #print (predict2)

    predict3=clf3.predict(P)
    #print (predict3)

    predict4=clf4.predict(P)
    #print (predict3)

    predict5=clf5.predict(P)
    #print (predict3)

    final_predict=[]
    final_predict=list(predict1)+list(predict2)+list(predict3)+list(predict4)+list(predict5)
    final_predict = Counter(final_predict)
    # print(final_predict.most_common(1)[0][0])
    # print ("Class of Question belongs to =",final_predict.most_common(1)[0][0])

    return final_predict.most_common(1)[0][0]

def PredictBatch(X, y):
    P=model.transform([Cleaning(str(text)) for text in X])
    predict1=clf1.predict(P)
    #print (predict1)

    predict2=clf2.predict(P)
    #print (predict2)

    predict3=clf3.predict(P)
    #print (predict3)

    final_predict=[]
    final_predict=list(predict1)+list(predict2)+list(predict3)
    final_predict = Counter(final_predict)
    predicted_class = final_predict.most_common(1)[0][0]

    # Calculate metrics
    precision = precision_score(y, np.array([predicted_class] * len(X_test)), average='weighted')
    recall = recall_score(y, np.array([predicted_class] * len(X_test)), average='weighted')
    f1 = f1_score(y, np.array([predicted_class] * len(X_test)), average='weighted')

    print(f'Precision: {precision:.4f}')
    print(f'Recall: {recall:.4f}')
    print(f'F1-Score: {f1:.4f}')
    print(f'Predicted Class: {final_predict}')
    print(f'True Class: {y}')

    return np.array([final_predict] * len(X_train))

PredictBatch(X_test, y_test)

"""Applying Predict on Testing dataset"""

print(X_test)

"""Applying the model for test dataset"""

y_pred = []
for test_q in X_test:
  # print(q)
  pred = Predict(test_q)
  y_pred.append(pred)


print(X_test)
print(y_pred)

# Calculate precision, recall, and f1-score
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

# Print the results
print(f'Accuracy Score: {accuracy*100:.2f}%')
print(f'Precision: {precision*100:.2f}%')
print(f'Recall: {recall*100:.2f}%')
# print(f'F1-Score: {f1*100:.2f}%')

##### Finding the most similar sentence
from sklearn.metrics.pairwise import linear_kernel

cosine_similarities = linear_kernel(X_train[1], X_train).flatten()
print ("Cosine Similarity of",data["question"][0],"with all questions in Corpus",cosine_similarities)
index=[i+1 for i in range(len(X))]
print (index)
print ("top 3 most similar question's to",data["question"][0],"are :")
print (sorted(zip(cosine_similarities, index, data["question"][index]), reverse=True)[:3])
print ("Thus answer to your question is ", max(data["answer"][index[0]],data["answer"][index[1]],data["answer"][index[3]]))

###### Generate Answers ######
answer_dictionary={
    "Greetings":[
        "Hello 👋🏻 I am PlacementPal , How can I assist you today?","Good morning","Have a pleasant day","Good Day"
        ],
      "Placement Data - companies":[
          '''Last year, a total of 50 companies visited our campus for placements. During placements,
          companies primarily look for candidates with strong technical skills such as programming languages like Python, Java, and C++,
          as well as proficiency in data analysis, problem-solving, and communication. The roles offered by these companies vary,
          including software engineer, data analyst, business analyst, product manager, and more.'''
          ],
    "Placement Data - packages":[
          '''The highest package offered was 15,00,000 per annum.
          The average CTC stood at Rs 6,00,000 per annum, where as median CTC was Rs 6,00,000 per annum'''
          ],
    "Placement Data - packages": [
        ''''''
    ],
      "Document Verification": [
          '''You can upload your documents under Documents section in your student dashboard which will be verified once you submit.
          Please make sure you have the scanned copy of the following documents :-
              - CV
              - Last Semester Marksheet
              - 12th Marksheet
              - 10th Marksheet'''
       ],
      "Training and Resources": [
          '''For information regarding available training programs to prepare for placements or details about placement training workshops offered by the placement cell,
          I recommend visiting the Training and Placement tab on our website.
          You'll find comprehensive information and updates regarding all training programs and workshops offered to help students prepare for placements.'''
      ],
      "Placement Process": [
          ''''''
      ],
      "Trouble shooting": [
        ''''''
      ],
      "Other": [
        ''''''
    ]

    }

import random

def generate_answer(predict_class):
    ans=random.choice(answer_dictionary[predict_class])
    return ans

###### The ChatBot #######
question = input("Enter Question = ")
prediction = Predict(question)
print(prediction)
if (prediction == "Other"):
      ask_gemini(question)
# ans=generate_answer(prediction)
# print("Answer = ",ans)

