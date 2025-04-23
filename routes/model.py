from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
from sklearn.preprocessing import LabelEncoder
from flask import Blueprint, request
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path='env/.env') #Access env variables
AIStarPrediction = Blueprint('AIStarPrediction', __name__)

@AIStarPrediction.route('/modelTesting', methods=['POST'])
def useModel():
    text_input = request.get_json().get('reviewContent')
# Load model
    print(os.listdir())
    model = load_model('AIModels/predictStarRatingModel.h5')

    #this is only tokenizing the inputted text: load the tokenizer from training instead
    texts = [text_input]  
    max_words = 10000
    max_len = 200
    tokenizer = Tokenizer(num_words=max_words, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)

    label_encoder = LabelEncoder()
    label_encoder.fit(["1", "2", "3", "4", "5"])  #our possible values

    input_seq = tokenizer.texts_to_sequences(texts)
    input_pad = pad_sequences(input_seq, maxlen=max_len, padding='post')

    pred_probs = model.predict(input_pad)
    pred_rating = np.argmax(pred_probs, axis=1) 
    rounded_rating = label_encoder.inverse_transform(pred_rating)

    
    return rounded_rating[0]