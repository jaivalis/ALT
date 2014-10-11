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
    last_word = phrase_tokens[len(phrase_tokens) - 1]
    last_word_ind = sentence_tokens.index(last_word)
    if last_word_ind == len(sentence_tokens) - 1:  # end of sentence
        return successors
    for phr in phrases:
        phr_tokens = phr.strip().split()
        if sentence_tokens.index(phr_tokens[0]) == last_word_ind + 1:  # phrase begins with successor
            successors.append(phr)
    return successors


def find_single_successor(sentence_tokens, word):
    """
    find single word successor
    :param sentence_tokens:
    :param word:
    """
    word_ind = sentence_tokens.index(word)
    if word_ind == len(sentence_tokens) - 1:  # end of sentence
        return None
    else:
        return sentence_tokens[word_ind + 1]


def translate(aligned_phrases, word, string):
    """

    :param alignments:
    :param word:
    :param string:
    """
    if string == "rl":
        for a in list(aligned_phrases):
            if a[1] == word:
                return a[0]
    if string == "lr":
        for a in list(aligned_phrases):
            if a[0] == word:
                return a[1]


def monotone(f_a, f_b, e_a, e_b):
    if f_a + 1 == f_b and e_a + 1 == e_b:
        return True


def swap(f_a, f_b, e_a, e_b):
    if f_a + 1 == f_b and e_a == e_b + 1:
        return True


def discontinuous(f_a, f_b, e_a, e_b):
    if not monotone(f_a, f_b, e_a, e_b) and not swap(f_a, f_b, e_a, e_b):
        return True


def find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, string1, string2):
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
    if string1 == "lr":  # english - german
        if string2 == "word":
            # find indexes of words
            f_b = f_tokens.index(f_suc)
            f_a = f_tokens.index(f)
            e_b = e_tokens.index(e_suc)
            e_a = e_tokens.index(e)
            print f_a, f_b, '||', e_a, e_b
            if monotone(f_a, f_b, e_a, e_b):
                print "mono"
                if f not in ms:
                    ms[f] = {}
                    if e in ms[f]:
                        ms[f][e] += 1
                    else:
                        ms[f][e] = 1
            if swap(f_a, f_b, e_a, e_b):
                print "swap"
                pass
            if discontinuous(f_a, f_b, e_a, e_b):
                print "dis"
                pass
        if string2 == "phrase":
            for e_s in e_suc:
                # find last words of current phrases and first words of successors
                last_f = f.strip().split()[-1]
                last_e = e.strip().split()[-1]
                first_e_s = e_s.strip().split()[0]
                first_f_s = f_s.strip().split()[0]
                # find indexes of those first and last words
                f_b = f_tokens.index(first_f_s)
                f_a = f_tokens.index(last_f)
                e_b = e_tokens.index(first_e_s)
                e_a = e_tokens.index(last_e)
                print f_a, f_b, '||', e_a, e_b
                if monotone(f_a, f_b, e_a, e_b):
                    print "mono"
                    if f not in ms:
                        ms[f] = {}
                        if e in ms[f]:
                            ms[f][e] += 1
                        else:
                            ms[f][e] = 1
                if swap(f_a, f_b, e_a, e_b):
                    print "swap"
                    pass
                if discontinuous(f_a, f_b, e_a, e_b):
                    print "dis"
                    pass
    if string1 == "rl":  # english - german
        if string2 == "word":
            # find indexes of words
            f_b = f_tokens.index(f_suc)
            f_a = f_tokens.index(f)
            e_b = e_tokens.index(e_suc)
            e_a = e_tokens.index(e)
            print f_a, f_b, '||', e_a, e_b
            if monotone(f_a, f_b, e_a, e_b):
                print "mono"
                ms = store_o(ms, f, e)
            if swap(f_a, f_b, e_a, e_b):
                print "swap"
                pass
            if discontinuous(f_a, f_b, e_a, e_b):
                print "dis"
                pass
    return ms


def store_o(dict, f, e):
    if f not in dict:
        dict[f] = {}
        if e in dict[f]:
            dict[f][e] += 1
        else:
            dict[f][e] = 1
    return dict


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
            e_f, e, f = extract_phrases(e_tokens, f_tokens, alignments, max_length)
            e_phrases = e.keys()
            f_phrases = f.keys()

            # word based
            for e in e_tokens:
                e_suc = find_single_successor(e_tokens, e)
                f = translate(e_f, e, "lr")
                if f is not None:
                    if ' ' in f:  # e was translated in more foreign words
                        ff = f.strip().split()
                        for f in ff:
                            f_suc = find_single_successor(f_tokens, f)
                            if f_suc is not None and e_suc is not None:
                                print e, e_suc, f, f_suc
                                ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "lr", "word")
                                continue
                    f_suc = find_single_successor(f_tokens, f)
                    if f_suc is not None and e_suc is not None:
                        print e, e_suc, f, f_suc
                        ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "lr", "word")
            for f in f_tokens:
                e = translate(e_f, f, "rl")
                if e is not None:
                    if ' ' in e:  # f was translated in two english words
                        ee = e_str.strip().split()
                        for e in ee:
                            e_suc = find_single_successor(e_tokens, e)
                            f_suc = find_single_successor(f_tokens, f)
                            if e_suc is not None and f_suc is not None:
                                ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "rl", "word")
                                print f, f_suc, e, e_suc
                                continue
                    e_suc = find_single_successor(e_tokens, e)
                    f_suc = find_single_successor(f_tokens, f)
                    if e_suc is not None and f_suc is not None:
                        ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "rl", "word")
                        print f, f_suc, e, e_suc
            # phrase based
            # for e_phr in e_phrases:
            #     e_suc = find_successors(e_tokens, e_phrases, e_phr)
            #     f_phr = translate(e_f, e_phr, "lr")
            #     f_suc = find_successors(f_tokens, f_phrases, f_phr)
            #     ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "lr", "phrase")
            # for f_phr in f_phrases:
            #     e_phr = translate(e_f, f_phr, "rl")
            #     e_suc = find_successors(e_tokens, e_phrases, e_phr)
            #     f_suc = find_successors(f_tokens, f_phrases, f_phr)
            #     ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "rl", "phrase")

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