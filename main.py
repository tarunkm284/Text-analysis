import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import re
import nltk
import os

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

punch = string.punctuation

df = pd.read_excel("Input.xlsx")
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
}

# cleaning the text
def clean_text(text):
    non_punch = ''
    for i in text:
        if i not in string.punctuation:
            non_punch += i
    split_text = re.split('\W+',non_punch)
    stop = nltk.corpus.stopwords.words('english')
    wn = nltk.WordNetLemmatizer()
    return " ".join([wn.lemmatize(word).lower() for word in split_text])

# removing the stopwords
def newContent(text):
  newcontent = []
  for item in text.split(" "):
    if item.upper() not in stopWords:
      newcontent.append(item)
  return newcontent

# Count the Syllables
def count_syllables(word):
    word = word.lower()
    counter = 0
    is_previous_vowel = False
    for index, value in enumerate(word):
        if value in ["a", "e", "i", "o", "u", "y"]:
            if index == len(word) - 1:
                if value == "e":
                    if counter == 0:
                        counter += 1
                else:
                    counter += 1
            else:
                if is_previous_vowel == True:
                    counter += 1
                    is_previous_vowel = False
                    break
            is_previous_vowel = True
        else:
            if is_previous_vowel == True:
                counter += 1
            is_previous_vowel = False
    return counter


path = "/StopWords"
dir_list = os.listdir(path)
stopWords = []
for p in dir_list:
  stopWords += open(path+"/"+p,"r", encoding='utf-8').read().split("\n")

output = {
    "URL_ID":[],
    "URL":[],
    "POSITIVE SCORE":[],
    "NEGATIVE SCORE":[],
    "POLARITY SCORE":[],
    "SUBJECTIVITY SCORE":[],
    "AVG SENTENCE LENGTH":[],
    "PERCENTAGE OF COMPLEX WORDS":[],
    "FOG INDEX":[],
    "AVG NUMBER OF WORDS PER SENTENCE":[],
    "COMPLEX WORD COUNT":[],
    "WORD COUNT":[],
    "SYLLABLE PER WORD":[],
    "PERSONAL PRONOUNS":[],
    "AVG WORD LENGTH":[],
}
# Find the variables for the output
index = 0
url_id_list = list(df["URL_ID"])
for url in df["URL"]:
	url_id = url_id_list[index]
	index += 1
	source = requests.get(url, headers=headers).text
	data = BeautifulSoup(source, 'lxml')
	title = data.find("h1",class_="entry-title")
	desc = data.find("div",class_="td-post-content")
	if title is not None:
		title = title.text
	else:
		title = ""
	if desc is not None:
		desc = desc.text
	else:
		desc = ""
	all_text = title+" "+desc
	content = clean_text(all_text)
	newc = newContent(content)
	if len(newc) == 0:
		continue
	pword = open("/MasterDictionary/positive-words.txt","r").read().split("\n")
	nword = open("/MasterDictionary/negative-words.txt","r", encoding='utf-8').read().split("\n")	

	positive_score = 0
	negative_score = 0

	for word in newc:
	  if word.lower() in pword:
	    positive_score += 1
	  if word.lower() in nword:
	    negative_score += 1

	polarity_score = (positive_score - negative_score)/ ((positive_score + negative_score) + 0.000001)
	subjectivity_score = (positive_score + negative_score)/ (len(newc) + 0.000001)
	sentences= nltk.sent_tokenize(" ".join(all_text))

	complex_words = 0
	for word in newc:
	  if count_syllables(word) > 2:
	    complex_words += 1

	percent_complex_Word = (complex_words*100)/len(newc)

	syllables_per_word = complex_words/len(newc)
	average_sentence_length = len(newc)/len(sentences)
	fog_index = 0.4 * (average_sentence_length + complex_words)
	pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b',re.I)
	personal_pronouns = len(pronounRegex.findall(all_text))
	avg_word_len = (len(content)-len(newc))/len(newc)
	
	sents = all_text.split('.')
	avg_sent_len = sum(len(x.split()) for x in sents) / len(sents)

	output["URL_ID"].append(url_id)
	output["URL"].append(url)
	output["POSITIVE SCORE"].append(positive_score)
	output["NEGATIVE SCORE"].append(-negative_score)
	output["POLARITY SCORE"].append(polarity_score)
	output["SUBJECTIVITY SCORE"].append(subjectivity_score)
	output["AVG SENTENCE LENGTH"].append(avg_sent_len)
	output["PERCENTAGE OF COMPLEX WORDS"].append(percent_complex_Word)
	output["FOG INDEX"].append(fog_index)
	output["AVG NUMBER OF WORDS PER SENTENCE"].append(average_sentence_length)
	output["COMPLEX WORD COUNT"].append(complex_words)
	output["WORD COUNT"].append(len(newc))
	output["SYLLABLE PER WORD"].append(syllables_per_word)
	output["PERSONAL PRONOUNS"].append(personal_pronouns)
	output["AVG WORD LENGTH"].append(avg_word_len)
	
output_df = pd.DataFrame(output)
output_df.to_excel("Output_Data_Structure.xlsx")
print("output saved!")