import sys
from alt import *


def find_successors(sentence_tokens, phrases, phrase):
    """
    Find possible successors
    :param phrase:
    :param sentence_tokens:
    :param phrases:
    """
    successors = []
    phrase_tokens = phrase.strip().split()
    last_word = phrase_tokens[len(phrase_tokens)-1]
    last_word_ind = sentence_tokens.index(last_word)
    if last_word_ind == len(sentence_tokens)-1:  # end of sentence
        return successors
    for phr in phrases:
        phr_tokens = phr.strip().split()
        if sentence_tokens.index(phr_tokens[0]) == last_word_ind + 1:  # phrase begins with successor
            successors.append(phr)
    return successors


def find_ms(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, string):
    """
    finds phrases with monotonic prientation with the following characteristic:
    there exists a (f',e')-pair, for which right(e') = left(e)-1 AND right(f') = left(f)-1
    :param e: current english phrase
    :param f: current foreign phrase
    :param e_suc: english successors of current english phrase
    :param f_suc: foreing successors of current foreign phrase
    :param e_tokens: tokens of english input sentence
    :param f_tokens: tokens of foreign input sentence
    :param string: left-right or right-left
    :return:
    """
    if f not in ms:
        ms[f] = {}
    for e_s, f_s in zip(e_suc, f_suc):
        print e, e_s, f, f_s
        if len(e_suc) == 1 and len(f_suc) == 1:
            # find last words of current phrases and first words of successors
            last_f = f.strip().split()[-1]
            last_e = e.strip().split()[-1]
            first_e_s = e_s.strip().split()[0]
            first_f_s = f_s.strip().split()[0]
            if f_tokens.index(last_f) == e_tokens.index(first_e_s) - 1 and e_tokens.index(last_e) == f_tokens.index(first_f_s) - 1:
                if e in ms[f]:
                    ms[f][e] += 1
                else:
                    ms[f][e] = 1
        #else:  # more than one successor in one of the languages. Problem: different amounts of successors
            # for ee, ff in zip(e_s, f_s):
            #     if f_tokens.index(f) == e_tokens.index(ee) - 1 and e_tokens.index(e) == f_tokens.index(ff) - 1:
            #         if e in ms[f]:
            #             ms[f[e]] += 1
            #         else:
            #             ms[f[e]] = 1
    return ms


def find_ss(e, f, e_phrases, f_phrases, e_str, f_str, string):
    return 0


def find_dls(e, f, e_phrases, f_phrases, e_str, f_str, string):
    return 0


def find_drs(e, f, e_phrases, f_phrases, e_str, f_str, string):
    return 0


def orientation_extraction(e_path, f_path, aligned_path, max_length):

    m_counter_rl = Counter()
    dl_counter_rl = Counter()
    dr_counter_rl = Counter()
    s_counter_rl = Counter()
    m_counter_lr = Counter()
    dl_counter_lr = Counter()
    dr_counter_lr = Counter()
    s_counter_lr = Counter()

    ms = {}

    with open(e_path, 'r') as e_f, open(f_path, 'r') as f_f, open(aligned_path, 'r') as aligned_f:
        sample_size = 10
        for e_str, f_str, align_str in zip(e_f, f_f, aligned_f):
            e_tokens = e_str.strip().split()
            f_tokens = f_str.strip().split()

            alignments = parse_alignments(align_str)

            # Update the various counters
            _, e, f = extract_phrases(e_tokens, f_tokens, alignments, max_length)
            e_phrases = e.keys()
            f_phrases = f.keys()
            for e, f in zip(e_phrases, f_phrases):
                e_suc = find_successors(e_tokens, e_phrases, e)
                f_suc = find_successors(f_tokens, f_phrases, f)
                ms = find_ms(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "rl")

            print ms
            raw_input("Bla:")


            sample_size -= 1
            if sample_size == 0:
                break
    print 'Phrases and orientations extracted'
    return m_counter_rl, dl_counter_rl, dr_counter_rl, s_counter_rl, m_counter_lr, dl_counter_lr, dr_counter_lr, s_counter_lr


def main():
    if len(sys.argv) != 4:
        print 'Usage: python alt3.py [e_file] [f_file] [aligned_file]'
        exit()

    e_path = sys.argv[1]
    f_path = sys.argv[2]
    aligned_path = sys.argv[3]
    max_length = 7

    orientations = orientation_extraction(e_path, f_path, aligned_path, max_length)


if __name__ == '__main__':
    main()