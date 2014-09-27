import sys
from collections import Counter
from random import randrange


def generate_output(clusters, outfile=None):
    """Generates the formatted output given the phrase counter as asked:
    <word> <class_id>

    :param clusters: dict containing <class_id>, <tuple> pairs
    :param outfile: filename to write output to
    """

    if outfile is None:
        out = sys.stdout
    else:
        out = open(outfile, 'w')
    try:
        for key, tupl in clusters:
            for w in tupl:
                out.write(w + " " + int(key) + "\n")
    finally:
        if outfile is not None:
            out.close()


def predictive_exchange_clustering(file_path, k):
    """ Implementation of the predictive exchange clustering algorithm

    Start  from  k  classes,  randomly  or  heuristically  initialized
    iteratively  move  each  word  of  the  vocabulary  to  the  class  that  results  in  the  best  likelihood  gain
    stop  at  convergence  or  after  a  given  number  of  iterations.

    :param file_path: Path to the file to be opened
    :param k: Number of clusters requested
    :return: dict containing the k clusters
    """
    N_w = Counter()
    N_w_w = dict()
    clusters = dict()
    N_C = Counter()
    N_w_C = dict()

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
        if rnd in clusters:
            clusters[rnd][len(clusters[rnd]) + 1] = w
        else:
            clusters[rnd] = {}
            clusters[rnd][0] = w

    # Count words in Classes
    for j in range(len(clusters)):
        N_C[j] = sum(clusters[j])

        # TODO: Create N_w_C

    return clusters


def main():
    if len(sys.argv) != 2:
        print 'Usage: python alt2.py [e_file]'
        exit()

    e_path = sys.argv[1]
    k = 20

    clusters = predictive_exchange_clustering(e_path, k)
    # generate_output(clusters)  # TODO

if __name__ == '__main__':
    main()