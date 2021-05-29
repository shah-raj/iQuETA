class ObjectiveTest:
    pass
#
#
# # Import packages
# from summarizer import Summarizer
# import re, nltk
# import numpy as np
# from nltk.corpus import wordnet as wn
# from flask_app import app, db, bcrypt, mail, google, REDIRECT_URI, currentUserType
# from flask_app.models import Questions,Test
#
# import PyPDF2, pprint, itertools
# import pke, string, joblib
# from nltk.corpus import stopwords
# from nltk.tokenize import sent_tokenize
#
# from flashtext import KeywordProcessor
# import requests, json, random
# from pywsd.lesk import adapted_lesk
# from pywsd.lesk import simple_lesk
# from pywsd.lesk import cosine_lesk
# from pywsd.similarity import max_similarity
# import bz2, pickle
# import _pickle as cPickle
#
# from io import StringIO
#
# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
# from pdfminer.pdfdocument import PDFDocument
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.pdfpage import PDFPage
# from pdfminer.pdfparser import PDFParser
#
# full_text=''
# summarized_text=''
#
# def full_pickle(title, data):
#     pikd = open(title + '.pickle', 'wb')
#     pickle.dump(data, pikd)
#     pikd.close()
# def loosen(file):
#     pikd = open(file, 'rb')
#     data = pickle.load(pikd)
#     pikd.close()
#     return data
# # def compressed_pickle(title, data):
# #     with bz2.BZ2File(title + '.pbz2', 'w') as f:
# #         cPickle.dump(data, f)
# # def decompress_pickle(file):
# #     data = bz2.BZ2File(file, 'rb')
# #     data = cPickle.load(data)
# #     return data
# class ObjectiveTest:
#     """Class abstraction for objective test generation module
#     """
#
#
#
#     def __init__(self,filepath):
#         """Class constructor
#
#         Arguments:
#             filepath {str} -- Absolute path to the corpus file
#         """
#         try:
#
#             if filepath[-3:].lower()=='pdf':
#                 # print("Haa andar")
#                 # pdfFileObject = open(filepath, 'rb')
#                 # print("File name is:",filepath)
#
#
#                 # pdfReader = PyPDF2.PdfFileReader(pdfFileObject)
#                 # pageObject = pdfReader.getPage(1)
#                 # # self.full_text=pageObject.extractText()
#                 # print('full text',full_text)
#                 # print('page obj',pageObject.extractText())
#                 # pdfFileObject.close()
#                 output_string = StringIO()
#                 with open(filepath, 'rb') as in_file:
#                     # print(filepath)
#                     parser = PDFParser(in_file)
#                     doc = PDFDocument(parser)
#                     rsrcmgr = PDFResourceManager()
#                     device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#                     interpreter = PDFPageInterpreter(rsrcmgr, device)
#                     for page in PDFPage.create_pages(doc):
#                         interpreter.process_page(page)
#
#                 self.full_text=output_string.getvalue()
#             elif filepath[-3:].lower()=='txt':
#                 with open(filepath, mode="r", encoding="utf8") as fp:
#                     self.full_text = fp.read()
#             model = Summarizer()
#             # train_model = 'iqueta.sav'
#             # joblib.dump(model, train_model)
#             # model = joblib.load("iqueta.sav")
#
#             # with open('model_pickle','wb') as f:
#             #     pickle.dump(model,f)
#
#
#             # full_pickle('new', model)
#             # model = loosen('new.pickle')
#             # compressed_pickle('new1', model)
#             # model = decompress_pickle('new1.pbz2')
#
#             # with open('model_pickle','rb') as f:
#             #     model = pickle.load(f)
#
#             result = model(self.full_text, min_length=60, max_length = 500 , ratio = 0.4)
#             self.summarized_text = ''.join(result)
#             print (self.summarized_text)
#         except FileNotFoundError as e:
#             print("Warning raised at `ObjectiveTest.__init__`", e)
#
#
#
#     def get_nouns_multipartite(self,text):
#         out=[]
#
#         extractor = pke.unsupervised.MultipartiteRank()
#         extractor.load_document(input=text)
#         #    not contain punctuation marks or stopwords as candidates.
#         pos = {'PROPN'}
#         #pos = {'VERB', 'ADJ', 'NOUN'}
#         stoplist = list(string.punctuation)
#         stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
#         stoplist += stopwords.words('english')
#         extractor.candidate_selection(pos=pos, stoplist=stoplist)
#         # 4. build the Multipartite graph and rank candidates using random walk,
#         #    alpha controls the weight adjustment mechanism, see TopicRank for
#         #    threshold/method parameters.
#         extractor.candidate_weighting(alpha=1.1,
#                                       threshold=0.75,
#                                       method='average')
#         keyphrases = extractor.get_n_best(n=20)
#
#         for key in keyphrases:
#             out.append(key[0])
#         return out
#
#
#     def tokenize_sentences(self,text):
#         sentences = [sent_tokenize(text)]
#         sentences = [y for x in sentences for y in x]
#         # Remove any short sentences less than 20 letters.
#         sentences = [sentence.strip() for sentence in sentences if len(sentence) > 20]
#         return sentences
#
#     def get_sentences_for_keyword(self,keywords, sentences):
#         keyword_processor = KeywordProcessor()
#         keyword_sentences = {}
#         for word in keywords:
#             keyword_sentences[word] = []
#             keyword_processor.add_keyword(word)
#         for sentence in sentences:
#             keywords_found = keyword_processor.extract_keywords(sentence)
#             for key in keywords_found:
#                 keyword_sentences[key].append(sentence)
#
#         for key in keyword_sentences.keys():
#             values = keyword_sentences[key]
#             values = sorted(values, key=len, reverse=True)
#             keyword_sentences[key] = values
#         return keyword_sentences
#
#
#     def get_distractors_wordnet(self,syn,word):
#         # print(word)
#         distractors=[]
#         word= word.lower()
#         orig_word = word
#         if len(word.split())>0:
#             word = word.replace(" ","_")
#         hypernym = syn.hypernyms()
#         if len(hypernym) == 0:
#             return distractors
#         for item in hypernym[0].hyponyms():
#             name = item.lemmas()[0].name()
#             #print ("name ",name, " word",orig_word)
#             if name == orig_word:
#                 continue
#             name = name.replace("_"," ")
#             name = " ".join(w.capitalize() for w in name.split())
#             if name is not None and name not in distractors:
#                 distractors.append(name)
#         return distractors
#
#     def get_wordsense(self,sent,word):
#         word= word.lower()
#
#         if len(word.split())>0:
#             word = word.replace(" ","_")
#
#
#         synsets = wn.synsets(word,'n')
#         if synsets:
#             wup = max_similarity(sent, word, 'wup', pos='n')
#             adapted_lesk_output =  adapted_lesk(sent, word, pos='n')
#             lowest_index = min (synsets.index(wup),synsets.index(adapted_lesk_output))
#             return synsets[lowest_index]
#         else:
#             return None
#
# # Distractors from http://conceptnet.io/
#     def get_distractors_conceptnet(self,word):
#         word = word.lower()
#         original_word= word
#         if (len(word.split())>0):
#             word = word.replace(" ","_")
#         distractor_list = []
#         url = "http://api.conceptnet.io/query?node=/c/en/%s/n&rel=/r/PartOf&start=/c/en/%s&limit=5"%(word,word)
#         obj = requests.get(url).json()
#
#         for edge in obj['edges']:
#             link = edge['end']['term']
#
#             url2 = "http://api.conceptnet.io/query?node=%s&rel=/r/PartOf&end=%s&limit=10"%(link,link)
#             obj2 = requests.get(url2).json()
#             for edge in obj2['edges']:
#                 word2 = edge['start']['label']
#                 if word2 not in distractor_list and original_word.lower() not in word2.lower():
#                     distractor_list.append(word2)
#
#         return distractor_list
#
#
#     def generate_test(self):
#
#         """Method to generate an objective test i.e., a set of questions and required options for answer.
#
#         Arguments:
#             num_of_questions {int} -- Integer denoting number of questions to set in the test.
#
#         Returns:
#             list, list -- A pair of lists containing questions and answer options respectively.
#         """
#
#         question = list()
#         answer = list()
#         mcq = list() #other options
#
#         key_distractor_list = {}
#         keywords = self.get_nouns_multipartite(self.full_text)
#         # print(keywords)
#         filtered_keys=[]
#         for keyword in keywords:
#             if keyword.lower() in self.summarized_text.lower():
#                 filtered_keys.append(keyword)
#         # print(filtered_keys)
#         sentences = self.tokenize_sentences(self.summarized_text)
#         keyword_sentence_mapping = self.get_sentences_for_keyword(filtered_keys, sentences)
#         # print(keyword_sentence_mapping)
#
#         for keyword in keyword_sentence_mapping:
#             # print('keyword',keyword_sentence_mapping[keyword])
#             if keyword_sentence_mapping[keyword] == []:
#                 continue
#             wordsense = self.get_wordsense(keyword_sentence_mapping[keyword][0],keyword)
#             if wordsense:
#                 distractors = self.get_distractors_wordnet(wordsense,keyword)
#                 if len(distractors) ==0:
#                     distractors = self.get_distractors_conceptnet(keyword)
#                 if len(distractors) != 0:
#                     key_distractor_list[keyword] = distractors
#             else:
#
#                 distractors = self.get_distractors_conceptnet(keyword)
#                 if len(distractors) != 0:
#                     key_distractor_list[keyword] = distractors
#
#         # index = 1
#         # print ("#############################################################################")
#         # print ("NOTE::::::::  Since the algorithm might have errors along the way, wrong answer choices generated might not be correct for some questions. ")
#         # print ("#############################################################################\n\n")
#         for each in key_distractor_list:
#             # print("Last wala loop",each)
#             sentence = keyword_sentence_mapping[each][0]
#             pattern = re.compile(each, re.IGNORECASE)
#             output = pattern.sub( " _______ ", sentence)
#             # print ("%s)"%(index),output)
#             question.append(output)
#             choices = [each.capitalize()] + key_distractor_list[each]
#             if len(choices)>=4:
#                 top4choices = choices[:4]
#             else:
#                 top4choices = []
#                 for i in choices:
#                     top4choices.append(i)
#                 for i in range(len(top4choices),4):
#                     top4choices.append('')
#             mcq.append(top4choices[1:])
#             random.shuffle(top4choices)
#             # print(top4choices)
#             answer.append(each.capitalize())
#             # optionchoices = ['a','b','c','d']
#             # tids=Test.query.with_entities(Test.id).all()
#             # tot=[]
#             # for a in tids:
#             #     tot.append(a[0])
#             # print("The test ids are:",tot)
#             # for idx,choice in enumerate(top4choices):
#             #     print ("\t",optionchoices[idx],")"," ",choice)
#             # result=Questions(question_text=output,test_id=tot[-1],ans=each.capitalize(),op1=top4choices[0],op2=top4choices[1],op3=top4choices[2],op4=top4choices[3])
#             # db.session.add(result)
#             # db.session.commit()
#             # print ("\nMore options: ", choices[4:20],"\n\n")
#             # index = index + 1
#         return question,answer,mcq
