import sys
from collections import Counter
from random import randrange
import math


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
            ret += (N_w_C[word][c] * math.log(N_w_C[word][c]))
    for cluster in N_C:
        if N_C[cluster] == 0:
            continue
        if N_C[cluster] < 0:
            print 'Negative log likelihood ', N_C[cluster]
        ret -= (N_C[cluster] * math.log(N_C[cluster]))
    return ret


def has_no_successor(N_w_w, word, w):
    """
    Returns true if the word has no successor in the N_w_w array, false otherwise
    :param N_w_w:
    :param word:
    :param w:
    :return: true if the word has no successor in the N_w_w array, false otherwise
    """
    if w not in N_w_w:
        assert w == "." or w == ")"
        return True
    if word not in N_w_w[w]:
        return True
    return False


def move_word(clusters, word, cluster, N_C, N_w, N_w_C, N_w_w):
    """ Moves a word to a given cluster
    :param clusters:
    :param word:
    :param N_C:
    :param N_w:
    :param N_w_C:
    :param N_w_w:
    :return:
    """
    N_C[cluster] = N_C[cluster] + N_w[word]
    clusters[cluster].update([word])
    for w in N_w_C:
        if has_no_successor(N_w_w, word, w):
            continue
        N_w_C[w][cluster] = N_w_C[w][cluster] + N_w_w[w][word]
    return clusters, N_C, N_w_C


def remove_word(clusters, word, N_C, N_w, N_w_C, N_w_w):
    origin_cluster = find_index(clusters, word)
    del clusters[origin_cluster][word]
    if N_C[origin_cluster] < N_w[word]:  # TODO
        print ''
    N_C_ = N_C
    N_C_[origin_cluster] = N_C[origin_cluster] - N_w[word]

    # remove word from clusters
    for w in N_w_C:  # for word in word-class array
        if has_no_successor(N_w_w, word, w):
            continue
        N_w_C[w][origin_cluster] = N_w_C[w][origin_cluster] - N_w_w[w][word]
    return clusters, N_C_, N_w_C, origin_cluster


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
        N_w_C[w] = [0 for _ in range(k)]
        if w in N_w_w:
            for v in N_w_w[w]:
                if in_list(N_w_C[w], find_index(clusters, v)):
                    N_w_C[w][find_index(clusters, v)] = N_w_w[w][v]
                else:
                    N_w_C[w][find_index(clusters, v)] += N_w_w[w][v]

    current_log_likelihood = 0
    while current_log_likelihood < 10000:  # stop at convergence

        for word in N_w:  # for word in vocabulary
            best_log_likelihood = compute_log_likelihood(N_C, N_w_C)

            clusters, N_C, N_w_C, origin_cluster = remove_word(clusters, word, N_C, N_w, N_w_C, N_w_w)

            best_cluster = origin_cluster
            for cluster in N_C:  # try every other cluster
                if cluster == origin_cluster:  # the log likelihood has already been computed
                    continue

                clusters, N_C, N_w_C = move_word(clusters, word, cluster, N_C, N_w, N_w_C, N_w_w)

                log_likelihood = compute_log_likelihood(N_C, N_w_C)
                if log_likelihood > best_log_likelihood:
                    best_log_likelihood = log_likelihood
                    best_cluster = cluster

                clusters, N_C, N_w_C, origin_cluster = remove_word(clusters, word, N_C, N_w, N_w_C, N_w_w)

            # put the word in the best cluster found
            clusters, N_C, N_w_C = move_word(clusters, word, best_cluster, N_C, N_w, N_w_C, N_w_w)

            print "word '{0}' moved to cluster #{1} with log likelihood: {2}"\
                .format(word, best_cluster, best_log_likelihood)
            # raw_input('AHA!: ')

        current_log_likelihood = best_log_likelihood
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