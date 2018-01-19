import sys
import argparse
import nltk


# TODO ruleset normalization, remove ".", remove unspecific rules, remove single protein rules
# TODO named entity recognition methods
# TODO write results to file

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
    for line in f.readlines():
        if line != "\n":
            word, tag = line.split("\t")
            current_sentence = current_sentence + " " + word
        else:
            token = nltk.regexp_tokenize(current_sentence, "[a-zA-Z'`0-9\.%<>=]+")
            pos_tags = nltk.pos_tag(token)
            sentence = ""
            for i in range(0, len(pos_tags)):
                sentence = sentence + " " + pos_tags[i][0] + "/" + pos_tags[i][1]
            text_list.append(sentence)
            current_sentence = ""
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
    f.close()
    return text_list


def build_ruleset(annotated_sentence_list, gene_list, stop_word_list):
    gene_stop_word_intersection = []
    rules = []
    word_frequencies = {}
    total_words = 0
    total_ngrams = []
    for gene in gene_list:
        if gene in stop_word_list:
            gene_stop_word_intersection.append(gene)
    for sentence in annotated_sentence_list:
        # count word frequencies
        if "/B" in sentence:
            annotated_words = sentence.split()
            for annotated_word in annotated_words:
                word = annotated_word.split("/")[0]
                total_words += 1
                if word in word_frequencies:
                    cnt = word_frequencies[word]
                    word_frequencies[word] = cnt + 1
                else:
                    word_frequencies[word] = 1
            # build ngrams
            for n in range(2, 5):
                for ngram in nltk.ngrams(annotated_words, n):
                    ngram_String = " ".join(ngram)
                    if "/B" in ngram_String:
                        occurences = ngram_String.count("/B")

                        # if multiple B in ngram, then adapt ngram, so only one protein is considered
                        if occurences >= 2:
                            for i in range(0, occurences):
                                copy_ngram = ngram
                                b_counter = 0
                                final_ngram = ""
                                for word in copy_ngram:
                                    if "/B" in word:
                                        if b_counter == i:
                                            word.replace("/B", "/O")
                                        final_ngram = " " + word
                                total_ngrams.append(final_ngram)
                        else:
                            total_ngrams.append(ngram_String)

    # print (word_frequencies)
    final_frequencies = {}
    for word in word_frequencies:
        if word_frequencies[word] != 1 and word not in stop_word_list:
            # print(word)
            final_frequencies[word] = word_frequencies[word]
    # print(final_frequencies)

    for ngram in total_ngrams:
        rule = ""
        parts = ngram.split()
        ngram_length = len(parts)
        tag_count = 0
        for part in parts:
            word, iob, tag = part.split("/")
            # print(word,iob,tag)
            if iob == "B-protein":
                rule = rule + " [PROTEIN]"
            elif word in stop_word_list:
                rule = rule + " /" + tag
                tag_count += 1
            elif word in final_frequencies:
                rule = rule + " " + word
            else:
                rule = rule + " /" + tag
                tag_count += 1
        if not tag_count >= ngram_length - 1:
            rules.append(rule)
            print(rule)
    return rules


def find_Entities_rulebased(sentence, rules):
    return


def find_Entities_structbased(sentence):
    words = sentence.split(" ")
    tagged_sentence = ""
    for index, word in enumerate(words):
        conditions_true = 0
        tags = word.split("/")
        print tags
        try:
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
            if conditions_true > 1:
                tagged_sentence = tagged_sentence + tags[0] + "/" + tags[1] + "/1 "
            else:
                tagged_sentence = tagged_sentence + tags[0] + "/" + tags[1] + "/0 "
        except:
            pass
    return tagged_sentence

#find_Entities_structbased("In/O/IN addition/O/NN lexical/O/JJ priming/O/NN was/O/VBD examined/O/VBN by/O/IN presenting/O/VBG an/O/DT identity/O/NN prime/O/JJ earlier/O/RBR in/O/IN the/O/DT text/O/NN ./O/.")

def find_Entities_dictbased(sentence):
    return


def find_Entities(input_file, rules):
    for sentence in input_file:
        print sentence
        potential_Entities_by_Rule = find_Entities_rulebased(sentence, rules)
        potential_Entities_by_Struct = find_Entities_structbased(sentence)
        potenital_Entities_by_dict = find_Entities_dictbased(sentence)


# calc occurences of potential proteins and decide on I or B-protein tag
# return iob-tagged strings

def write_results_to_file(iob_tagged_input, input_file):
    return


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="input file for annotation")
    args = parser.parse_args()

    # load gene names
    gene_list = load_gene_list()
    # load stop words
    stop_word_list = load_stop_words()
    # load training file	#input file if
    annotated_sentence_list = load_annotated_sentence_list()
    rules = build_ruleset(annotated_sentence_list, gene_list, stop_word_list)
    annotated_input = load_input_file(args.input_file)
    iob_tagged_input = find_Entities(annotated_input, rules)
    write_results_to_file(iob_tagged_input, args.input_file)


if __name__ == '__main__':
    main(sys.argv)
