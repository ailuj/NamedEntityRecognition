import sys
import argparse
import nltk

def load_gene_list():
	f=open("human-genenames.txt","r")
	gene_list=[]
	for line in f.readlines():
		gene_list.append(line.rstrip())
	f.close()
	return gene_list

def load_stop_words():
	f=open("english_stop_words.txt","r")
	stop_word_list=[]
	for line in f.readlines():
		if line.rstrip() != '':	
			stop_word_list.append(line.rstrip())
	f.close()
	return stop_word_list

def load_input_file(input_file):
	f=open(input_file,"r")
	text_list = []
	current_sentence = ""
	for line in f.readlines():
		if line !="\n":
			word, tag=line.split("\t")
			current_sentence=current_sentence+" "+word
		else:
			token=nltk.regexp_tokenize(current_sentence, "[a-zA-Z'`0-9\.%<>=]+")
			pos_tags=nltk.pos_tag(token)
			sentence=""
			for i in range(0, len(pos_tags)):
				sentence=sentence+" "+pos_tags[i][0]+"/"+pos_tags[i][1]
			text_list.append(sentence)
			current_sentence=""
	f.close()
	print (text_list)
	return text_list

def load_annotated_sentence_list():
	f=open("uebung4-training.iob","r")
	text_list=[]
	current_sentence=""
	current_iob_tags=[]
	for line in f.readlines():
		if line !="\n":
			word, tag=line.split("\t")
			current_sentence=current_sentence+" "+word
			current_tags=current_iob_tags.append(tag.rstrip())
		else:
			token=nltk.regexp_tokenize(current_sentence, "[a-zA-Z'`0-9\.%<>=]+")
			pos_tags=nltk.pos_tag(token)
			sentence=""
			for i in range(0, len(pos_tags)):
				sentence=sentence+" "+pos_tags[i][0]+"/"+current_iob_tags[i]+"/"+pos_tags[i][1]
			text_list.append(sentence)
			current_iob_tags=[]
			current_sentence=""
	f.close()
	return text_list

def build_ruleset(annotated_sentence_list, gene_list, stop_word_list):
	gene_stop_word_intersection=[]
	rules=[]
	word_frequencies={}
	total_words=0
	total_ngrams=[]
	for gene in gene_list:
		if gene in stop_word_list:
			gene_stop_word_intersection.append(gene)
	for sentence in annotated_sentence_list:
		#count word frequencies
		if "/B" in sentence:
			annotated_words=sentence.split()
			for annotated_word in annotated_words:
				word=annotated_word.split("/")[0]
				total_words+=1
				if word in word_frequencies:
					cnt=word_frequencies[word]
					word_frequencies[word]=cnt+1
				else:
					word_frequencies[word]=1
		#build ngrams
			for n in range(2,5):
				for ngram in nltk.ngrams(annotated_words,n):
					ngram_String=" ".join(ngram)
					if "/B" in ngram_String:
						total_ngrams.append(ngram_String)
					

	#print (word_frequencies)
	final_frequencies={}
	for word in word_frequencies:
		if word_frequencies[word]!=1 and word not in stop_word_list:
			#print(word)
			final_frequencies[word]=word_frequencies[word]
			#print(final_frequencies)

	for ngram in total_ngrams:
		rule=""
		parts=ngram.split()
		ngram_length=len(ngram)
		tag_count=0
		for part in parts:
			word,iob,tag=part.split("/")
			#print(word,iob,tag)
			if iob=="B-protein":
				rule=rule+" [PROTEIN]"
			elif word in stop_word_list:
				rule=rule+" /"+tag
				tag_count+=1
			elif word in final_frequencies:
				rule=rule+" "+word
			else:
				rule=rule+" /"+tag
				tag_count+=1
		if not tag_count>=ngram_length-1:
			rules.append(rule)								
		#print(rule)
	return rules

def find_Entities_rulebased(sentence, rules):
	return

def find_Entities_structbased(sentence):
	return

def find_Entities_dictbased(sentence):
	return

def find_Entities(input_file, rules):
	for sentence in input_file:
		potential_Entities_by_Rule=find_Entities_rulebased(sentence, rules)
		potential_Entities_by_Struct=find_Entities_structbased(sentence)
		potenital_Entities_by_dict=find_Entities_dictbased(sentence)
		#calc occurences of potential proteins and decide on I or B-protein tag
		#return iob-tagged strings


def main(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument("input_file", help="input file for annotation")
	args = parser.parse_args()

	#load gene names
	gene_list=load_gene_list()
	#load stop words
	stop_word_list=load_stop_words()
	#load training file	#input file if
	annotated_sentence_list=load_annotated_sentence_list()
	rules=build_ruleset(annotated_sentence_list, gene_list, stop_word_list)
	annotated_input=load_input_file(args.input_file)

if __name__ == '__main__':
	main(sys.argv)

