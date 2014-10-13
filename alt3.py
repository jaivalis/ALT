from collections import Counter
import sys


def parse_alignments(alignments_str):
    """ Parse an alignment string line into a set containing the pairs of the pairs """
    ret = set()
    alignments = alignments_str.strip().split()
    for al in alignments:
        num1, num2 = al.split('-')
        ret.add((int(num1), int(num2)))
    return ret


def get_phrase_alignment(e_start, e_end, f_start, f_end, alignments, e_tokens, f_tokens):
    if f_end < 0:
        return None
    for f, e in alignments:
        if (f_start <= f <= f_end) and (e < e_start or e > e_end):
            return None

    aligned_phrases = []
    e_phrases = []
    f_phrases = []

    f_aligned = [j for _, j in alignments]

    f_s = f_start
    while True:
        f_e = f_end
        while True:  # add phrase pair (e_start, e_end, f_start, f_end) to returned
            e_phrase = ' '.join(e_tokens[e_start:e_end+1])
            f_phrase = ' '.join(f_tokens[f_s:f_e+1])

            aligned_phrases.append([e_phrase, f_phrase])
            e_phrases.append(e_phrase)
            f_phrases.append(f_phrase)

            f_e += 1
            if f_e in f_aligned or f_e == len(f_tokens):  # until f_e aligned
                break
        f_s -= 1
        if f_s in f_aligned or f_s < 0:  # until f_s aligned
            break
    return aligned_phrases, e_phrases, f_phrases


def extract_phrases(e_tokens, f_tokens, alignments, max_length):
    aligned_phrases = []
    e_phrases = []
    f_phrases = []

    for e_start in range(0, len(e_tokens)):
        for e_end in range(e_start, len(e_tokens)):
            if e_end-e_start > max_length:
                continue

            f_start = len(f_tokens)-1
            f_end = -1

            for f, e in alignments:
                if e_start <= e <= e_end:
                    f_start = min(f, f_start)
                    f_end = max(f, f_end)

            tmp = get_phrase_alignment(e_start, e_end, f_start, f_end, alignments, e_tokens, f_tokens)
            if tmp is None:
                continue
            phrase_alignment = tmp[0]
            e_phrase = tmp[1]
            f_phrase = tmp[2]

            aligned_phrases = aligned_phrases + phrase_alignment
            e_phrases.append(e_phrase)
            f_phrases.append(f_phrase)
    return aligned_phrases, e_phrases, f_phrases
###### alt1.py end


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


def find_single_successor(sentence_tokens, word_ind, orientation):
    """ Find single word successor
    :param sentence_tokens:
    :param word_ind:
    :return:
    """
    if orientation == 'lr':
        if word_ind == len(sentence_tokens) - 1:  # end of sentence
            return None
        else:
            return sentence_tokens[word_ind + 1]
    else:
        if word_ind == 0:  # start of sentence
            return None
        else:
            return sentence_tokens[word_ind - 1]


def translate(aligned_phrases, word):
    """
    :param aligned_phrases:
    :param word:
    :param string:
    :return:
    """
    for pair in aligned_phrases:
        if pair[0] == word:
            return pair[1]


def monotone(f_a, f_b, e_a, e_b, orientation):
    if orientation == 'rl':
        if f_a == f_b + 1 and e_a == e_b + 1:
            return True
    if orientation == 'lr':
        if f_a + 1 == f_b and e_a + 1 == e_b:
            return True
    return False


def swap(f_a, f_b, e_a, e_b, orientation):
    if orientation == 'rl':
        if f_a + 1 == f_b and e_a == e_b + 1:
            return True
    if orientation == 'lr':
        if f_a == f_b + 1 and e_a + 1 == e_b:
            return True
    return False


def discontinuous(f_a, f_b, e_a, e_b, orientation):
    if not monotone(f_a, f_b, e_a, e_b, orientation) and not swap(f_a, f_b, e_a, e_b, 'rl') and not swap(f_a, f_b, e_a, e_b, 'lr'):
        return True
    return False


def get_orientation(e, f, e_suc, f_suc, e_index, e_suc_index, f_index, f_suc_index, orientation, approach):
    """ Determines the orientation for a given e-f pair
    :param e:
    :param f:
    :param e_suc:
    :param f_suc:
    :param e_index:
    :param e_suc_index:
    :param f_index:
    :param f_suc_index:
    :param orientation: rl, lr
    :param approach: word, phrase
    :return: String corresponding to the case ['mono', 'swap', 'discR', 'discL']
    """
    if approach == "word":
        print f_index, f_suc_index, '||', e_index, e_suc_index
        if monotone(f_index, f_suc_index, e_index, e_suc_index, orientation):
            print 'mono'
            return 'mono'
        if swap(f_index, f_suc_index, e_index, e_suc_index, orientation):
            print 'swap'
            return 'swap'
        if discontinuous(f_index, f_suc_index, e_index, e_suc_index, orientation):
            if f_index < f_suc_index:
                print 'discR'
                return 'discR'
            elif f_index > f_suc_index:
                print 'discL'
                return 'discL'
    # if string2 == "phrase":
        #     for e_s in e_suc:
        #         # find last words of current phrases and first words of successors
        #         last_f = f.strip().split()[-1]
        #         last_e = e.strip().split()[-1]
        #         first_e_s = e_s.strip().split()[0]
        #         first_f_s = f_s.strip().split()[0]
        #         # find indexes of those first and last words
        #         f_b = f_tokens.index(first_f_s)
        #         f_a = f_tokens.index(last_f)
        #         e_b = e_tokens.index(first_e_s)
        #         e_a = e_tokens.index(last_e)
        #         print f_index, f_b, '||', e_a, e_b
        #         if monotone(f_index, f_b, e_a, e_b):
        #             print "mono"
        #             if f not in ms:
        #                 ms[f] = {}
        #                 if e in ms[f]:
        #                     ms[f][e] += 1
        #                 else:
        #                     ms[f][e] = 1
        #         if swap(f_a, f_b, e_a, e_b):
        #             print "swap"
        #             pass
        #         if discontinuous(f_a, f_b, e_a, e_b):
        #             print "dis"
        #             pass


def _store_o(dict, f, e):
    if f not in dict:
        dict[f] = {}
        if e in dict[f]:
            dict[f][e] += 1
        else:
            dict[f][e] = 1


def store_orientation(o, e, f, orientation):
    if orientation == 'lr':
        if o == 'mono':
            _store_o(m_counter_lr, f, e)
        elif o == 'swap':
            _store_o(s_counter_lr, f, e)
        elif o == 'discR':
            _store_o(dr_counter_lr, f, e)
        elif o == 'discL':
            _store_o(dl_counter_lr, f, e)
    elif orientation == 'rl':
        if o == 'mono':
            _store_o(m_counter_rl, f, e)
        elif o == 'swap':
            _store_o(s_counter_rl, f, e)
        elif o == 'discR':
            _store_o(dr_counter_rl, f, e)
        elif o == 'discL':
            _store_o(dl_counter_rl, f, e)


def get_translation_indexes(index, suc_index, alignments):
    i = []
    suc_i = []
    for pair in alignments:
        if pair[0] == index:
            i.append(pair[1])
        if pair[0] == suc_index:
            suc_i.append(pair[1])
    return i, suc_i


def orientation_extraction(e_path, f_path, aligned_path, max_length):
    with open(e_path, 'r') as e_f, open(f_path, 'r') as f_f, open(aligned_path, 'r') as aligned_f:
        sample_size = 1
        for e_str, f_str, align_str in zip(e_f, f_f, aligned_f):
            e_tokens = e_str.strip().split()
            f_tokens = f_str.strip().split()

            alignments = parse_alignments(align_str)
            # Update the various counters
            e_f, e_phrases, f_phrases = extract_phrases(e_tokens, f_tokens, alignments, max_length)

            for e_index, e in enumerate(e_tokens):  # word based
                orientation = 'lr'
                e_suc = find_single_successor(e_tokens, e_index, orientation)
                print e_suc
                if e_suc is None:  # last word
                    break
                f = translate(e_f, e)
                print f
                if f is not None:
                    if ' ' in f:  # e was translated to more than one foreign words
                        f_split = f.strip().split()
                        for f_token in f_split:
                            f_suc = find_single_successor(f_tokens, e_index, orientation)
                            if f_suc is not None and e_suc is not None:
                                print e, e_suc, f_token, f_suc

                                f_index, f_suc_index = get_translation_indexes(e_index, e_index+1, alignments, orientation)
                                print "indices: ", e_index, e_index+1, f_index, f_suc_index
                                if len(f_suc_index) == 0:  # unaligned word #yolo
                                    print 'yolo'
                                    continue

                                if len(f_index) > 1 or len(f_suc_index) > 1:
                                    if len(f_index) > 1 and len(f_suc_index) == 1:
                                        for f_indices in f_index:
                                            o = get_orientation(e, f, e_suc, f_suc, e_index, e_index+1,
                                                                f_indices, f_suc_index[0], orientation, "word")
                                            store_orientation(o, e, f, orientation)
                                    if len(f_suc_index) > 1 and len(f_index) == 1:
                                        for f_suc_indices in f_suc_index:
                                            o = get_orientation(e, f, e_suc, f_suc, e_index, e_index+1,
                                                                f_index[0], f_suc_indices, orientation, "word")
                                            store_orientation(o, e, f, orientation)
                                else:
                                    o = get_orientation(e, f, e_suc, f_suc, e_index, e_index+1,
                                                        f_index[0], f_suc_index[0], orientation, "word")
                                    store_orientation(o, e, f, orientation)
                    else:  # 1-1 case
                        f_suc = translate(e_f, e_suc)
                        if f_suc is not None:
                            print e, e_suc, f, f_suc

                            f_index, f_suc_index = get_translation_indexes(e_index, e_index+1, alignments)
                            print "indices: ", e_index, e_index+1, f_index, f_suc_index
                            if len(f_index) == 0 or len(f_suc_index) == 0:  # unaligned word #yolo
                                print 'yolo'
                                continue
                            if len(f_index) > 1 or len(f_suc_index) > 1:
                                if len(f_index) > 1 and len(f_suc_index) == 1:
                                    for f_indices in f_index:
                                        o = get_orientation(e, f, e_suc, f_suc, e_index, e_index+1,
                                                            f_indices, f_suc_index[0], orientation, "word")
                                        store_orientation(o, e, f, orientation)
                                if len(f_suc_index) > 1 and len(f_index) == 1:
                                    for f_suc_indices in f_suc_index:
                                        o = get_orientation(e, f, e_suc, f_suc, e_index, e_index+1,
                                                            f_index[0], f_suc_indices, orientation, "word")
                                        store_orientation(o, e, f, orientation)
                            else:
                                o = get_orientation(e, f, e_suc, f_suc, e_index, e_index+1,
                                                    f_index[0], f_suc_index[0], orientation, "word")
                                store_orientation(o, e, f, orientation)
                        else:
                            print 'no f translation \'{}\', \'{}\' '.format(e, e_suc)
            for e_index, e in enumerate(e_tokens):  # word based
                orientation = 'rl'
                e_suc = find_single_successor(e_tokens, e_index, orientation)
                print e_suc
                if e_index == 0:
                    continue
                if e_suc is None:  # last word
                    break
                f = translate(e_f, e)
                print f
                if f is not None:
                    if ' ' in f:  # e was translated to more than one foreign words
                        f_split = f.strip().split()
                        for f_token in f_split:
                            f_suc = find_single_successor(f_tokens, e_index, orientation)
                            if f_suc is not None and e_suc is not None:
                                print e, e_suc, f_token, f_suc

                                f_index, f_suc_index = get_translation_indexes(e_index, e_index-1, alignments, orientation)
                                print "indices: ", e_index, e_index-1, f_index, f_suc_index
                                if len(f_suc_index) == 0:  # unaligned word #yolo
                                    print 'yolo'
                                    continue

                                if len(f_index) > 1 or len(f_suc_index) > 1:
                                    if len(f_index) > 1 and len(f_suc_index) == 1:
                                        for f_indices in f_index:
                                            o = get_orientation(e, f, e_suc, f_suc, e_index, e_index-1,
                                                                f_indices, f_suc_index[0], orientation, "word")
                                            store_orientation(o, e, f, orientation)
                                    if len(f_suc_index) > 1 and len(f_index) == 1:
                                        for f_suc_indices in f_suc_index:
                                            o = get_orientation(e, f, e_suc, f_suc, e_index, e_index-1,
                                                                f_index[0], f_suc_indices, orientation, "word")
                                            store_orientation(o, e, f, orientation)
                                else:
                                    o = get_orientation(e, f, e_suc, f_suc, e_index, e_index-1,
                                                        f_index[0], f_suc_index[0], orientation, "word")
                                    store_orientation(o, e, f, orientation)
                    else:  # 1-1 case
                        f_suc = translate(e_f, e_suc)
                        if f_suc is not None:
                            print e, e_suc, f, f_suc

                            f_index, f_suc_index = get_translation_indexes(e_index, e_index-1, alignments)
                            if len(f_index) == 0 or len(f_suc_index) == 0:  # unaligned word #yolo
                                print 'yolo'
                                continue
                            if len(f_index) > 1 or len(f_suc_index) > 1:
                                if len(f_index) > 1 and len(f_suc_index) == 1:
                                    for f_indices in f_index:
                                        o = get_orientation(e, f, e_suc, f_suc, e_index, e_index-1,
                                                            f_indices, f_suc_index[0], orientation, "word")
                                        store_orientation(o, e, f, orientation)
                                if len(f_suc_index) > 1 and len(f_index) == 1:
                                    for f_suc_indices in f_suc_index:
                                        o = get_orientation(e, f, e_suc, f_suc, e_index, e_index-1,
                                                            f_index[0], f_suc_indices, orientation, "word")
                                        store_orientation(o, e, f, orientation)
                            else:
                                o = get_orientation(e, f, e_suc, f_suc, e_index, e_index-1,
                                                    f_index[0], f_suc_index[0], orientation, "word")
                                store_orientation(o, e, f, orientation)
                        else:
                            print 'no f translation \'{}\', \'{}\' '.format(e, e_suc)
            # for i, f in enumerate(f_tokens):
            #     e = translate(e_f, f, "rl")
            #     if e is not None:
            #         # if ' ' in e:  # f was translated in two english words
            #         #     ee = e_str.strip().split()
            #         #     for e in ee:
            #         #         e_suc = find_single_successor(e_tokens, e, orientation)
            #         #         f_suc = find_single_successor(f_tokens, f, orientation)
            #         #         if e_suc is not None and f_suc is not None:
            #         #             ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "rl", "word")
            #         #             print f, f_suc, e, e_suc
            #         #             continue
            #         e_suc = find_single_successor(e_tokens, i, orientation)
            #         f_suc = find_single_successor(f_tokens, f, orientation)
            #         if e_suc is not None and f_suc is not None:
            #             ms = find_orientations(ms, e, f, e_suc, f_suc, e_tokens, f_tokens, "rl", "word")
            #             print f, f_suc, e, e_suc

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

# static vars
m_counter_rl = Counter()
dl_counter_rl = Counter()
dr_counter_rl = Counter()
s_counter_rl = Counter()
m_counter_lr = Counter()
dl_counter_lr = Counter()
dr_counter_lr = Counter()
s_counter_lr = Counter()


def main():
    if len(sys.argv) != 4:
        print 'Usage: python alt3.py [e_file] [f_file] [aligned_file]'
        exit()

    e_path = sys.argv[1]
    f_path = sys.argv[2]
    aligned_path = sys.argv[3]
    max_length = 7

    orientation_extraction(e_path, f_path, aligned_path, max_length)

    pass


if __name__ == '__main__':
    main()