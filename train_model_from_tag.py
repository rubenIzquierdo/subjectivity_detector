#!/usr/bin/env python

import argparse
import sys
import os
import shutil
import glob
import time
import signal

from KafNafParserPy import KafNafParser
from lib.train_classifier import train_classifier_from_folders

                    
VERSION='0.1'


def create_training_sentences(folder_tag_in,folder_kaf_in, opinion_layers,non_opinion,folder_out):
    #Remove the outputfolder if exists and create it again
    if os.path.exists(folder_out):
        shutil.rmtree(folder_out)
    os.mkdir(folder_out)
    total_sents_opi = total_sents_no_opi = 0
        
    for tag_file in glob.glob(os.path.join(folder_tag_in,'*.tag')):
        basename = os.path.basename(tag_file).replace('.tag','')
        kaf_file = os.path.join(folder_kaf_in,basename+'.kaf')
        if os.path.exists(kaf_file):
            ##From the tag file we extract the token ids for opinions and for non opinionated
            opinion_wids = set()        #token ids annotated as opinions
            no_opinion_wids = set()     #token ids annotated as no opinions
            
            fd = open(tag_file,'rb')
            for line in fd:
                fields = line.strip().split('\t')
                wid = fields[0]
                for opinion_idx in opinion_layers:
                    if fields[opinion_idx] == 'Opinion':
                        opinion_wids.add(wid)
                    
                    if non_opinion is not None and fields[non_opinion] == 'NON-OPINIONATED':
                        no_opinion_wids.add(wid)
                        
            fd.close()
            #########
            
            ###
            # Obtain the sentences that are opinionated (positive) and not (negative)
            # The negatives are:
            # If there are non-opinionated:  just the non opinionated
            # If not --> all the rest that are not positive
            #####
            sentences = {}
            all_sent_ids = set()
            sent_for_token_id = {}
            kaf_obj = KafNafParser(kaf_file)
            for token in kaf_obj.get_tokens():
                token_id = token.get_id()
                sent_id = token.get_sent()
                token_value = token.get_text()
                
                if sent_id not in sentences:
                    sentences[sent_id] = []
                sentences[sent_id].append(token_value)
                
                all_sent_ids.add(sent_id)
                
                sent_for_token_id[token_id] = sent_id
            ###
            
            positive_sents = set()
            negative_sents = set()
            
            ##Positive sents are the sentences for the opinion_ids
            for token_id in opinion_wids:
                positive_sents.add(sent_for_token_id[token_id])
            ####
            
            #Negative sents
            if non_opinion is not None:
                #In this case the negative are just the sentence of the no_opinion_wids
                for token_id in no_opinion_wids:
                    negative_sents.add(sent_for_token_id[token_id])
            else:
                #In this case the negative are all the sentences but the positive ones
                negative_sents = all_sent_ids - positive_sents
                
            #Free some memory    
            del opinion_wids
            del no_opinion_wids
            del kaf_obj
            
            ##Store the results in the file
            output_file = os.path.join(folder_out,basename+'.sents')
            fd_out = open(output_file,'w')
            fd_out.write('#'+tag_file+'\n')
            for sent_id in sorted(list(positive_sents)):
                text = ' '.join(sentences[sent_id])
                fd_out.write('+ '+text.encode('utf-8')+'\n')
                
            for sent_id in sorted(list(negative_sents)):
                text = ' '.join(sentences[sent_id])
                fd_out.write('- '+text.encode('utf-8')+'\n')
            fd_out.close()
            
            #print 'Processed ',basename
            #print '   Subjective sents:',len(positive_sents)
            #print '   Non subje. sents:',len(negative_sents)
            total_sents_opi += len(positive_sents)
            total_sents_no_opi += len(negative_sents)
        else:
            print 'KAF FILE NOT FOUND',kaf_file
    return total_sents_opi, total_sents_no_opi
    
            
        
        
    
    
    
    
if __name__ == '__main__':
    lang = 'fr'
    hotel_en = ('/home/izquierdo/data/opinion_annotations_en/tag/hotel','/home/izquierdo/data/opinion_annotations_en/kaf/hotel',[7], None,'hotel_en')
    news_en  = ('/home/izquierdo/data/opinion_annotations_en/tag/news' ,'/home/izquierdo/data/opinion_annotations_en/kaf/news',[7,11],13,'news_en')    
    
    hotel_nl = ('/home/izquierdo/data/opinion_annotations_nl/tag/hotel','/home/izquierdo/data/opinion_annotations_nl/kaf/hotel',[7], None,'hotel_nl')
    news_nl  = ('/home/izquierdo/data/opinion_annotations_nl/tag/news' ,'/home/izquierdo/data/opinion_annotations_nl/kaf/news',[7,11],13,'news_nl')

    hotel_de = ('/home/izquierdo/data/opinion_annotations_de/tag/hotel','/home/izquierdo/data/opinion_annotations_de/kaf/hotel',[7], None,'hotel_de')
    news_de  = ('/home/izquierdo/data/opinion_annotations_de/tag/news' ,'/home/izquierdo/data/opinion_annotations_de/kaf/news',[7,11],13,'news_de')

    hotel_fr = ('/home/izquierdo/data/opinion_annotations_fr/tag/hotel','/home/izquierdo/data/opinion_annotations_fr/kaf/hotel',[7], None,'hotel_fr')
    news_fr  = ('/home/izquierdo/data/opinion_annotations_fr/tag/news' ,'/home/izquierdo/data/opinion_annotations_fr/kaf/news',[7,11],13,'news_fr')


    process_these = []
    output_folder = None
    if lang == 'en':
        process_these.append(hotel_en)
        process_these.append(news_en)
        output_folder = 'my_classifier_en'
    elif lang == 'nl':
        process_these.append(hotel_nl)
        process_these.append(news_nl)
        output_folder = 'my_classifier_nl'
    elif lang == 'de':
        process_these.append(hotel_de)
        process_these.append(news_de)
        output_folder = 'my_classifier_de'
    elif lang == 'fr':
        process_these.append(hotel_fr)
        process_these.append(news_fr)
        output_folder = 'my_classifier_fr'        
            
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

   
    training_folders = []
    total_sents_opi = total_sents_no_opi = 0 
    for folder_tag_in, folder_kaf_in, opinion_layers, non_opinion, sub_folder_out in process_these:
        
        this_pid = os.fork()
        if this_pid == 0:
            print 'Converting KAF/TAG files to the internal format',sub_folder_out,' ',
            while True:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
        else:      
            complete_out_folder = os.path.join(output_folder,sub_folder_out)
            num_sents_opi, num_sents_no_opi = create_training_sentences(folder_tag_in,folder_kaf_in, opinion_layers, non_opinion, complete_out_folder)
            total_sents_opi += num_sents_opi
            total_sents_no_opi += num_sents_no_opi
            training_folders.append(complete_out_folder)
            os.kill(this_pid,signal.SIGKILL)
    
        print
        print '  Processed dataset',sub_folder_out
        print '    Opinionated sentences:',num_sents_opi
        print '    No opinionated sentences:',num_sents_no_opi
        
    print
    print '#'*50 
    print 'Num datasets processed:',len(process_these)
    print '  Opinionated sentences:',total_sents_opi
    print '  No opinionated sentences:',total_sents_no_opi
    print '#'*50    
    
    #Train with the folders in training_folders
    train_classifier_from_folders(training_folders,os.path.join(output_folder,'model'))
     
      
  