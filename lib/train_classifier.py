#!/usr/bin/env python

import os
import sys
import time
import glob
import shutil
import signal
from subprocess import Popen, PIPE

from VUA_pylib.io import * 
from feature_extractor import extract_features
from path_finder import find_svmlight_learn


###################################
__name_feature = 'sentences.feat'
__name_training= 'sentences.train'
__name_index = 'index_features.idx'
__name_model = 'model.svm'
##################################

def write_to_output(my_class,feats, output):
    my_str = my_class
    for name, value in feats:
        my_str += '\t'+name+'='+value
    output.write(my_str.encode('utf-8')+'\n')
    
    
def run_svmlight_learn(example_file,model_file,params):
    svmlight = find_svmlight_learn()
    
    if not os.path.exists(svmlight):
        print>>sys.stderr,'SVMlight learn not found on',svmlight
        sys.exit(-1)
    
    this_pid = os.fork()
    if this_pid == 0:
        print 'Training and optimizing model',
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
    else:
    
        cmd = [svmlight]
        cmd.append(params)
        cmd.append(example_file)
        cmd.append(model_file)
        err_file = model_file+'.log'
        err_fic = open(err_file,'w')
        svm_process = Popen(' '.join(cmd),stdin=PIPE, stdout=err_fic, stderr=PIPE, shell=True)
        svm_process.wait()
        os.kill(this_pid,signal.SIGKILL)
        str_err = svm_process.stderr.read()
        if len(str_err) != 0:
            print>>sys.stderr,'SVM light error '+str_err
            sys.exit(-1)
        err_fic.close()
    
    
def train_classifier_from_folders(list_folders,output_folder):
    #Create the training feature file with format:
    #CLASS label FEAT FEAT FEAT
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    
    features_folder = os.path.join(output_folder,'features')
    os.mkdir(features_folder)
    
    feature_filename = os.path.join(output_folder,__name_feature)
    fd_feats = open(feature_filename,'w')
    for f in list_folders:    
        this_pid = os.fork()
        if this_pid == 0:
            print 'Extracting features from',f,' '
            while True:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
        else:
            #For each sent file
            for sent_file in glob.glob(os.path.join(f,'*.sents')):
                fin = open(sent_file,'r')
                for line in fin:
                    fields = line.decode('utf-8').strip().split(' ')
                    class_label = fields[0]
                    ##Conver + - o +1 -1
                    if class_label[0]=='+': class_label='+1'
                    elif class_label[0]=='-': class_label='-1'
                    tokens = fields[1:]
                    these_feats = extract_features(tokens)
                    write_to_output(class_label, these_feats, fd_feats)
                fin.close()
            ##Done
            os.kill(this_pid,signal.SIGTERM)
            print
    fd_feats.close()
    print 'Feature file:',feature_filename
    
    ##Convert this features file in the index file
    training_filename = os.path.join(output_folder,__name_training)
    fd_train = open(training_filename,'w')

    
    feature_file_obj = Cfeature_file(feature_filename)
    index_features = Cfeature_index()
    index_features.encode_feature_file_to_svm(feature_file_obj,out_fic=fd_train)
    print 'Training instances saved to ',training_filename
    fd_train.close()
    
    #Save the index of features that will be used for the classification
    index_filename = os.path.join(output_folder,__name_index )
    index_features.save_to_file(index_filename)
    print 'Index of features saved to',index_filename
    
    #Train the model using the file training_filename
    model_filename = os.path.join(output_folder,__name_model)
    params = '-c 0.5 -x 1'
    run_svmlight_learn(training_filename,model_filename,params)
    print 'Model trained and saved to',model_filename

        
    

            
    

        