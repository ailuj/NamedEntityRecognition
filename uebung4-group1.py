import sys
import argparse
import nltk

#TODO ruleset normalization, remove ".", remove unspecific rules, remove single protein rules
#TODO named entity recognition methods
#TODO write results to file

minimal_word_occurences=1
ngram_range=(4,8)
minimal_occ_of_word_in_rule=2


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
				sentence=sentence+" "+pos_tags[i][0]+"/"+pos_tags[i][1]+"/"+str(i)
			text_list.append(sentence)
			current_sentence=""
	f.close()
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
			for n in range(ngram_range[0],ngram_range[1]):
				for ngram in nltk.ngrams(annotated_words,n):
					ngram_String=" ".join(ngram)
					if "/B" in ngram_String:
						occurences=ngram_String.count("/B")

						#if multiple B in ngram, then adapt ngram, so only one protein is considered
						if occurences>=2:
							for i in range (0, occurences):
								copy_ngram=ngram
								b_counter=0
								final_ngram=""
								for word in copy_ngram:
									if "/B" in word:
										if b_counter==i:
											word.replace("/B","/O")
										final_ngram=" "+word
								total_ngrams.append(final_ngram)
						else:
							total_ngrams.append(ngram_String)

	#print (word_frequencies)
	final_frequencies={}
	for word in word_frequencies:
		if word_frequencies[word]>=minimal_word_occurences and word not in stop_word_list:
			#print(word)n
			final_frequencies[word]=word_frequencies[word]

	for ngram in total_ngrams:
		rule=""
		parts=ngram.split()
		ngram_length=len(parts)
		tag_count=0
		word_count=0
		for part in parts:
			word,iob,tag=part.split("/")
			#print(word,iob,tag)
			if iob=="B-protein":
				rule=rule+" [PROTEIN]"
				tag_count+=1
			elif word in stop_word_list:
				rule=rule+" /"+tag
				tag_count+=1
			elif "." in tag:
				tag_count+=1
			elif word in final_frequencies:
				word_count+=1
				rule=rule+" "+word
			else:
				rule=rule+" /"+tag
				tag_count+=1
		if tag_count<len(parts) and word_count>minimal_occ_of_word_in_rule:
			rules.append(rule.rstrip())
			#print (rule)
	#print(len(rules))
	return rules

def find_Entities_rulebased(sentence, rules):
	print("Analyzing sentence \""+sentence+"\"")
	entities=set()
	for n in range(ngram_range[0],ngram_range[1]):
		for ngram in nltk.ngrams(sentence.rsplit(), n):
			for rule in rules:
				rule_parts=rule.split()
				if len(ngram)==len(rule_parts):
					match=True
					contender=""
					contender_pos=0
					for i in range (0,len(ngram)):
						#print (ngram[i])
						ngram_word,ngram_tag,pos=ngram[i].split("/")
						if "/" in rule_parts[i]:
							if "/"+ngram_tag!=rule_parts[i]:
								match=False
						elif "[PROTEIN]" in rule_parts[i]:
							if "." in ngram_tag:
								match=False
							else:
								contender_pos=pos
								contender=ngram_word
						elif ngram_word!=rule_parts[i]:
							match=False
					if match==True:
						print (">"+contender,contender_pos+" matches rule \""+rule+"\"")
						entities.add((contender,contender_pos))
	return entities

def find_Entities_structbased(sentence):
	return

def find_Entities_dictbased(sentence):
	return

def find_Entities(input_file, rules):
	for sentence in input_file:
		potential_Entities_by_Rule=find_Entities_rulebased(sentence, rules)
		potential_Entities_by_Struct=find_Entities_structbased(sentence)
		potenital_Entities_by_dict=find_Entities_dictbased(sentence)
		print(potential_Entities_by_Rule)
		#calc occurences of potential proteins and decide on I or B-protein tag
		#return iob-tagged strings

def write_results_to_file(iob_tagged_input, input_file):
	return

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
	iob_tagged_input=find_Entities(annotated_input,rules)
	write_results_to_file(iob_tagged_input, args.input_file)

if __name__ == '__main__':
	main(sys.argv)

