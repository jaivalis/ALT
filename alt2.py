import sys
from collections import Counter
from random import randrange


def generate_output(phrase_counter, token_pairs, e_phrases, f_phrases, outfile=None):
    """ Generates the formatted output given the phrase counter as asked:

      f ||| e ||| p(f|e) p(e|f) l(f|e) l(e|f) ||| freq(f) freq(e) freq(f,e)
    FIXME
    """

    if outfile is None:
        out = sys.stdout
    else:
        out = open(outfile, 'w')
    try:
        e_phrases_count = sum(e_phrases.values())
        f_phrases_count = sum(f_phrases.values())
        all_phrases_count = sum(phrase_counter.values())
        for pair in phrase_counter:
            tok = pair.split('|||')
            e = tok[0]
            f = tok[1]


            freq_f = f_phrases[f]
            freq_e = e_phrases[e]
            freq_fe = phrase_counter[pair]
            prob_e = float(freq_e) / e_phrases_count
            prob_f = float(freq_f) / f_phrases_count

            cond_f_e = float(freq_fe) / freq_f
            cond_e_f = float(freq_fe) / freq_e
            l_e_f = -1 # TODO
            l_f_e = -1 # TODO

            string = "{0} ||| {1} {2:.4f} {3:.4f} {4:.4f} {5:.4f} ||| {6} {7} {8}".\
                format(f, e, cond_f_e, cond_e_f, l_f_e, l_e_f, freq_f, freq_e, freq_fe)
            out.write(string + '\n')

    finally:
        if outfile is not None:
            out.close()


def predictive_exchange_clustering(e_path, k):
    #start  from  k  classes,  randomly  or  heurisEcally  iniEalized
    #iteraEvely  move  each  word  of  the  vocabulary  to  the  class  that  results  in  the  best  likelihood  gain
    #stop  at  convergence  or  afer  a  given  number  of  iteraEons
    #result_ k clusters

    N_w = Counter()
    N_w_w = dict()
    classes = dict()
    N_C = Counter()
    N_w_C = dict()

    with open(e_path, 'r') as e_f:
        sample_size = 10
        for e_str in e_f:
            e_tokens = e_str.strip().split()
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
        
        # initaialze k classes randomly
        for w in N_w:
            rnd = randrange(k)
            if rnd in classes:
                classes[rnd][len(classes[rnd]) + 1] = w
            else:
                classes[rnd] = {}
                classes[rnd][0] = w

        # Count words in Classes
        for j in range(len(classes)):
            N_C[j] = sum(classes[j])

        # TODO: Create N_w_C

    print 'classes clustered with exchange algorithm'
    #generate_output(e_phrases, classes, 'file.out')


def main():
    if len(sys.argv) != 2:
        print 'Usage: python alt2.py [e_file]'
        exit()

    e_path = sys.argv[1]
    k = 20

    predictive_exchange_clustering(e_path, k)

if __name__ == '__main__':
    main()