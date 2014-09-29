import sys
from collections import Counter
from random import randrange
import math
import copy


def generate_output(clusters, outfile=None):
    """Generates the formatted output given the phrase counter as asked:
    <word> <class_id>

    :param clusters: dict containing <class_id>, <Counter> pairs
    :param outfile: filename to write output to
    """
    if outfile is None:
        out = sys.stdout
    else:
        out = open(outfile, 'w')
    try:
        for key, counter in clusters.iteritems():
            for w in counter:
                out.write(w + " " + str(key) + "\n")
    finally:
        if outfile is not None:
            out.close()


def count_words_per_cluster(clusters):
    """ Given the clusters returns a dict containing the sum of counts of words per cluster
    :param clusters
    :return: dict containing the sum of counts of words per cluster
    """
    ret = {}
    for i in range(len(clusters)):
        ret[i] = sum(clusters[i].values())
    return ret


def in_list(dict_, word):
    # looks up if word is in dict
    if dict_ == {}:
        return False
    if word in dict_:
        return True
    else:
        return False


def find_index(cluster, word):
    # looks up in cluster and returns index
    for i in range(len(cluster)):
        if word in list(cluster[i]):
            return i


def compute_log_likelihood(N_C, N_w_C):
    ret = 0
    for word in N_w_C:
        for c in N_w_C[word]:
            if N_w_C[word][c] == 0:
                continue
            # try:
            ret += (N_w_C[word][c] * math.log(N_w_C[word][c]))
            # except ValueError:
            #     print "Value Error: log()\tword: '{0}' \tc: '{1}'\tN_w_C[word][c]={2}".format(word, c, N_w_C[word][c])
    for word in N_C:
        if N_C[word] == 0:
            continue
        # try:
        if N_C[word] < 0:
            print 'negative', word, N_C[word]
        ret -= (N_C[word] * math.log(N_C[word]))
        # except ValueError:
        #     print "Value Error: log()\tword: '{0}' \tN_C[word]={1}".format(word, c, N_C[word])
    return ret


def move_word(word, cluster, N_C, N_w):

    delta = N_C * math.log(N_C)
    N_C_prime = N_C - N_w
    delta = delta - N_C_prime * math.log(N_C_prime)


def predictive_exchange_clustering(file_path, k):
    """ Implementation of the predictive exchange clustering algorithm

    Start  from  k  classes,  randomly  or  heuristically  initialized
    iteratively  move  each  word  of  the  vocabulary  to  the  class  that  results  in  the  best  likelihood  gain
    stop  at  convergence  or  after  a  given  number  of  iterations.

    :param file_path: Path to the file to be opened
    :param k: Number of clusters requested
    :return: dict containing the k clusters
    """
    N_w = Counter()  # word counter
    N_w_w = dict()  # word successors
    N_C = dict()  # sum of counts per class
    N_w_C = dict()  # word-class successors

    clusters = dict()  # returned variable

    with open(file_path, 'r') as e_file:
        sample_size = 10
        for line in e_file:
            e_tokens = line.strip().split()
            # Count the words
            N_w.update(e_tokens)
            
            # Count successors
            for i in range(len(e_tokens)-1):
                if e_tokens[i] in N_w_w:
                    if e_tokens[i+1] in N_w_w[e_tokens[i]]:
                        N_w_w[e_tokens[i]][e_tokens[i+1]] += 1
                    else:
                        N_w_w[e_tokens[i]][e_tokens[i+1]] = 1
                else:
                    N_w_w[e_tokens[i]] = {}
                    N_w_w[e_tokens[i]][e_tokens[i+1]] = 1

            sample_size -= 1
            if sample_size == 0:
                break
        
    # initialize k classes randomly
    for w in N_w:
        rnd = randrange(k)
        if rnd not in clusters:
            clusters[rnd] = Counter([])
        clusters[rnd].update([w])

    # Count words in Classes
    N_C = count_words_per_cluster(clusters)

    # Create N_w_C
    for w in N_w:
        N_w_C[w] = [0 for x in range(k)]
        if w in N_w_w:
            for v in N_w_w[w]:
                if in_list(N_w_C[w], find_index(clusters, v)):
                    N_w_C[w][find_index(clusters, v)] = N_w_w[w][v]
                else:
                    N_w_C[w][find_index(clusters, v)] += N_w_w[w][v]

    log = 0
    while log < 10000:  # stop at convergence
        print 'before', sum(N_C.values())
        for word in N_w:  # for word in vocabulary
            log = compute_log_likelihood(N_C, N_w_C)
            #print " old class: ", C_a
            # copy N_C and N_w_C
            N_C_copy = copy.deepcopy(N_C)
            N_w_C_copy = copy.deepcopy(N_w_C)
            # remove word and update tables N_C and N_w_C
            C_a = find_index(clusters, word)
            print 'count original class', N_C[C_a]
            N_C_ = N_C
            N_C_[C_a] = N_C[C_a] - N_w[word]
            for w in N_w_C:  # for word in word-class array
                if w not in N_w_w:  # the '.'
                    assert w == "." or w == ")"
                    continue
                if word not in N_w_w[w]:
                    continue
                N_w_C[w][C_a] = N_w_C[w][C_a] - N_w_w[w][word]
            for c in N_C:  # for every count
                print 'before class', c, 'count', N_C[c]
                #print "Class # ", c
                # move word to other class
                if c == C_a:
                    continue
                N_C[c] = N_C[c] + N_w[word]
                for w in N_w_C:
                    if w not in N_w_w:  # the '.'
                        assert w == "." or w == ")"
                        continue
                    if word not in N_w_w[w]:
                        continue
                    N_w_C[w][c] = N_w_C[w][c] + N_w_w[w][word]
                if compute_log_likelihood(N_C, N_w_C) < log:
                    # if new class leads to less log-likelihood, don't move the word there
                    N_C = copy.deepcopy(N_C_copy)
                    N_w_C = copy.deepcopy(N_w_C_copy)
                    print 'not moved! after class', c, 'count', N_C[c], 'occurencies word', N_w[word]
                else:
                    N_C[C_a] = N_C_[C_a]
                    print 'moved! after class', c, 'count', N_C[c], 'occurencies word', N_w[word]
                    print 'count original class after moved', N_C[C_a]
                    break
                if c == len(N_C) - 1:  # put it back to old class i guess?
                    print "word: '{0}' \tc: '{1}' not moved.".format(word, c)
                    N_C = N_C_copy
                    N_W_C = N_w_C_copy
            print 'after', sum(N_C.values())
            raw_input('AHA!: ')

    return clusters


def main():
    if len(sys.argv) != 2:
        print 'Usage: python alt2.py [e_file]'
        exit()

    e_path = sys.argv[1]
    k = 20

    clusters = predictive_exchange_clustering(e_path, k)
    generate_output(clusters)

if __name__ == '__main__':
    main()