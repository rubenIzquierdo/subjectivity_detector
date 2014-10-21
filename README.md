#Subjectivy Detector#

This software implements a subjectivy detector at sentence level based on Support Vector Machines and a basic model with unigrams, bigrams and trigrams.
There are two basic options: training your own models and assigning subjectivity values to sentences.

Requirements:
* SVMLight library
* KafNafParser
* VUA_pylib

##Installation##

You will need to follow these basic steps:

1. Clone in a path where python can find the library KafNafPaser (https://github.com/opener-project/KafNafParserPy)
2. Clone in a path where python can find the library VUA_pylib (https://github.com/opener-project/VUA_pylib)
3. Install SVMLigh following the instructions at http://svmlight.joachims.org/
4. Clone this repository
5. Modify the file `lib/path_finder.py` to point to the SVMLight executables in your local installation

##Training your own models##

You will need to provide a set of TAG+KAF files with examples of sentences with opinions (subjective) and without opinions. You will need
to modify the script `train_model_from_tag.py` to indicate which are the data sets you want to use for trainind (it could be more than one).
For instance you could indicate:
````shell
    hotel_en = ('/home/izquierdo/data/opinion_annotations_en/tag/hotel','/home/izquierdo/data/opinion_annotations_en/kaf/hotel',[7], None,'hotel_en')
    news_en  = ('/home/izquierdo/data/opinion_annotations_en/tag/news' ,'/home/izquierdo/data/opinion_annotations_en/kaf/news',[7,11],13,'news_en')
    process_these.append(hotel_en)
    process_these.append(news_en)
    output_folder = 'my_classifier_en'
````

With the first 2 lines you indicate the datasets, you add them to the list of datasets and provide the name of the output folder. The format of each
dataset is a tuple with 5 fields:
* The path to the TAG files
* The path to the KAF files
* A list of numbers indicating which layers contain the opinion annotations in the TAG files
* The number of layer which contains non-opinionated annotations (None) else
* The name of the subfolder where the training instances will be stored

Then you just need to run the script `train_model_from_tag.py` and the training process will begin. The resulting folder stores the models that must be used
for tagging new sentences.

##Detecting subjective sentences##

When you have your trained models or you used the models pre-trained, you can make use of this tool for assigning subjectivity values to sentences. 
The main function is classify_sentences, on the `lib/classifier.py` file. In the main root folder there is an example script `example_classify_sentences.py` which shows the usage:
```shell
    sentences = []
    sentences.append(['This','is','a','sentence'])
    sentences.append(['This','is','a','very','interesting','sentence'])
    sentences.append(['I','think', 'this','is','a','simple','sentence'])
    sentences.append('Nells Park Hotel'.split())
    svm_values = classify_sentences(sentences,'/home/izquierdo/mybitbucket/subjectivity_detector/my_classifier/model')
    for idx, value in enumerate(svm_values):
        print sentences[idx],value
```

And this will generate:
```shell
['This', 'is', 'a', 'sentence'] 0.32386576
['This', 'is', 'a', 'very', 'interesting', 'sentence'] 0.53049329
['I', 'think', 'this', 'is', 'a', 'simple', 'sentence'] 0.77534662
['Nells', 'Park', 'Hotel'] -1.0001291
```

You can import the classify_sentences in your python script and use it in this same fashion. This function takes as input 2 parameters:

* A list of sentences, where every sentence is a list of tokens
* The path to the folder with the models

It returns a list of values, one for each sentence, indicating the degree of subjetivity of each sentence. The higher the value is, the more likely
the sentence is expected to be subjective (contain opinions).

##Contact##
* Ruben Izquierdo
* Vrije University of Amsterdam 
* ruben.izquierdobevia@vu.nl
