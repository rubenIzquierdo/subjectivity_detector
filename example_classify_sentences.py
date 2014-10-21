#!/usr/bin/env python

from lib.classifier import classify_sentences

if __name__ == '__main__':  
    sentences = []
    sentences.append(['This','is','a','sentence'])
    sentences.append(['This','is','a','very','interesting','sentence'])
    sentences.append(['I','think', 'this','is','a','simple','sentence'])
    sentences.append('Nells Park Hotel'.split())
    my_model = 'hotel_new_models/en'
    svm_values = classify_sentences(sentences,my_model)
    for idx, value in enumerate(svm_values):
        print sentences[idx],value
                                        
                                        