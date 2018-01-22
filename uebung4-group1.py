import sys
import argparse
import nltk


minimal_word_occurences=2
ngram_range=(3,6)
minimal_occ_of_word_in_rule=1


def load_gene_list():
    f = open("human-genenames.txt", "r")
    gene_list = []
    for line in f.readlines():
        gene_list.append(line.rstrip())
    f.close()
    return gene_list


def load_stop_words():
    f = open("english_stop_words.txt", "r")
    stop_word_list = []
    for line in f.readlines():
        if line.rstrip() != '':
            stop_word_list.append(line.rstrip())
    f.close()
    return stop_word_list


def load_input_file(input_file):
    f = open(input_file, "r")
    text_list = []
    current_sentence = ""
    pos=0
    for line in f.readlines():
        if line != "\n":
            pos=0
            word, tag = line.split("\t")
            current_sentence = current_sentence + " " + word
        else:
            token = nltk.regexp_tokenize(current_sentence, "[a-zA-Z'`0-9\.%<>=]+")
            pos_tags = nltk.pos_tag(token)
            sentence = ""
            for i in range(0, len(pos_tags)):
                sentence = sentence + " " + pos_tags[i][0] + "/" + pos_tags[i][1] +"/"+str(pos)
                pos+=1
            #print(sentence)
            text_list.append(sentence)
            current_sentence = ""

    if current_sentence != "":
        token = nltk.regexp_tokenize(current_sentence, "[a-zA-Z'`0-9\.%<>=]+")
        pos_tags = nltk.pos_tag(token)
        sentence = ""
        for i in range(0, len(pos_tags)):
            sentence = sentence + " " + pos_tags[i][0] + "/" + pos_tags[i][1] +"/"+str(pos)
            pos+=1
        text_list.append(sentence)

    f.close()
    # print (text_list)
    return text_list

def load_annotated_sentence_list():
    f = open("uebung4-training.iob", "r")
    text_list = []
    current_sentence = ""
    current_iob_tags = []
    for line in f.readlines():
        if line != "\n":
            word, tag = line.split("\t")
            current_sentence = current_sentence + " " + word
            current_tags = current_iob_tags.append(tag.rstrip())
        else:
            token = nltk.regexp_tokenize(current_sentence, "[a-zA-Z'`0-9\.%<>=]+")
            pos_tags = nltk.pos_tag(token)
            sentence = ""
            for i in range(0, len(pos_tags)):
                sentence = sentence + " " + pos_tags[i][0] + "/" + current_iob_tags[i] + "/" + pos_tags[i][1]
            text_list.append(sentence)
            current_iob_tags = []
            current_sentence = ""

    if current_sentence != "":
        token = nltk.regexp_tokenize(current_sentence, "[a-zA-Z'`0-9\.%<>=]+")
        pos_tags = nltk.pos_tag(token)
        sentence = ""
        for i in range(0, len(pos_tags)):
            sentence = sentence + " " + pos_tags[i][0] + "/" + current_iob_tags[i] + "/" + pos_tags[i][1]
        text_list.append(sentence)
        current_iob_tags = []
        current_sentence = ""

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
            #print(word)
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
        if word_count>=minimal_occ_of_word_in_rule:
            rules.append(rule.rstrip())
            print (rule)
    #print(len(rules))
    return rules

def find_Entities_rulebased(sentence, rules):
    #rint("Analyzing sentence \""+sentence+"\"")
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
                        #print (">"+contender,contender_pos+" matches rule \""+rule+"\"")
                        entities.add((contender,contender_pos))
    return entities

def find_Entities_structbased(sentence):
    words = sentence.split(" ")
    entities = set()
    for index, word in enumerate(words):
        conditions_true = 0
        tags = word.split("/")
        try:
            #RAFTK
            if tags[1] == 'NN' or tags[1] == 'NNP' or tags[1] == 'NNS' or tags[1] == 'CD':
                if any(char.isdigit() for char in tags[0]):
                    conditions_true = conditions_true + 1
                if any(char.isupper() for char in tags[0]):
                    if tags[0][0].isupper() and index > 1:
                        conditions_true = conditions_true + 1
                    elif tags[0].isupper():
                        conditions_true = conditions_true + 1
                    elif any(char.isupper() for char in tags[0][1:]):
                        conditions_true = conditions_true + 1
            if conditions_true >= 1:
                entities.add((tags[0], str(index-1)))
        except:
            pass
    return entities

def find_Entities_dictbased(sentence, gene_list):
    words = sentence.split(" ")
    entities = set()

    #test for pos-tags?
    for word in words:
        token = word.split("/")
        if token[0] in gene_list:
            entities.add((token[0], token[2]))

    return entities


def find_Entities(input_file, rules, output_file, gene_list):
    iob_tagged_sentences = []
    for sentence in input_file:
        print (sentence)
        output_sentence = ""
        potential_Entities_by_Rule=find_Entities_rulebased(sentence, rules)
        #print(potential_Entities_by_Rule)
        potential_Entities_by_Struct=find_Entities_structbased(sentence)
        #print(potential_Entities_by_Struct)
        potential_Entities_by_dict=find_Entities_dictbased(sentence, gene_list)
        #print(potential_Entities_by_dict)
        #print("\n")
        #print(potential_Entities_by_Rule)
        #print(potential_Entities_by_Struct)
        #print(potential_Entities_by_dict)
        rule_n_struct = potential_Entities_by_Rule & potential_Entities_by_Struct
        rule_n_dict = potential_Entities_by_Rule & potential_Entities_by_dict
        struct_n_dict = potential_Entities_by_Struct & potential_Entities_by_dict
        possible_proteins = rule_n_struct | rule_n_dict | struct_n_dict
        print(possible_proteins)
        print("\n")
        for word in sentence.split():
            token = word.split("/")
            if (token[0], token[2]) in possible_proteins:
                output_sentence = output_sentence + "\n" + token[0] + "\tB-protein"
            else:
                output_sentence = output_sentence + "\n" + token[0] + "\tO"
        #write_sentence_to_file(output_sentence, output_file)
        iob_tagged_sentences.append(output_sentence+"\n")

    #calc occurences of potential proteins and decide on I or B-protein tag
    
    return iob_tagged_sentences


def write_results_to_file(iob_tagged_input, output_file):
    file = open(output_file, "w")

    iob_tagged_input[0] = iob_tagged_input[0][1:]

    for sent in iob_tagged_input:
        print (sent)
        file.write(sent)

    file.close()

    return


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="input file for annotation")
    parser.add_argument("output_file", help="output file to save results")
    args = parser.parse_args()

    # load gene names
    gene_list = load_gene_list()
    # load stop words
    stop_word_list = load_stop_words()
    # load training file	#input file if
    annotated_sentence_list = load_annotated_sentence_list()
    rules = build_ruleset(annotated_sentence_list, gene_list, stop_word_list)
    annotated_input = load_input_file(args.input_file)
    iob_tagged_input = find_Entities(annotated_input, rules, args.output_file, gene_list)
    write_results_to_file(iob_tagged_input, args.output_file)


if __name__ == '__main__':
    main(sys.argv)
