import numpy as np
import torch
from torch import nn
from torch import optim
from torch.autograd import Variable
from torch.nn import functional as F
from utils import batch_generator
# from utils import nb_classes
# from utils import nb_postags
# from utils import nb_chunktags
from utils import max_sentence_size
# from utils import vec2word
from utils import np2autograd
# from lang_model import CharacterLanguageModel
# from lang_model import embedding_size
# from pos_tag import POSTag
# from chunking import Chunking
# from dependency import Dependency
from sentiment import SentimentClassification
from stance import StanceClassification
from emotion import EmotionClassification
from sklearn.metrics import accuracy_score
# from predict import prediction

# Hyperparams
learning_rate = 1e-3
postag_reg = 1e-3
chunking_reg = 1e-3
sentiment_reg = 1e-3
stance_reg = 1e-3
emotion_reg = 1e-3

class JointMultiTaskModel(nn.Module):
    def __init__(self, mode='all'):
        super(JointMultiTaskModel, self).__init__()

        # models
        # self.lang_model = CharacterLanguageModel()
        # self.postag = POSTag()
        # self.chunking = Chunking()
        # self.dependency = Dependency()
        self.sentiment = SentimentClassification()
        self.stance = StanceClassification()

        self.emotion_anger = EmotionClassification()
        self.emotion_anticipation = EmotionClassification()
        self.emotion_disgust = EmotionClassification()
        self.emotion_fear = EmotionClassification()
        self.emotion_joy = EmotionClassification()
        self.emotion_sadness = EmotionClassification()
        self.emotion_surprise = EmotionClassification()
        self.emotion_trust = EmotionClassification()


        # Mode - all or module_name
        self.mode = mode

    def get_sentiment(self, sentence):
        return self.sentiment(sentence)

    def get_stance(self, sentence):
        return self.stance(sentence)
    
    def get_emotion_anger(self, sentence):
        return self.emotion_anger(sentence)

    def get_emotion_anticipation(self, sentence):
        return self.emotion_anticipation(sentence)
    
    def get_emotion_fear(self, sentence):
        return self.emotion_fear(sentence)
    
    def get_emotion_disgust(self, sentence):
        return self.emotion_disgust(sentence)
    
    def get_emotion_joy(self, sentence):
        return self.emotion_joy(sentence)

    def get_emotion_sadness(self, sentence):
        return self.emotion_sadness(sentence)
    
    def get_emotion_surprise(self, sentence):
        return self.emotion_surprise(sentence)

    def get_emotion_trust(self, sentence):
        return self.emotion_trust(sentence)

    def run_all(self, x):
        # sentence = self.embedded_batch(x)
        # print(x)
        for s in x:
            # print(len(s[0]))
            y_sentiment = self.get_sentiment(s)
            y_stance = self.get_stance(s)
            y_emotion_anger = self.get_emotion_anger(s)
            y_emotion_anticipation = self.get_emotion_anticipation(s)
            y_emotion_disgust = self.get_emotion_disgust(s)
            y_emotion_fear = self.get_emotion_fear(s)
            y_emotion_joy = self.get_emotion_joy(s)
            y_emotion_sadness = self.get_emotion_sadness(s)
            y_emotion_surprise = self.get_emotion_surprise(s)
            y_emotion_trust = self.get_emotion_trust(s)

            yield y_sentiment, y_stance, y_emotion_anger, y_emotion_anticipation, y_emotion_disgust, y_emotion_fear, y_emotion_joy, y_emotion_sadness, y_emotion_surprise, y_emotion_trust

    def forward(self, x):
        # print(len(x))
        out = self.run_all(x)
        # print(out)
        out = list(out)

        return out


    def sentiment_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.sentiment.w.norm() ** 2) * sentiment_reg

        return loss

    def stance_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.stance.w.norm() ** 2) * stance_reg

        return loss
      
    def emotion_anger_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_anger.w.norm() ** 2) * emotion_reg

        return loss
    
    def emotion_anticipation_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_anticipation.w.norm() ** 2) * emotion_reg

        return loss
    
    def emotion_disgust_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_disgust.w.norm() ** 2) * emotion_reg

        return loss
    
    def emotion_fear_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_fear.w.norm() ** 2) * emotion_reg

        return loss

    def emotion_joy_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_joy.w.norm() ** 2) * emotion_reg

        return loss
    
    def emotion_sadness_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_sadness.w.norm() ** 2) * emotion_reg

        return loss
      
    def emotion_surprise_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_surprise.w.norm() ** 2) * emotion_reg

        return loss
    
    def emotion_trust_loss(self, y, yt):
        loss = (yt.float() - y) ** 2 \
               + (self.emotion_trust.w.norm() ** 2) * emotion_reg

        return loss
      
    def loss(self, y, sentiment, stance, anger, anticipation, disgust, fear, joy, sadness, suprise, trust):
        # print("Hi i am in loss")
        losses = []
        # print("Hi i am in loss line 2")
        length = len(y)

        for i in range(length):

            p_sent, r_sent = y[i][0], np2autograd(sentiment[i])
            p_stance, r_stance = y[i][1], np2autograd(stance[i])
            p_anger, r_anger = y[i][2], np2autograd(anger[i])
            p_anticipation, r_anticipation = y[i][3], np2autograd(anticipation[i])
            p_disgust, r_disgust = y[i][4], np2autograd(disgust[i])
            p_fear, r_fear = y[i][5], np2autograd(fear[i])
            p_joy, r_joy = y[i][6], np2autograd(joy[i])
            p_sadness, r_sadness = y[i][7], np2autograd(sadness[i])
            p_surprise, r_surprise = y[i][8], np2autograd(surprise[i])
            p_trust, r_trust = y[i][9], np2autograd(trust[i])


            loss_sent = self.sentiment_loss(p_sent, r_sent)
            loss_stance = self.stance_loss(p_stance, r_stance)
            loss_emotion_anger = self.emotion_anger_loss(p_anger, r_anger)
            loss_emotion_anticipation = self.emotion_anticipation_loss(p_anticipation, r_anticipation)
            loss_emotion_disgust = self.emotion_disgust_loss(p_disgust, r_disgust)
            loss_emotion_fear = self.emotion_disgust_loss(p_fear, r_fear)
            loss_emotion_joy = self.emotion_disgust_loss(p_joy, r_joy)
            loss_emotion_sadness = self.emotion_disgust_loss(p_sadness, r_sadness)
            loss_emotion_surprise = self.emotion_disgust_loss(p_surprise, r_surprise)
            loss_emotion_trust = self.emotion_disgust_loss(p_trust, r_trust)


            loss = loss_sent * 0.1 + loss_stance * 0.1 + loss_emotion_anger * 0.1 + loss_emotion_anticipation * 0.1 + loss_emotion_disgust * 0.1 + loss_emotion_fear * 0.1 + loss_emotion_joy * 0.1 + loss_emotion_sadness * 0.1 + loss_emotion_surprise * 0.1 + loss_emotion_trust * 0.1
            loss = loss/10

            losses.append(loss)

        loss = losses[0]

        for i in range(1, length):
            loss += losses[i]

        loss = loss / length

        return loss

def threshold(prediction, upperBound, lowerBound):
  if prediction >= upperBound:
      prediction = 1
  elif prediction < lowerBound:
      prediction = -1
  else:
      prediction = 0

def compare(out):

    predicted_sent = out[0][0].numpy()[0][0]
    predicted_sent = threshold(predicted_sent, 0.5, 0)

    print(predicted_sent)

    predicted_stance = out[0][1].numpy()[0][0]
    predicted_stance = threshold(predicted_stance, 0.5, 0)

    predicted_emotion_anger = out[0][2].numpy()[0][0]
    predicted_emotion_anger = threshold(predicted_emotion_anger, 0.5, 0)

    predicted_emotion_anticipation = out[0][3].numpy()[0][0]
    predicted_emotion_anticipation = threshold(predicted_emotion_anticipation, 0.5, 0)

    predicted_emotion_disgust = out[0][4].numpy()[0][0]
    predicted_emotion_disgust = threshold(predicted_emotion_disgust, 0.5, 0)

    predicted_emotion_fear = out[0][5].numpy()[0][0]
    predicted_emotion_fear = threshold(predicted_emotion_fear, 0.5, 0)

    predicted_emotion_joy = out[0][6].numpy()[0][0]
    predicted_emotion_joy = threshold(predicted_emotion_joy, 0.5, 0)

    predicted_emotion_sadness = out[0][7].numpy()[0][0]
    predicted_emotion_sadness = threshold(predicted_emotion_sadness, 0.5, 0)

    predicted_emotion_surprise = out[0][8].numpy()[0][0]
    predicted_emotion_surprise = threshold(predicted_emotion_surprise, 0.5, 0)

    predicted_emotion_trust = out[0][9].numpy()[0][0]
    predicted_emotion_trust = threshold(predicted_emotion_trust, 0.5, 0)
    
    return [predicted_sent, predicted_stance, predicted_emotion_anger, predicted_emotion_anticipation, predicted_emotion_disgust, predicted_emotion_fear, predicted_emotion_joy, predicted_emotion_sadness, predicted_emotion_surprise, predicted_emotion_trust]

def accuracy(train_batch_acc, sent_nb_batches, stance_nb_batches, emotion_anger_nb_batches, emotion_anticipation_nb_batches, emotion_disgust_nb_batches, emotion_fear_nb_batches, emotion_joy_nb_batches, emotion_sadness_nb_batches, emotion_surprise_nb_batches, emotion_trust_nb_batches):

  pred_sent = []
  pred_stance = []
  pred_emotion_anger = []
  pred_emotion_anticipation = []
  pred_emotion_disgust = []
  pred_emotion_fear = []
  pred_emotion_joy = []
  pred_emotion_sadness = []
  pred_emotion_surprise = []
  pred_emotion_trust = []

  l = len(train_batch_acc)

  for i in range(l):
    pred_sent.append(train_batch_acc[i][0])
    pred_stance.append(train_batch_acc[i][1])
    pred_emotion_anger.append(train_batch_acc[i][2])
    pred_emotion_anticipation.append(train_batch_acc[i][3])
    pred_emotion_disgust.append(train_batch_acc[i][4])
    pred_emotion_fear.append(train_batch_acc[i][5])
    pred_emotion_joy.append(train_batch_acc[i][6])
    pred_emotion_sadness.append(train_batch_acc[i][7])
    pred_emotion_surprise.append(train_batch_acc[i][8])
    pred_emotion_trust.append(train_batch_acc[i][9])

  print(pred_sent)
  print(sent_nb_batches)
  # print(pred_stance)
  # print(stance_nb_batches)

  sent_acc = accuracy_score(sent_nb_batches, pred_sent)
  stance_acc = accuracy_score(stance_nb_batches, pred_stance)
  anger_acc = accuracy_score(emotion_anger_nb_batches, pred_emotion_anger)
  anticipation_acc = accuracy_score(emotion_anticipation_nb_batches, pred_emotion_anticipation)
  disgust_acc = accuracy_score(emotion_disgust_nb_batches, pred_emotion_disgust)
  fear_acc = accuracy_score(emotion_fear_nb_batches, pred_emotion_fear)
  joy_acc = accuracy_score(emotion_joy_nb_batches, pred_emotion_joy)
  sadness_acc = accuracy_score(emotion_sadness_nb_batches, pred_emotion_sadness)
  surprise_acc = accuracy_score(emotion_surprise_nb_batches, predicted_emotion_surprise)
  trust_acc = accuracy_score(emotion_trust_nb_batches, predicted_emotion_trust)
  
  return(sent_acc, stance_acc, anger_acc, anticipation_acc, disgust_acc, fear_acc, joy_acc, sadness_acc, surprise_acc, trust_acc)


nb_epochs = 5
# batch_size = 47
batch_size = 1
nb_batches = 2914
# 2914

gen = batch_generator(batch_size, nb_batches)

model = JointMultiTaskModel()
adam = optim.Adam(model.parameters(), lr=learning_rate)

train_epoch_acc = []

for epoch in range(nb_epochs):

    train_batch_loss = []
    train_batch_acc = []

    sent_nb_batches = []
    stance_nb_batches = []
    emotion_anger_nb_batches = []
    emotion_anticipation_nb_batches = []
    emotion_disgust_nb_batches = []
    emotion_fear_nb_batches = []
    emotion_joy_nb_batches = []
    emotion_sadness_nb_batches = []
    emotion_surprise_nb_batches = []
    emotion_trust_nb_batches = []

    for batch in range(nb_batches):

        text, sent, stance, anger, anticipation, disgust, fear, joy, sadness, surprise, trust = next(gen)

        sent_nb_batches.append(sent[0][0])
        stance_nb_batches.append(stance[0][0])
        emotion_anger_nb_batches.append(anger[0][0])
        emotion_anticipation_nb_batches.append(anticipation[0][0])
        emotion_disgust_nb_batches.append(disgust[0][0])
        emotion_fear_nb_batches.append(fear[0][0])
        emotion_joy_nb_batches.append(joy[0][0])
        emotion_sadness_nb_batches.append(sadness[0][0])
        emotion_surprise_nb_batches.append(surprise[0][0])
        emotion_trust_nb_batches.append(trust[0][0])
        

        out = model.forward(text)

        loss = model.loss(out, sent, stance, anger, anticipation, disgust, fear, joy, sadness, surprise, trust)
        print("Epoch:", epoch,
              "Batch:", batch,
              "Loss:", loss.data[0])

        adam.zero_grad()
        # loss.backward()
        loss.sum().backward()
        adam.step()
        # print("out", out)
        model.eval() # enter evaluation mode
        with torch.no_grad():
              train_batch_acc.append(compare(out)) # evaluate mini-batch train accuracy in evaluation
    acc = accuracy(train_batch_acc, sent_nb_batches, stance_nb_batches, emotion_anger_nb_batches, emotion_anticipation_nb_batches, emotion_disgust_nb_batches, emotion_fear_nb_batches, emotion_joy_nb_batches, emotion_sadness_nb_batches, emotion_surprise_nb_batches, emotion_trust_nb_batches)
    print("Epoch: ", epoch, "Sentiment Accuracy: ", acc[0], "Stance Accuracy: ", acc[1], "Anger Accuracy: ", acc[2], "Anticipation Accuracy: ", acc[3], "Disgust Accuracy: ", acc[4], "Fear Accuracy: ", acc[5], "Joy Accuracy: ", acc[6], "Sadness Accuracy: ", acc[7], "Suprise Accuracy: ", acc[8], "Trust Accuracy: ", acc[9])


