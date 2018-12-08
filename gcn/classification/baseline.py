import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from tensorflow.python import keras as K
from gcn.util import gpu_enable


class TfidfClassifier():

    def __init__(self, max_df=1.0, min_df=1, vocabulary=None):
        self.vectorizer = TfidfVectorizer(max_df=max_df, min_df=min_df,
                                          vocabulary=vocabulary)
        self.classifier = LogisticRegression(penalty="l1", solver="liblinear",
                                             multi_class="ovr")
        self.model = Pipeline([("vectorizer", self.vectorizer),
                               ("classifier", self.classifier)])

    def fit(self, x, y, cv=5):
        scores = cross_val_score(self.model, x, y, cv=cv, scoring="f1_micro")
        self.model.fit(x, y)
        return scores

    def predict(self, x):
        return self.model.predict(x)

    def predict_proba(self, x):
        return self.model.predict_proba(x)


class LSTMClassifier():

    def __init__(self, vocab_size, embedding_size=100, hidden_size=100,
                 layers=1, dropout=0.5):

        self.vocab_size = vocab_size
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        self.layers = layers
        self.dropout = dropout
        self.model = None

    def build(self, num_classes, preprocessor=None):
        self.preprocessor = preprocessor
        model = K.Sequential()
        embedding = K.layers.Embedding(input_dim=self.vocab_size,
                                       output_dim=self.embedding_size,
                                       embeddings_regularizer=K.regularizers.l2(),
                                       name="embedding")
        model.add(embedding)
        model.add(K.layers.Dropout(self.dropout))
        for layer in range(self.layers):
            model.add(K.layers.LSTM(self.hidden_size))

        model.add(K.layers.Dropout(self.dropout))
        model.add(K.layers.Dense(num_classes, activation="softmax"))

        self.model = model

    def predict(self, x):
        preds = self.predict_proba(x)
        return np.argmax(preds, axis=1)

    def predict_proba(self, x):
        _x = x if self.preprocessor is None else self.preprocessor(x)
        return self.model.predict(_x)
