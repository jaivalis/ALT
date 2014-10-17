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
            e_phrase = ' '.join(e_tokens[e_start:e_end + 1])
            f_phrase = ' '.join(f_tokens[f_s:f_e + 1])

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
    e_phrases = set()
    f_phrases = set()

    for e_start in range(0, len(e_tokens)):
        for e_end in range(e_start, len(e_tokens)):
            if e_end - e_start > max_length:
                continue

            f_start = len(f_tokens) - 1
            f_end = -1

            for f, e in alignments:
                if e_start <= e <= e_end:
                    f_start = min(f, f_start)
                    f_end = max(f, f_end)

            tmp = get_phrase_alignment(e_start, e_end, f_start, f_end, alignments, e_tokens, f_tokens)
            if tmp is None:
                continue
            phrase_alignment = tmp[0]

            aligned_phrases = aligned_phrases + phrase_alignment
    for pp in aligned_phrases:
        e_phrases.add(pp[0])
        f_phrases.add(pp[1])
    return aligned_phrases, e_phrases, f_phrases


# ##### alt1.py end


def find_successors(e_tokens, phrases, end_index, orientation):
    """ Returns all the phrases that start after the word that ends in end_index
    :param e_tokens:
    :param phrases:
    :param end_index:
    """
    successor_phrases = []
    if orientation == 'lr':
        if end_index != len(e_tokens) - 1:  # not end of sentence
            start_word = e_tokens[end_index + 1]  # TODO this might go out of bounds
            for phr in phrases:
                if phr.startswith(start_word + ' '):
                    # TODO what happens in case we have more occurences of the same word in a sentence
                    successor_phrases.append(phr)
    if orientation == 'rl':
        if end_index != 0:  # not end of sentence
            start_word = e_tokens[end_index - 1]  # TODO this might go out of bounds
            for phr in phrases:
                if phr.endswith(' ' + start_word):
                    # TODO what happens in case we have more occurences of the same word in a sentence
                    successor_phrases.append(phr)
    return successor_phrases


def find_single_successor(e_f, sentence_tokens, word_ind, orientation):
    """ Find single word successor
    :param sentence_tokens:
    :param word_ind:
    :return:
    """
    if orientation == 'lr':
        if word_ind == len(sentence_tokens) - 1:  # end of sentence
            return None
        else:
            return get_phrase_containing(e_f, sentence_tokens[word_ind + 1], sentence_tokens[word_ind])
    else:
        if word_ind == 0:  # start of sentence
            return None
        else:
            return get_phrase_containing(e_f, sentence_tokens[word_ind - 1], sentence_tokens[word_ind])


def translate(aligned_phrases, word):
    """
    :param aligned_phrases:
    :param word:
    :return:
    """
    for pair in aligned_phrases:
        if pair[0] == word:
            return pair[1]
    min_ret_size = 10
    ret = None
    for pair in aligned_phrases:  # word hasn't been found, because of translation into multiple words
        if word not in pair[0]:
            continue
        if word in pair[0]:
            ret_size = len(pair[1])  # return shortest phrase, since aligned_phrases might contain word more often
            if ret_size < min_ret_size:
                ret = pair[1]
    return ret


def monotone(f_a, f_b, e_a, e_b, orientation):
    if f_a + 1 == f_b and e_a + 1 == e_b and orientation == 'lr':
        return True
    if f_a - 1 == f_b and e_a - 1 == e_b and orientation == 'rl':
        return True
    return False


def swap(f_a, f_b, e_a, e_b, orientation):
    if orientation == 'rl' and f_a + 1 == f_b and e_a == e_b + 1:
        return True
    if orientation == 'lr' and f_a == f_b + 1 and e_a + 1 == e_b:
        return True
    return False


def get_orientation(e_index, e_suc_index, f_index, f_suc_index, orientation):
    """ Determines the orientation for a given e-f pair
    :param e_index: source starting index
    :param e_suc_index: source successor index
    :param f_index: target starting index
    :param f_suc_index: target successor index
    :param orientation: rl, lr
    :return: String corresponding to the case ['mono', 'swap', 'discR', 'discL']
    """
    if monotone(f_index, f_suc_index, e_index, e_suc_index, orientation):
        return 'mono', abs(f_index - f_suc_index)
    if swap(f_index, f_suc_index, e_index, e_suc_index, orientation):
        return 'swap', abs(f_index - f_suc_index)
    # if discontinuous(f_index, f_suc_index, e_index, e_suc_index, orientation):
    # Discontinuous since not swap and not mono, no need to call 3 functions, 2 of which have been already called.
    if f_index < f_suc_index:  # TODO this is probably wrong? Comments are from Katja's mail.
        # - they have disc. RIGHT reordering if e2 immediately follows e1 (on the target side);
        # and on the source side f2 comes after f1 and there's a gap
        return 'discR', abs(f_index - f_suc_index)
    else:
        # they have discontinuous LEFT reordering if e2 immediately follows e1 (on the target side);
        # and on the source side f2 comes before f1, and there is a gap between them
        return 'discL', abs(f_index - f_suc_index)


def store_orientation(o, e, f, orientation):
    #assert (o in ['mono', 'swap', 'discR', 'discL'])  # TODO this is why we get zeros
    phrase_str = e + " ||| " + f
    if orientation == 'lr':
        if o == 'mono':
            global m_counter_lr
            m_counter_lr.update([phrase_str])
        elif o == 'swap':
            global s_counter_lr
            s_counter_lr.update([phrase_str])
        elif o == 'discR':
            global dr_counter_lr
            dr_counter_lr.update([phrase_str])
        elif o == 'discL':
            global dl_counter_lr
            dl_counter_lr.update([phrase_str])
    elif orientation == 'rl':
        if o == 'mono':
            global m_counter_rl
            m_counter_rl.update([phrase_str])
        elif o == 'swap':
            global s_counter_rl
            s_counter_rl.update([phrase_str])
        elif o == 'discR':
            global dr_counter_rl
            dr_counter_rl.update([phrase_str])
        elif o == 'discL':
            global dl_counter_rl
            dl_counter_rl.update([phrase_str])


def get_translation_indexes(index, suc_index, alignments):
    i = []
    suc_i = []
    for pair in alignments:
        if pair[0] == index:
            i.append(pair[1])
        if pair[0] == suc_index:
            suc_i.append(pair[1])
    return i, suc_i


def get_phrase_indexes(phrase, sentence_tokens):
    end = -1
    tmp = phrase.split()
    word_count = len(tmp)
    start_word = phrase if word_count == 0 else tmp[0]
    for start, token in enumerate(sentence_tokens):
        if token == start_word:
            if ' '.join(sentence_tokens[start:start + word_count]) == phrase:
                end = start + word_count - 1
                break
    return start, end


def get_phrase_containing(e_f, containing, not_containing=None):
    ret = None
    min_ret_size = sys.maxint
    for pair in e_f:
        if pair[0] == containing:
            return containing
        else:
            if (not_containing is None) or (not_containing not in pair[0]):
                if containing in pair[0]:
                    ret_size = len(
                        pair[0])  # return shortest phrase, since aligned_phrases might contain word more often
                    if ret_size < min_ret_size:
                        min_ret_size = ret_size
                        ret = pair[0]
    return ret


def word_based_orientation_extract(e_tokens, f_tokens, e_f, orientation):
    """ Updates the static variables containing the counts of the orientations by word based extraction
    :param e_tokens: tokens of source language
    :param f_tokens: tokens of target language
    :param e_f: phrase alignments
    :param orientation: rl, lr
    """
    direction = +1 if orientation == 'lr' else -1
    e_index = 0 if orientation == 'lr' else len(e_tokens) - 1
    while True:
        if orientation == 'lr' and e_index > len(e_tokens) - 1:  # termination conditions
            break
        if orientation == 'rl' and e_index < 0:
            break

        e_token = e_tokens[e_index]
        e = get_phrase_containing(e_f, e_token)
        if e is None:  # TODO remove comment e not in e_f, probably error in phrase extraction
            e_index += direction * 1
            continue
        e_start, e_end_ = get_phrase_indexes(e, e_tokens)
        e_end = e_end_ if orientation == 'lr' else e_start
        e_suc = find_single_successor(e_f, e_tokens, e_end, orientation)

        if e_suc is None:  # last word
            break
        f = translate(e_f, e)
        if f is not None:
            f_suc = translate(e_f, e_suc)
            if f_suc is not None:
                f_index, _ = get_phrase_indexes(f, f_tokens)
                f_suc_index, _ = get_phrase_indexes(f_suc, f_tokens)
                if f_index == f_suc_index:
                    pass
                if f_index is None or f_suc_index is None or f_index == f_suc_index:  # unaligned word
                    e_index += direction * len(e.split())
                    continue
                else:
                    o, distance = get_orientation(e_end, e_end + direction, f_index, f_suc_index, orientation)
                    phrase_size = len(f.split())
                    if distance > 9:
                        distance = 10
                    if orientation == 'rl':
                        if distance in distances_rl_w:
                            distances_rl_w[distance] += 1
                        else:
                            distances_rl_w[distance] = 1
                        if phrase_size < 8:
                            phrase_size_rl_w[phrase_size] += 1
                    if orientation == 'lr':
                        if o in distances_lr_w:
                            distances_lr_w[distance] += 1
                        else:
                            distances_lr_w[distance] = 1
                        if phrase_size < 8:
                            phrase_size_lr_w[phrase_size] += 1
                    store_orientation(o, e, f, orientation)
            else:
                print 'no f translation \'{}\', \'{}\' '.format(e, e_suc)
        e_index += direction * len(e.split())


def phrase_based_orientation_extract(e_phrases, f_phrases, e_tokens, f_tokens, e_f, orientation):
    for e in e_phrases:
        f = translate(e_f, e)

        e_start, e_end = get_phrase_indexes(e, e_tokens)
        f_start, f_end = get_phrase_indexes(f, f_tokens)
        if orientation == 'lr':
            e_sucs = find_successors(e_tokens, e_phrases, e_end, orientation)
        elif orientation == 'rl':
            e_sucs = find_successors(e_tokens, e_phrases, e_start, orientation)
        for e_suc in e_sucs:
            f_suc = translate(e_f, e_suc)
            if f_suc is None:
                continue

            e_suc_start, e_suc_end = get_phrase_indexes(e_suc, e_tokens)
            f_suc_start, f_suc_end = get_phrase_indexes(f_suc, f_tokens)

            if orientation == 'lr':
                o, distance = get_orientation(e_end, e_suc_start, f_end, f_suc_start, orientation)
            elif orientation == 'rl':
                o, distance = get_orientation(e_start, e_suc_end, f_start, f_suc_end, orientation)
            phrase_size = len(f.split())
            if distance > 9:
                distance = 10
            if orientation == 'rl':
                if distance in distances_rl_p:
                    distances_rl_p[distance] += 1
                else:
                    distances_rl_p[distance] = 1
                if phrase_size < 8:
                    phrase_size_rl_p[phrase_size] += 1
            if orientation == 'lr':
                if o in distances_lr_p:
                    distances_lr_p[distance] += 1
                else:
                    distances_lr_p[distance] = 1
                if phrase_size < 8:
                    phrase_size_lr_p[phrase_size] += 1
            store_orientation(o, e, f, orientation)


def generate_output(phrase_pairs, outfile=None):
    out = sys.stdout if outfile is None else open(outfile, 'w')
    try:
        m_rl_count = sum(m_counter_rl.values()) + .0
        dl_rl_count = sum(dl_counter_rl.values()) + .0
        dr_rl_count = sum(dr_counter_rl.values()) + .0
        s_rl_count = sum(s_counter_rl.values()) + .0
        m_lr_count = sum(m_counter_lr.values()) + .0
        dl_lr_count = sum(dl_counter_lr.values()) + .0
        dr_lr_count = sum(dr_counter_lr.values()) + .0
        s_lr_count = sum(s_counter_lr.values()) + .0
        for pp in phrase_pairs:
            p1 = float(get_count_of_orientation(m_counter_rl, pp)) / m_rl_count if m_rl_count > 0 else 0.0
            p2 = float(get_count_of_orientation(dl_counter_rl, pp)) / dl_rl_count if dl_rl_count > 0 else 0.0
            p3 = float(get_count_of_orientation(dr_counter_rl, pp)) / dr_rl_count if dr_rl_count > 0 else 0.0
            p4 = float(get_count_of_orientation(s_counter_rl, pp)) / s_rl_count if s_rl_count > 0 else 0.0
            p5 = float(get_count_of_orientation(m_counter_lr, pp)) / m_lr_count if m_lr_count > 0 else 0.0
            p6 = float(get_count_of_orientation(dl_counter_lr, pp)) / dl_lr_count if dl_lr_count > 0 else 0.0
            p7 = float(get_count_of_orientation(dr_counter_lr, pp)) / dr_lr_count if dr_lr_count > 0 else 0.0
            p8 = float(get_count_of_orientation(s_counter_lr, pp)) / s_lr_count if s_lr_count > 0 else 0.0
            string = '{0} ||| {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}'.format(pp, p1, p2, p3, p4, p5, p6, p7, p8)
            out.write(string + '\n')
    finally:
        if outfile is not None:
            out.close()


def get_count_of_orientation(counter, pair):
    count = counter.get(pair)
    return 0 if count is None else count


def orientation_extraction(e_path, f_path, aligned_path, max_length):
    sentence = 0
    phrase_pairs = set()
    with open(e_path, 'r') as e_f, open(f_path, 'r') as f_f, open(aligned_path, 'r') as aligned_f:
        sample_size = 2000
        for e_str, f_str, align_str in zip(e_f, f_f, aligned_f):
            e_tokens = e_str.strip().split()
            f_tokens = f_str.strip().split()

            alignments = parse_alignments(align_str)
            e_f, e_phrases, f_phrases = extract_phrases(e_tokens, f_tokens, alignments, max_length)

            # Store phrase pairs
            [phrase_pairs.add(" ||| ".join(pp)) for pp in e_f]

            # Word based
            word_based_orientation_extract(e_tokens, f_tokens, e_f, orientation='lr')
            word_based_orientation_extract(e_tokens, f_tokens, e_f, orientation='rl')
            # Phrase based
            phrase_based_orientation_extract(e_phrases, f_phrases, e_tokens, f_tokens, e_f, orientation='lr')
            phrase_based_orientation_extract(e_phrases, f_phrases, e_tokens, f_tokens, e_f, orientation='rl')

            sentence += 1
            if sentence % 100 == 0:
                print sentence

            sample_size -= 1
            if sample_size == 0:
                break
    print 'Phrases and orientations extracted'
    #generate_output(phrase_pairs, outfile='alt3.out')
    print distances_rl_p, distances_lr_p, distances_rl_w, distances_lr_w
    print phrase_size_lr_p, phrase_size_rl_p, phrase_size_lr_w, phrase_size_rl_w

# static vars
m_counter_rl = Counter()
dl_counter_rl = Counter()
dr_counter_rl = Counter()
s_counter_rl = Counter()
m_counter_lr = Counter()
dl_counter_lr = Counter()
dr_counter_lr = Counter()
s_counter_lr = Counter()
distances_rl_p = {}
distances_lr_p = {}
distances_rl_w = {}
distances_lr_w = {}
phrase_size_rl_p = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
phrase_size_lr_p = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
phrase_size_rl_w = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
phrase_size_lr_w = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}


def main():
    if len(sys.argv) != 4:
        print 'Usage: python alt3.py [e_file] [f_file] [aligned_file]'
        exit(-1)
    e_path = sys.argv[1]
    f_path = sys.argv[2]
    aligned_path = sys.argv[3]
    max_length = 7

    orientation_extraction(e_path, f_path, aligned_path, max_length)


if __name__ == '__main__':
    main()