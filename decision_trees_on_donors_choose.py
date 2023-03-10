
# Commented out IPython magic to ensure Python compatibility.
# Import all the necessary libraries 
# %matplotlib inline
import warnings
warnings.filterwarnings("ignore")


import pandas as pd
import numpy as np
import nltk
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from sklearn.metrics import roc_curve, auc

import re

import pickle
from tqdm import tqdm
import os

import plotly
import plotly.offline as offline
import plotly.graph_objs as go
offline.init_notebook_mode()
from collections import Counter

data = pd.read_csv('/content/drive/MyDrive/Main_uploads/preprocessed_data.csv',nrows=50000)

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

# Assigning the sentiment score to respective variables.
data['neg'] = [sid.polarity_scores(i).get('neg') for i in data['essay']]
data['pos'] = [sid.polarity_scores(i).get('pos') for i in data['essay']]
data['neu'] = [sid.polarity_scores(i).get('neu') for i in data['essay']]
data['compound'] = [sid.polarity_scores(i).get('compound') for i in data['essay']]

data.head()

len(data)

data.info()

y = data['project_is_approved'].values
X = data.drop(['project_is_approved'], axis=1)

#Spliting the data into trian and test data using stratify as y
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, stratify=y,random_state=33)

# Implementing tfidfvectorizer on essay
vec = TfidfVectorizer(min_df=10,ngram_range=(1,4), max_features=5000)
tf_idf = vec.fit(X_train['essay'].values)

X_train_essay_tfidf = tf_idf.transform(X_train['essay'].values)
X_test_essay_tfidf = tf_idf.transform(X_test['essay'].values)

vec = TfidfVectorizer()
vec.fit(X_train['essay'])
tfidf_words = set(vec.get_feature_names())
dictionary = dict(zip(vec.get_feature_names(), list(vec.idf_)))

# Getting all the glove_words for implementing tfidf_w2v
with open('/content/drive/MyDrive/Main_uploads/glove_vectors', 'rb') as f:
    model = pickle.load(f)
    glove_words =  set(model.keys())

X_train_tfidf_w2v = []
for sentence in tqdm(X_train["essay"]):
    vector = np.zeros(300) 
    weight =0
    for word in sentence.split(): 
        if (word in glove_words) and (word in tfidf_words):
            tf_idf = dictionary[word]*(sentence.count(word)/len(sentence.split())) 
            weight += tf_idf
    if weight != 0:
        vector /= weight
    X_train_tfidf_w2v.append(vector)
X_train_tfidf_w2v=np.array(X_train_tfidf_w2v)

X_test_tfidf_w2v = []
for sentence in tqdm(X_test['essay']):
  vector = np.zeros(300)
  weight =0
  for word in sentence.split():
    if (word in glove_words) and (word in tfidf_words):
      tf_idf = dictionary[word]*(sentence.count(word)/len(sentence.split()))
      weight +=tf_idf
  if weight !=0:
    vector /= weight
  X_test_tfidf_w2v.append(vector)
X_test_tfidf_w2v=np.array(X_test_tfidf_w2v)

#Converting the school_state to One hot encoding.
vectorizer = CountVectorizer()
vectorizer.fit(X_train['school_state'].values) # fit has to happen only on train data

X_train_state_ohe = vectorizer.transform(X_train['school_state'].values)
X_test_state_ohe = vectorizer.transform(X_test['school_state'].values)

vectorizer = CountVectorizer()
vectorizer.fit(X_train['teacher_prefix'].values)

X_train_teacher_prefix_ohe = vectorizer.transform(X_train['teacher_prefix'].values)
X_test_teacher_prefix_ohe = vectorizer.transform(X_test['teacher_prefix'].values)

#Converting the project_grade_category to array with the help of one_hot_encoding.
vectorizer = CountVectorizer()
vectorizer.fit(X_train['project_grade_category'].values)

X_train_project_grade_category_ohe = vectorizer.transform(X_train['project_grade_category'].values)
X_test_project_grade_category_ohe = vectorizer.transform(X_test['project_grade_category'].values)

#Converting the clean_categories to array with the help of one_hot_encoding.
vectorizer = CountVectorizer()
vectorizer.fit(X_train['clean_categories'].values)

X_train_clean_categories_ohe = vectorizer.transform(X_train['clean_categories'].values)
X_test_clean_categories_ohe = vectorizer.transform(X_test['clean_categories'].values)

#Converting the clean_subcategories to array with the help of one_hot_encoding.
vectorizer = CountVectorizer()
vectorizer.fit(X_train['clean_subcategories'].values)

X_train_clean_subcategories_ohe = vectorizer.transform(X_train['clean_subcategories'].values)
X_test_clean_subcategories_ohe = vectorizer.transform(X_test['clean_subcategories'].values)

# One_hot_encoding is not appropriate for numerical values so using Normalizer.
from sklearn.preprocessing import Normalizer
normalizer = Normalizer()

normalizer.fit(X_train['price'].values.reshape(-1,1))

X_train_price_norm = normalizer.transform(X_train['price'].values.reshape(-1,1))
X_test_price_norm = normalizer.transform(X_test['price'].values.reshape(-1,1))

normalizer = Normalizer()

normalizer.fit(X_train['teacher_number_of_previously_posted_projects'].values.reshape(-1,1))

X_train_previous_posted_norm = normalizer.transform(X_train['teacher_number_of_previously_posted_projects'].values.reshape(-1,1))
X_test_previous_posted_norm = normalizer.transform(X_test['teacher_number_of_previously_posted_projects'].values.reshape(-1,1))

normalizer = Normalizer()

normalizer.fit(X_train['neg'].values.reshape(-1,1))

X_train_neg_norm = normalizer.transform(X_train['neg'].values.reshape(-1,1))
X_test_neg_norm = normalizer.transform(X_test['neg'].values.reshape(-1,1))

normalizer = Normalizer()

normalizer.fit(X_train['pos'].values.reshape(-1,1))

X_train_pos_norm = normalizer.transform(X_train['pos'].values.reshape(-1,1))
X_test_pos_norm = normalizer.transform(X_test['pos'].values.reshape(-1,1))

normalizer = Normalizer()

normalizer.fit(X_train['neu'].values.reshape(-1,1))

X_train_neu_norm = normalizer.transform(X_train['neu'].values.reshape(-1,1))
X_test_neu_norm = normalizer.transform(X_test['neu'].values.reshape(-1,1))

normalizer = Normalizer()

normalizer.fit(X_train['compound'].values.reshape(-1,1))

X_train_compound_norm = normalizer.transform(X_train['compound'].values.reshape(-1,1))
X_test_compound_norm = normalizer.transform(X_test['compound'].values.reshape(-1,1))

from scipy.sparse import hstack
# Joining all the features horizontally using hstack.
set_1_x_train = hstack((X_train_essay_tfidf,X_train_state_ohe,X_train_teacher_prefix_ohe,X_train_project_grade_category_ohe,X_train_clean_categories_ohe,X_train_clean_subcategories_ohe,X_train_price_norm,X_train_previous_posted_norm,X_train_neg_norm,X_train_pos_norm,X_train_neu_norm,X_train_compound_norm))
set_1_x_test = hstack((X_test_essay_tfidf,X_test_state_ohe,X_test_teacher_prefix_ohe,X_test_project_grade_category_ohe,X_test_clean_categories_ohe,X_test_clean_subcategories_ohe,X_test_price_norm,X_test_previous_posted_norm,X_test_neg_norm,X_test_pos_norm,X_test_neu_norm,X_test_compound_norm))

set_2_x_train = hstack((X_train_tfidf_w2v,X_train_state_ohe,X_train_teacher_prefix_ohe,X_train_project_grade_category_ohe,X_train_clean_categories_ohe,X_train_clean_subcategories_ohe,X_train_price_norm,X_train_previous_posted_norm,X_train_neg_norm,X_train_pos_norm,X_train_neu_norm,X_train_compound_norm))
set_2_x_test = hstack((X_test_tfidf_w2v,X_test_state_ohe,X_test_teacher_prefix_ohe,X_test_project_grade_category_ohe,X_test_clean_categories_ohe,X_test_clean_subcategories_ohe,X_test_price_norm,X_test_previous_posted_norm,X_test_neg_norm,X_test_pos_norm,X_test_neu_norm,X_test_compound_norm))

print(set_1_x_train.shape)
print(set_1_x_test.shape)
print(set_2_x_train.shape)
print(set_2_x_test.shape)

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
neigh = DecisionTreeClassifier(class_weight='balanced')
parameter = {'max_depth': [1, 3, 10, 30], 'min_samples_split': [5, 10, 100, 500]}

# Implementing the Gridsearchcv to find best param, best_score.
clf = GridSearchCV(neigh,param_grid=parameter,cv=5,scoring='roc_auc',return_train_score=True)
clf.fit(set_1_x_train,y_train)

print('best_score: ', clf.best_score_)
print('best_parameter: ', clf.best_params_)

import plotly.offline as offline
import plotly as py
import plotly.graph_objs as go
offline.init_notebook_mode()
import numpy as np
import matplotlib.pyplot as plt

x_axis = [5,10,100,500]
y_axis = [1,3,10,30]
z1 = clf.cv_results_['mean_train_score']
z2 = clf.cv_results_['mean_test_score']


trace1 = go.Scatter3d(x=x_axis,y=y_axis,z=z1, name = 'train')
trace2 = go.Scatter3d(x=x_axis,y=y_axis,z=z2, name = 'Cross validation')
data = [trace1, trace2]

layout = go.Layout(scene = dict(
        xaxis = dict(title='min_sample_split'),
        yaxis = dict(title='max_depth'),
        zaxis = dict(title='AUC'),))

fig = go.Figure(data=data, layout=layout)
offline.plot(fig, filename='3d_scatter_colorscale')
fig.show()
plt.show()

dt = DecisionTreeClassifier(class_weight='balanced',max_depth =30, min_samples_split=500 )
dt.fit(set_1_x_train,y_train)
y_train_prob = dt.predict_proba(set_1_x_train)[:,1]
y_test_prob = dt.predict_proba(set_1_x_test)[:,1]

train_fpr,train_tpr,train_threshold = roc_curve(y_train,y_train_prob)
test_fpr,test_tpr,test_threshold = roc_curve(y_test,y_test_prob)

plt.figure(figsize=(10,8))
plt.plot(train_fpr,train_tpr,label='train_AUC')
plt.plot(test_fpr,test_tpr,label='test_AUC')
plt.legend()
plt.xlabel("False positive rate")
plt.ylabel("True positive rate")
plt.title('ROC Curve')
plt.grid()
plt.show()

print(auc(test_fpr,test_tpr))

# This will find the threshold to get the confusion_matrix.
def find_best_threshold(threshould, fpr, tpr):
  t = threshould[np.argmax(tpr*(1-fpr))]

  print("the maximum value of tpr*(1-fpr)", max(tpr*(1-fpr)), "for threshold", np.round(t,3))
  return t

def predict_with_best_t(proba, threshould):
  predictions =[]
  for i in proba:
    if i>=threshould:
      predictions.append(1)
    else:
      predictions.append(0)
  return predictions

# importing confusion_matrix.
from sklearn.metrics import confusion_matrix
best_t = find_best_threshold(train_threshold, train_fpr, train_tpr)
con_m=confusion_matrix(y_train, predict_with_best_t(y_train_prob, best_t))
# Using heatmap to make things more clear.
sns.heatmap(con_m, annot=True, fmt='d',cmap='coolwarm')
plt.title("Train Confusion Matrix")
plt.xlabel("Precicted Label")
plt.ylabel("Actual Label")
plt.show()

best_t = find_best_threshold(test_threshold, test_fpr, test_tpr)
con_m=confusion_matrix(y_test, predict_with_best_t(y_test_prob, best_t))
# Using heatmap to make things more clear.
sns.heatmap(con_m, annot=True, fmt='d',cmap='coolwarm')
plt.title("Test Confusion Matrix")
plt.xlabel("Precicted Label")
plt.ylabel("Actual Label")
plt.show()

predict = predict_with_best_t(y_test_prob,best_t)

fpi = []
for i in range(len(y_test)):
  if (y_test[i]==0) and (predict[i] ==1):
    fpi.append(i)

cols = X_test.columns
false_positive = pd.DataFrame(columns=cols)
false_positive = X_test.iloc[fpi]
len(false_positive)

from wordcloud import WordCloud, STOPWORDS
comment_words = ''
stopwords = set(STOPWORDS)
for word in false_positive['essay']:
  val = str(word)  #https://www.geeksforgeeks.org/generating-word-cloud-python/
  tokens = val.split()
  for i in range(len(tokens)):
    tokens[i] = tokens[i].lower()
  comment_words += " ".join(tokens)+" "

wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(comment_words)

plt.figure(figsize=(8,8),)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)

plt.show()

plt.figure(figsize=(8,6))
sns.boxplot('price',data=false_positive,orient="V").set_title("Box plot of price on false positive")
plt.grid()

plt.figure(figsize=(8,6))
counts, bin_edges = np.histogram(false_positive['teacher_number_of_previously_posted_projects'], bins=10, density = True)

pdf = counts/(sum(counts))
plt.plot(bin_edges[1:],pdf,color='blue')
plt.title("teacher number of previously posted of false positive data")
plt.xlabel('teacher number of previously posted projects')

clf = GridSearchCV(neigh,param_grid=parameter,cv=5,scoring='roc_auc',return_train_score=True)
clf.fit(set_2_x_train,y_train)

print('best_score: ', clf.best_score_)
print('best_parameter: ', clf.best_params_)

import plotly.offline as offline
import plotly as py
import plotly.graph_objs as go
offline.init_notebook_mode()
import numpy as np
import matplotlib.pyplot as plt

x_axis = [5,10,100,500]
y_axis = [1,3,10,30]
z1 = clf.cv_results_['mean_train_score']
z2 = clf.cv_results_['mean_test_score']


trace1 = go.Scatter3d(x=x_axis,y=y_axis,z=z1, name = 'train')
trace2 = go.Scatter3d(x=x_axis,y=y_axis,z=z2, name = 'Cross validation')
data = [trace1, trace2]

layout = go.Layout(scene = dict(
        xaxis = dict(title='min_sample_split'),
        yaxis = dict(title='max_depth'),
        zaxis = dict(title='AUC'),))

fig = go.Figure(data=data, layout=layout)
offline.plot(fig, filename='3d_scatter_colorscale')
fig.show()
plt.show()

dt = DecisionTreeClassifier(class_weight='balanced',max_depth =30, min_samples_split=500 )
dt.fit(set_2_x_train,y_train)
y_train_prob = dt.predict_proba(set_2_x_train)[:,1]
y_test_prob = dt.predict_proba(set_2_x_test)[:,1]

train_fpr,train_tpr,train_threshold = roc_curve(y_train,y_train_prob)
test_fpr,test_tpr,test_threshold = roc_curve(y_test,y_test_prob)

plt.figure(figsize=(10,8))
plt.plot(train_fpr,train_tpr,label='train_AUC')
plt.plot(test_fpr,test_tpr,label='train_AUC')
plt.legend()
plt.xlabel("False positive rate")
plt.ylabel("True positive rate")
plt.title('ROC Curve')
plt.grid()
plt.show()

print(auc(test_fpr,test_tpr))

# This will find the threshold to get the confusion_matrix.
def find_best_threshold(threshould, fpr, tpr):
  t = threshould[np.argmax(tpr*(1-fpr))]

  print("the maximum value of tpr*(1-fpr)", max(tpr*(1-fpr)), "for threshold", np.round(t,3))
  return t

def predict_with_best_t(proba, threshould):
  predictions =[]
  for i in proba:
    if i>=threshould:
      predictions.append(1)
    else:
      predictions.append(0)
  return predictions

# importing confusion_matrix.
from sklearn.metrics import confusion_matrix
best_t = find_best_threshold(train_threshold, train_fpr, train_tpr)
print("Train confusion matrix")
con_m=confusion_matrix(y_train, predict_with_best_t(y_train_prob, best_t))
# Using heatmap to make things more clear.
sns.heatmap(con_m, annot=True, fmt='d',cmap='coolwarm')
plt.title("Train Confusion Matrix")
plt.xlabel("Precicted Label")
plt.ylabel("Actual Label")
plt.show()

best_t = find_best_threshold(test_threshold, test_fpr, test_tpr)
print("Train confusion matrix")
con_m=confusion_matrix(y_test, predict_with_best_t(y_test_prob, best_t))
# Using heatmap to make things more clear.
sns.heatmap(con_m, annot=True, fmt='d',cmap='coolwarm')
plt.title("Test Confusion Matrix")
plt.xlabel("Precicted Label")
plt.ylabel("Actual Label")
plt.show()

predict = predict_with_best_t(y_test_prob,best_t)

fpi = []
for i in range(len(y_test)):
  if (y_test[i]==0) and (predict[i] ==1):
    fpi.append(i)

cols = X_test.columns
false_positive = pd.DataFrame(columns=cols)
false_positive = X_test.iloc[fpi]
len(false_positive)

from wordcloud import WordCloud, STOPWORDS
comment_words = ''
stopwords = set(STOPWORDS)
for word in false_positive['essay']:
  val = str(word)
  tokens = val.split()
  for i in range(len(tokens)):
    tokens[i] = tokens[i].lower()
  comment_words += " ".join(tokens)+" "

wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(comment_words)

plt.figure(figsize=(8,8),)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)

plt.show()

plt.figure(figsize=(8,6))
sns.boxplot('price',data=false_positive,orient="v").set_title("Box plot of price on false positive")
plt.grid()

plt.figure(figsize=(8,6))
counts, bin_edges = np.histogram(false_positive['teacher_number_of_previously_posted_projects'], bins=10, density = True)

pdf = counts/(sum(counts))
plt.plot(bin_edges[1:],pdf,color='blue')
plt.title("teacher number of previously posted of false positive data")
plt.xlabel('teacher number of previously posted projects')

"""## Task - 2

### Implementing Decision Trees on all Non zero features
"""

clf = DecisionTreeClassifier(class_weight='balanced',max_depth=None,min_samples_split=500)

clf.fit(set_1_x_train,y_train)

features = clf.feature_importances_

# assigning all the non zero features to a list.
non_zero_features=[]
for i in range(len(features)):
  if features[i]>0:
    non_zero_features.append(i)

c = set_1_x_train.tocsr()
d = set_1_x_test.tocsr()

x_tr = c[:,non_zero_features]
x_te = d[:,non_zero_features]

dt = DecisionTreeClassifier(class_weight='balanced')
clf = GridSearchCV(dt,parameter,cv=5,scoring='roc_auc',return_train_score=True,)
clf.fit(x_tr,y_train)

print('best_score: ', clf.best_score_)
print('best_parameter: ', clf.best_params_)

import plotly.offline as offline
import plotly as py
import plotly.graph_objs as go
offline.init_notebook_mode()
import numpy as np
import matplotlib.pyplot as plt

x_axis = [5,10,100,500]
y_axis = [1,3,10,30]
z1 = clf.cv_results_['mean_train_score']
z2 = clf.cv_results_['mean_test_score']


trace1 = go.Scatter3d(x=x_axis,y=y_axis,z=z1, name = 'train')
trace2 = go.Scatter3d(x=x_axis,y=y_axis,z=z2, name = 'Cross validation')
data = [trace1, trace2]

layout = go.Layout(scene = dict(
        xaxis = dict(title='min_sample_split'),
        yaxis = dict(title='max_depth'),
        zaxis = dict(title='AUC'),))

fig = go.Figure(data=data, layout=layout)
offline.plot(fig, filename='3d_scatter_colorscale')
fig.show()
plt.show()

dt = DecisionTreeClassifier(class_weight='balanced',max_depth =30, min_samples_split=500 )
dt.fit(x_tr,y_train)
y_train_prob = dt.predict_proba(x_tr)[:,1]
y_test_prob = dt.predict_proba(x_te)[:,1]

train_fpr,train_tpr,train_threshold = roc_curve(y_train,y_train_prob)
test_fpr,test_tpr,test_threshold = roc_curve(y_test,y_test_prob)

plt.figure(figsize=(10,8))
plt.plot(train_fpr,train_tpr,label='train_AUC')
plt.plot(test_fpr,test_tpr,label='train_AUC')
plt.legend()
plt.xlabel("False positive rate")
plt.ylabel("True positive rate")
plt.title('ROC Curve')
plt.grid()
plt.show()

print(auc(test_fpr,test_tpr))

# This will find the threshold to get the confusion_matrix.
def find_best_threshold(threshould, fpr, tpr):
  t = threshould[np.argmax(tpr*(1-fpr))]

  print("the maximum value of tpr*(1-fpr)", max(tpr*(1-fpr)), "for threshold", np.round(t,3))
  return t

def predict_with_best_t(proba, threshould):
  predictions =[]
  for i in proba:
    if i>=threshould:
      predictions.append(1)
    else:
      predictions.append(0)
  return predictions

# importing confusion_matrix.
from sklearn.metrics import confusion_matrix
best_t = find_best_threshold(train_threshold, train_fpr, train_tpr)
print("Train confusion matrix")
con_m=confusion_matrix(y_train, predict_with_best_t(y_train_prob, best_t))
# Using heatmap to make things more clear.
sns.heatmap(con_m, annot=True, fmt='d',cmap='coolwarm')
plt.title("Train Confusion Matrix")
plt.xlabel("Precicted Label")
plt.ylabel("Actual Label")
plt.show()

best_t = find_best_threshold(test_threshold, test_fpr, test_tpr)
print("Train confusion matrix")
con_m=confusion_matrix(y_test, predict_with_best_t(y_test_prob, best_t))
# Using heatmap to make things more clear.
sns.heatmap(con_m, annot=True, fmt='d',cmap='coolwarm')
plt.title("Test Confusion Matrix")
plt.xlabel("Precicted Label")
plt.ylabel("Actual Label")
plt.show()

#Summerizing the work with the help of prettytable.
from prettytable import PrettyTable
mytable = PrettyTable(['Vectorizer','Model','Max Depth','Min Simple Split','AUC'])
mytable.add_row(['TFIDF','Decision Trees','10','500','0.61'])
mytable.add_row(['TFIDF-W2V',"Decision Trees",'10','500','0.54'])
mytable.add_row(['TFIDF on Non-Zero features',"Decision Trees",'10','500','0.61'])
print(mytable)
