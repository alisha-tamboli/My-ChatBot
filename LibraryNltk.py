import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk import pos_tag
from nltk import ne_chunk
from nltk.stem import WordNetLemmatizer


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# function to preprocess user input
def preprocess_user_input(user_input):
    # Tokenize input into words
    tokens = word_tokenize(user_input.lower())
    return tokens

def tokenize_user_input(user_input):
    return word_tokenize(user_input.lower())


def tag_user_input(user_input):
    tokens = tokenize_user_input(user_input)
    return pos_tag(tokens)
  
def named_entity_recognition(user_input):
    tokens = tokenize_user_input(user_input)
    pos_tags = pos_tag(tokens)
    return ne_chunk(pos_tags)

def lemmatize_user_input(user_input):
    lemmatizer = WordNetLemmatizer()
    tokens = tokenize_user_input(user_input)
    lemmas = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmas
