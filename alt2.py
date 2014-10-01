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


def count_words_per_cluster(clusters, N_w):
    """ Given the clusters returns a dict containing the sum of counts of words per cluster
    :param clusters
    :return: dict containing the sum of counts of words per cluster
    """
    ret = {}
    for i in range(len(clusters)):
        ret[i] = 0
        for w in clusters[i]:
            ret[i] += N_w[w]
    return ret


def get_cluster_index(cluster, word):
    """ Returns the index of a given word in the clusters dict
    :param cluster: clusters dict
    :param word: the word to look for
    :return: index of a given word in the clusters dict
    """
    for i in range(len(cluster)):
        if word in list(cluster[i]):
            return i


def compute_log_likelihood(N_C, N_w_C):
    ret = 0
    for word in N_w_C:
        for count in N_w_C[word]:
            if count == 0:
                continue
            ret += (count * math.log(count))
    for cluster in N_C:
        if N_C[cluster] == 0:
            continue
        if N_C[cluster] < 0:
            print 'Negative log likelihood ', N_C[cluster]
        ret -= (N_C[cluster] * math.log(N_C[cluster]))
    return ret


def successor_pair_exists(N_w_w, w1, w2):
    """ Returns true if the successor pair exists in the N_w_w array, false otherwise
    :param N_w_w: Successor pair matrix
    :param w1:    First word
    :param w2:    Successor word
    :return: true if the successor pair exists in the N_w_w array, false otherwise
    """
    if w1 not in N_w_w or w2 not in N_w_w[w1]:
        return False
    return True


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
        if successor_pair_exists(N_w_w, w, word):
            N_w_C[w][cluster] = N_w_C[w][cluster] + N_w_w[w][word]
    return clusters, N_C, N_w_C


def remove_word(clusters, word, N_C, N_w, N_w_C, N_w_w):
    origin_cluster = get_cluster_index(clusters, word)
    del clusters[origin_cluster][word]
    N_C[origin_cluster] -= N_w[word]

    for w in N_w_C:  # for word in word-class array
        if not successor_pair_exists(N_w_w, w, word):
            continue
        # if find_index(clusters, w) == origin_cluster:  # word is in the origin cluster
            # newcount = N_w_C[w][origin_cluster] - N_w_w[w][word]
        N_w_C[w][origin_cluster] -= N_w_w[w][word]
    return clusters, N_C, N_w_C, origin_cluster


def predictive_exchange_clustering(file_path, k, convergence_steps=100, sample_sentense_count=100):
    """ Implementation of the predictive exchange clustering algorithm

    Start from k classes, randomly initialized iteratively move each word of the vocabulary to the class
    that results in the best likelihood gain stop at convergence or after a given number of iterations.

    :param file_path: Path to the file to be opened
    :param k: Number of clusters requested
    :return: dict containing the k clusters
    """
    N_w = Counter()  # word counter/vocabulary
    N_w_w = dict()   # word successors
    N_C = dict()     # sum of counts per class
    N_w_C = dict()   # word-class successors

    clusters = dict()  # returned variable

    with open(file_path, 'r') as e_file:
        for line in e_file:
            e_tokens = line.strip().split()

            N_w.update(e_tokens)  # Count the words

            for i in range(len(e_tokens)-1):  # Count successors
                if e_tokens[i] in N_w_w:
                    if e_tokens[i+1] in N_w_w[e_tokens[i]]:
                        N_w_w[e_tokens[i]][e_tokens[i+1]] += 1
                    else:
                        N_w_w[e_tokens[i]][e_tokens[i+1]] = 1
                else:
                    N_w_w[e_tokens[i]] = {}
                    N_w_w[e_tokens[i]][e_tokens[i+1]] = 1

            sample_sentense_count -= 1
            if sample_sentense_count == 0:
                break

    for w in N_w:  # initialize k classes randomly [Correct, checked]
        rnd = randrange(k)
        if rnd not in clusters:
            clusters[rnd] = Counter([])
        clusters[rnd].update([w])

    N_C = count_words_per_cluster(clusters, N_w)  # Count words in Classes

    for word in N_w:  # Create N_w_C [Correct, checked]
        N_w_C[word] = [0 for _ in range(k)]
        if word in N_w_w:
            for v in N_w_w[word]:
                N_w_C[word][get_cluster_index(clusters, v)] += N_w_w[word][v]

    current_log_likelihood = 0
    converged = False
    steps = 0
    while not converged and steps < convergence_steps:  # stop at convergence
        for word in N_w:                                # for word in vocabulary
            best_log_likelihood = compute_log_likelihood(N_C, N_w_C)  # calculate initial log likelihood

            # 0 - remove word from original (random) cluster
            clusters, N_C, N_w_C, origin_cluster = remove_word(clusters, word, N_C, N_w, N_w_C, N_w_w)
            best_cluster = origin_cluster

            for cluster in N_C:  # try every other cluster
                if cluster == origin_cluster:  # the log likelihood has already been computed
                    continue
                # 1 - put the word in the cluster
                clusters, N_C, N_w_C = move_word(clusters, word, cluster, N_C, N_w, N_w_C, N_w_w)

                # 2 - measure log likelihood and store most likelihood
                log_likelihood = compute_log_likelihood(N_C, N_w_C)
                if log_likelihood > best_log_likelihood:
                    best_log_likelihood = log_likelihood
                    best_cluster = cluster

                # 3 - remove word from cluster (do not store the cluster# returned value)
                clusters, N_C, N_w_C, _ = remove_word(clusters, word, N_C, N_w, N_w_C, N_w_w)

            # 4 - put the word in the best cluster found
            clusters, N_C, N_w_C = move_word(clusters, word, best_cluster, N_C, N_w, N_w_C, N_w_w)

        converged = math.fabs(current_log_likelihood - best_log_likelihood) < 1
        steps += 1
        current_log_likelihood = best_log_likelihood
    return clusters


def main():
    if len(sys.argv) != 2:
        print 'Usage: python alt2.py [e_file]'
        exit()
    e_path = sys.argv[1]
    k = 4

    clusters = predictive_exchange_clustering(e_path, k)
    generate_output(clusters)

if __name__ == '__main__':
    main()