#!/usr/bin/env

import os
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE

from VUA_pylib.io import * 
from feature_extractor import extract_features
from path_finder import find_svmlight_classify


###################################
__name_index = 'index_features.idx'
__name_model = 'model.svm'
##################################


def run_svm_classify(example_file,model_file):
    #usage: svm_classify [options] example_file model_file output_file
    svmlight = find_svmlight_classify()
    if not os.path.exists(svmlight):
        print>>sys.stderr,'SVMlight learn not found on',svmlight
        sys.exit(-1)
                                                    
    cmd = [svmlight]
    cmd.append(example_file)
    cmd.append(model_file)
    tempout = NamedTemporaryFile(delete=False)
    tempout.close()
    
    cmd.append(tempout.name)
    svm_process = Popen(' '.join(cmd),stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    svm_process.wait()
    str_err = svm_process.stderr.read()
    if len(str_err) != 0:
        print>>sys.stderr,'SVM light classify error '+str_err
        sys.exit(-1)
    #logging.debug('SVMlight classigfy log'+err_file)
    results = []
    fout = open(tempout.name,'r')
    for line in fout:
        results.append(float(line.strip()))
    fout.close()
    os.remove(tempout.name)
    return results


def classify_sentences(list_of_sentences,model_folder):
    #Create feature file
    index_features_filename = os.path.join(model_folder,__name_index)
    model_filename = os.path.join(model_folder,__name_model)
    
    feature_index = Cfeature_index()
    feature_index.load_from_file(index_features_filename)
    
    ################################################
    #Create the feature file for classification
    ################################################
    my_feat_file = NamedTemporaryFile(delete=False)
    for list_of_tokens in list_of_sentences:
        these_feats = extract_features(list_of_tokens)
        feature_index.encode_example_for_classification(these_feats,my_feat_file)   
    my_feat_file.close()
    ################################################
    
    #Run the classifier svm_clasify
    #SVM values will be a list of floats, one per sentence, with the value associated by SVM
    svm_values = run_svm_classify(my_feat_file.name,model_filename)
    
    os.remove(my_feat_file.name)
    return svm_values


if __name__ == '__main__':
    sentences = []
    sentences.append(['This','is','a','sentence'])
    sentences.append(['This','is','a','very','interesting','sentence'])
    sentences.append(['I','think', 'this','is','a','simple','sentence'])
    sentences.append('Nells Park Hotel'.split())
    svm_values = classify_sentences(sentences,'/home/izquierdo/mybitbucket/subjectivity_detector/my_classifier/model')
    for idx, value in enumerate(svm_values):
        print sentences[idx],value
    
    
