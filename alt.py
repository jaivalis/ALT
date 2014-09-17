import sys
from collections import Counter


def extract_phrases(e_str, f_str, alignments, max_length):
    aligned_phrases = Counter()
    e_phrases = Counter()
    f_phrases = Counter()
    e_tokens = e_str.strip().split()
    f_tokens = f_str.strip().split()

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
            print tmp
            print type(tmp)
            phrase_alignment = tmp[0]
            e_phrase = tmp[1]
            f_phrase = tmp[2]
            
            aligned_phrases.update(phrase_alignment)
            e_phrases.update(e_phrase)
            f_phrases.update(f_phrase)
    return (aligned_phrases, e_phrases, f_phrases)


def get_phrase_alignment(e_start, e_end, f_start, f_end, alignments, e_tokens, f_tokens):
    if f_end < 0:
        return {}

    for f, e in alignments:
        if (f_start <= f <= f_end) and (e < e_start or e > e_end):
            return {}

    aligned_phrases = set()
    e_phrases       = set()
    f_phrases       = set()

    f_aligned = [j for _, j in alignments]

    f_s = f_start
    while True:
        f_e = f_end
        while True:
            # add phrase pair (e_start, e_end, f_start, f_end) to returned
            e_phrase = ' '.join(e_tokens[e_start:e_end+1])
            f_phrase = ' '.join(f_tokens[f_s:f_e+1])

            aligned_phrases.add((e_phrase, f_phrase))
            e_phrases.add(e_phrase)
            f_phrases.add(f_phrase)

            f_e += 1
            if f_e in f_aligned or f_e == len(f_tokens):  # until f_e aligned
                break
        f_s -= 1
        if f_s in f_aligned or f_s < 0:  # until f_s aligned
            break
    return (aligned_phrases, e_phrases, f_phrases)


def generate_output(phrase_counter, e_phrases, f_phrases, outfile=None):
    """ Generates the formatted output given the phrase counter as asked:

            f ||| e ||| freq(f) freq(e) freq(f, e)
    FIXME
    """

    if outfile is None:
        out = sys.stdout
    else:
        out = open(outfile, 'w')
    try:
        e_phrases_count   = sum(e_phrases.values())
        f_phrases_count   = sum(f_phrases.values())
        all_phrases_count = sum(phrase_counter.values())
        for tupl, count in phrase_counter.iteritems():
            e = tupl[0]
            f = tupl[1]

            freq_f = float(count) / f_phrases_count
            freq_e = float(count) / e_phrases_count
            freq_fe = -1

            string = "{0} ||| {1} {2:.6f} {3:.6f}".format(f, e, freq_f, freq_e, freq_fe)
            out.write(string + '\n')

    finally:
        if outfile is not None:
            out.close()


def extract_word_pairs(e_tokens, f_tokens, alignments):
    ret = set()
    for f, e in alignments:
        ret.add((f_tokens[f], e_tokens[e]))
    return ret


def parse_alignments(alignments_str):
    """ Parse an alignment string line into a set containing the pairs of the pairs

    """
    ret = set()
    alignments = alignments_str.strip().split()

    for al in alignments:
        num1, num2 = al.split('-')
        ret.add((int(num1), int(num2)))

    return ret


def phrase_extraction(e_path, f_path, aligned_path, max_length):
    # alignments_for_phrases = dict()

    phrase_pairs = Counter()

    e_phrases = Counter()
    f_phrases = Counter()
    all_phrases_counter = Counter()

    with open(e_path, 'r') as e_f, open(f_path, 'r') as f_f, open(aligned_path, 'r') as aligned_f:
        sample_size = 10
        for e_str, f_str, align_str in zip(e_f, f_f, aligned_f):

            alignments = parse_alignments(align_str)

            tmp = extract_phrases(e_str, f_str, alignments, max_length)
            phrases_counter = tmp[0]
            e_phrases_counter = tmp[1]
            f_phrases_counter = tmp[2]
            all_phrases_counter.update(phrases_counter)
            e_phrases.update(e_phrases_counter)
            f_phrases.update(f_phrases_counter)

            sample_size -= 1
            if sample_size == 0:
                break
    print 'Phrases extracted'
    generate_output(all_phrases_counter, e_phrases, f_phrases, 'file.out')


def main():
    if len(sys.argv) != 4:
        print 'Usage: python alt.py [e_file] [f_file] [aligned_file]'
        exit()

    e_path = sys.argv[1]
    f_path = sys.argv[2]
    aligned_path = sys.argv[3]
    max_length = 7

    phrase_extraction(e_path, f_path, aligned_path, max_length)

# 1\ Phrase extraction algorithm. Output: program and file with extracted phrases.
#    The file should be of the form:  f ||| e ||| freq(f) freq(e) freq(f,e)
# 2\ Phrase translation probabilities: p(f|e) and p(f|e). Output:
#    program and file of the form: f ||| e ||| p(f|e) p(e|f)
# 3\ Lexical translation probabilities (Koehn-Marcu-Och approach).
#    Output: program and file of the form: f ||| e ||| p(f|e) p(e|f) l(f|e) l(e|f)
# 4\ The resulting files of (1-3) can be combined into one single file of the form:

if __name__ == '__main__':
    main()