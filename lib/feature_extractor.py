#Write here the feature extractors
# Input: list of tokens (of a sentence)
# Output: list of [(feat_type,value), (feat_type, value) ...


#Unigrams, bigrams an trigrams
def extract_features(list_of_tokens):
    features = []
    for idx, token in enumerate(list_of_tokens):
        #Unigram
        features.append(('unigram',token))
        
        
        #Bigram
        if idx+1 <  len(list_of_tokens):
            bigram = token+'#-#'+list_of_tokens[idx+1]
            features.append(('bigram',bigram))
        
        #Trigrams
        if idx+2 < len(list_of_tokens):
            trigram = token+'#-#'+list_of_tokens[idx+1]+'#-#'+list_of_tokens[idx+2]
            features.append(('trigram',trigram))
        
    return features


if __name__ == '__main__':
    tokens = ['This','is','a','sample','text','with','some','tokens','.']
    print extract_features(tokens)