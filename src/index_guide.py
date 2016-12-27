'''
Created on Oct 27, 2016

@author: Alison Paredes
'''
import fileinput
from collections import namedtuple, deque
import string
import math
import sys

def index_source(my_file, inverted_index, document_index):
    '''
    Reads the given file and constructs an inverted index.
    
    Index is made up of a dictionary for fast look up O(log n), 
    an index of terms O(1)), and an index of documents O(1) to store 
    document lengths, which may be used a query time.
    
    Each term in the term index contains a postings list
    containing document IDs (sentence IDs?), term frequencies, 
    weighted term frequencies.
    
    With the exception of TF-IDF, the index is constructed as file is read, 
    summing document lengths as each document is read.
    
    Because all documents must have been indexed before document frequency
    can be calculated for each term, TF-IDF requires a second pass
    through the inverted index. This is done at query time.
    '''
    for line in fileinput.input(my_file):
        term_occurrences = term_frequency(line)
        document_index.append(None)
        document_id = len(document_index) - 1
        length_term_frequency(document_index, document_id, term_occurrences, line)
        index_terms(inverted_index, term_occurrences, document_id)
    

def index_terms(inverted_index, term_occurrences, document_id):
    '''Expects a list of terms and term frequencies for a document and adds them to the inverted index.'''
    for term, term_frequency in term_occurrences.iteritems():
        
        posting = Posting(document_id=document_id,
                          term_frequency=term_frequency,
                          tf_idf=None)
    
        if term in inverted_index.vocabulary:
            term_id = inverted_index.vocabulary[term] #Python requires dictionary entry to be hashable
            postings = inverted_index.term_index[term_id]
            postings.append(posting)
        else:
            term_id = len(inverted_index.term_index)
            inverted_index.vocabulary[term]=term_id
            postings = [posting]
            inverted_index.term_index.append(postings)


def term_frequency(line):
    '''Parses a line into tokens and keeps track of the number of times the token occurred in the line.'''
    keep=''
    tokens={}
    for char in line:
        if char not in string.ascii_letters:
            char=''
        if char == '' and len(keep) > 0:
            if keep in tokens:
                tokens[keep]+=1
            else: 
                tokens[keep]=1
            keep=''
        else:
            keep += char
    return tokens


def length_term_frequency(document_index, document_id, term_occurrences, line):
    '''Adds a document to the document index'''
    running_term_frequency = 0.0    
    for _, tf in term_occurrences.iteritems():
        running_term_frequency += pow(tf,2)   
    document = Document(length_term_frequency=math.sqrt(running_term_frequency),
                        sum_tf_idf=0.0, text=line)
    document_index[document_id]=document


def get_postings(term, inverted_index):
    '''Returns a posting list from the inverted index.'''
    term_id = inverted_index.vocabulary[term]
    return inverted_index.term_index[term_id]


def get_inverse_document_frequency(term, inverted_index, document_index):
    '''Calculates inverse document frequency for a term.'''
    term_id = inverted_index.vocabulary[term]
    document_frequency = len(inverted_index.term_index[term_id])
    corpus_length = len(document_index)
    return math.log(corpus_length / float(document_frequency), 10)

def get_all_inverse_document_frequencies(inverted_index, document_index):
    '''Calculates inverse document frequency for all terms in the index.'''
    all_inverse_document_frequencies=[]
    for term, term_id in inverted_index.vocabulary.iteritems():
        all_inverse_document_frequencies.append((term, get_inverse_document_frequency(term, inverted_index, document_index)))
    return all_inverse_document_frequencies


def get_all_document_frequencies(inverted_index):
    '''Calculates document frequency for each term in the index. '''
    all_document_frequencies=[]
    for term, term_id in inverted_index.vocabulary.iteritems():
        all_document_frequencies.append((term, len(inverted_index.term_index[term_id])))
    return all_document_frequencies


def print_all_inverse_document_frequencies(all_inverse_document_frequencies):
    '''Prints a tab-delimited list of terms and their inverse document frequencies'''
    for frequency in all_inverse_document_frequencies:
        print '{0}\t{1}'.format(frequency[0], frequency[1])


def get_incidence_matrix(inverted_index, document_index):
    '''Creates an incidence matrix out of the inverted index and the document index.'''
    incidence_matrix=[[]]*len(inverted_index.vocabulary)
    for term, term_id in inverted_index.vocabulary.iteritems():
        incidence_matrix[term_id]=[0]*len(document_index)
        postings = inverted_index.term_index[term_id]
        for posting in postings:
            incidence_matrix[term_id][posting.document_id]=posting.term_frequency
        incidence_matrix[term_id].append(term)
    return incidence_matrix


def get_document_vector(document_id, inverted_index, document_index, score_using='TF_IDF'):
    '''Calculates TF-IDF for each term in the given document, returning a document vector.'''
    document_vector=[0]*len(inverted_index.vocabulary)
    incidence_matrix = get_incidence_matrix(inverted_index, document_index)
    for term, term_id in inverted_index.vocabulary.iteritems():
        if score_using=='TF_IDF':
            score=incidence_matrix[term_id][document_id] * get_inverse_document_frequency(term, inverted_index, document_index)
            document_vector[term_id]=(term, score)
    return document_vector


def get_normalized_document_vector(document_vector):
    '''Given a document vector, returns a new document vector containing normalized scores.'''
    sum_squared_terms = 0.0
    for term in document_vector:
        sum_squared_terms+= pow(term[1],2)
    vector_length = math.sqrt(sum_squared_terms)
    normalized_document_vector = []
    for term in document_vector:
        normalized_document_vector.append((term[0], term[1]/vector_length))
    return normalized_document_vector

def print_document_vector(document_id, document_vector):
    '''Prints a tab delimited list of terms and scores for the given document.'''
    print document_id
    for term in document_vector:
        if term[1] > 0:
            print '{0}\t{1}'.format(term[0], term[1])

def print_document_vector_for_jmp(document_id, document_vector):
    ''''''
    for term in document_vector:
       if term[1] > 0:
            print '{0}\t{1}'.format(document_id, term[1])

def get_term_frequency(term, document_id, inverted_index, document_index):
    '''Returns the term frequency for a given term-document pair'''
    incidence_matrix = get_incidence_matrix(inverted_index, document_index)
    term_id = inverted_index.vocabulary[term]
    return incidence_matrix[term_id][document_id]


def query(term_list, inverted_index, document_index):
    '''Queries the index, ranking documents by their similarity to the query. Similarity is sum of TF_IDF scores for
    each term occuring in both the document and the query.'''
    result_dict={}
    for term in term_list:
        if term in inverted_index.vocabulary:
            term_id = inverted_index.vocabulary[term]
            postings = inverted_index.term_index[term_id]
            for posting in postings:
                score = (1 + math.log(posting[1])) * get_inverse_document_frequency(term, inverted_index, document_index)
                if posting.document_id in result_dict:
                    result_dict[posting.document_id] += score
                else:
                    result_dict[posting.document_id] = score
    result_list = []
    for document_id, score in result_dict.iteritems():
        result_list.append([document_id, score, document_index[document_id].text])

    return sorted(result_list, key=lambda document: document[1], reverse=True)[0:9]


if __name__ == '__main__':
    

    Document = namedtuple('Document',['length_term_frequency','sum_tf_idf', 'text'])
    Posting = namedtuple('Posting',['document_id', 'term_frequency', 'tf_idf']) 
    InvertedIndex = namedtuple('InvertedIndex',['vocabulary','term_index','inverse_document_frequency'])
    
    inverted_index = InvertedIndex(vocabulary={},term_index=[], inverse_document_frequency=None)
    document_index=[]
    
    index_source(sys.argv[1], inverted_index, document_index)
    
    #print 'vocabulary {0}'.format(len(inverted_index.vocabulary))
    #print get_all_document_frequencies(inverted_index)
    #print get_incidence_matrix(inverted_index, document_index)
    #print_all_inverse_document_frequencies(get_all_inverse_document_frequencies(inverted_index, document_index))
    '''document_list = [3]
    for document_id in document_list:
        document_vector = get_document_vector(document_id, inverted_index, document_index)
        normalized_document_vector = get_normalized_document_vector(document_vector)
        #print_document_vector(document_id, normalized_document_vector)'''
    #print query(['settlers'], inverted_index, document_index) #
    #print query(['starting','position'], inverted_index, document_index)
    #print get_inverse_document_frequency('settlers',inverted_index, document_index)
    #print get_term_frequency('settlers', 3, inverted_index, document_index)
    #print 'term index {0}'.format(len(inverted_index.term_index))
    #print 'document index {0}'.format(len(document_lengths))
    #print (get_postings('of',inverted_index))
    #print (get_normalized_tf_idf('nomads',1,inverted_index,document_lengths))
    #print query(['what','resources','should','i','move','my','settler','to'], inverted_index, document_index) #query_id = 1
    #print query(['do','i','irrigate','a','leather','square'], inverted_index, document_index) #query_id = 1
    #print query(['do','i','build','a','barracks','or','warrior','first'], inverted_index, document_index) #query_id = 1
    #print query(['do','i','fortify','or','sentry','my','warrior','in','city'], inverted_index, document_index) #query_id = 1
    #print query(['what','is','the','autoworker','doing'], inverted_index, document_index) #query_id = 1
    #print query(['how','long','does','the','peace','treaty','last','will','he','break','it'], inverted_index, document_index) #query_id = 1
    #print query(['where','is','barbarian','unrest'], inverted_index, document_index)
    #print query(['are','my','units','damaging','the','barbarians'], inverted_index, document_index)
    #print query(['should','i','build','archers','to','seige','my','enemy','s','cities'], inverted_index, document_index)
    query_terms = sys.argv[2].split()
    print sys.argv[2]
    query_results = query(query_terms, inverted_index, document_index) #['how','do','i','attack','with','archers']
    for result in query_results:
        print '{0}\t{1}\t{2}'.format(result[0], result[1], result[2].replace('\n',''))
    print '\n'