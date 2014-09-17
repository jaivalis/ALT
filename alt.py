import sys
from collections import Counter

def extract_phrases(e_str, f_str, alignments, max_length):
	ret = Counter()
	e_tokens = e_str.strip().split()
	f_tokens = f_str.strip().split()

	word_alignments = extract_word_pairs(e_tokens, f_tokens, alignments)

	# extract_phrase_alignments(len(e_tokens), len(f_tokens), word_alignments, max_length)

	for e_start in range(0, len(e_tokens)):
		for e_end in range(e_start, len(e_tokens)):

			if e_end-e_start > max_length:
				continue
			
			f_start = len(f_tokens)
			f_end =  0

			for f, e in alignments:
				if e_start <= e <= e_end:
					f_start = min(f, f_start)
					f_end = max(f, f_end)

			phrase_alignment = get_phrase_alignment(e_start, e_end, f_start, f_end, alignments, e_tokens, f_tokens)

			ret.update(phrase_alignment)
	return ret

def get_phrase_alignment(e_start, e_end, f_start, f_end, alignments, e_tokens, f_tokens):
	if f_end < 0:
		return {}

	for f, e in alignments:
		if (f_start <= f <= f_end) and (e < e_start or e > e_end):
			return {}

	ret = set()
	f_s = f_start

	# e_aligned = [i for i,_ in alignments]
	f_aligned = [j for _,j in alignments]

	while True:
		f_e = f_end
		while True:
			# add phrase pair (e_start, e_end, f_start, f_end) to returned
			e_phrase = ' '.join(e_tokens[e_start : e_end+1])
			f_phrase = ' '.join(f_tokens[f_start : f_end+1])
			ret.add( (e_phrase, f_phrase) )

			if f_e in f_aligned:  # until f_e aligned
				break
			f_e += 1

		if f_s in f_aligned:  # until f_s aligned
			break
		f_s -= 1

	return ret

def generate_output(phrase_counter, outfile=None):
	""" Generates the formatted output given the phrase counter as asked:

			f ||| e ||| freq(f) freq(e) freq(f, e)
	FIXME
	"""

	if outfile is None:
		out = sys.stdout
	else:
		out = open(outfile, 'w')
	try:
		print phrase_counter
		for f, e in phrase_counter:
			count = 0

			freq_f = -1
			freq_e = -1
			freq_fe = -1

			string = "{0} ||| {1} {2} {3}".format(f, e, freq_f, freq_e, freq_fe)
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
	# phrase_pairs = Counter()
	# e_phrases = Counter()
	# f_phrases = Counter()

	sentense_count = -1

	all_phrases_counter = Counter()


	with open(e_path, 'r') as e_f, open(f_path, 'r') as f_f, open(aligned_path, 'r') as aligned_f:
		sample_size = 10
		for e_str, f_str, align_str in zip(e_f, f_f, aligned_f):

			alignments = parse_alignments(align_str)

			phrases_counter = extract_phrases(e_str, f_str, alignments, max_length)
			all_phrases_counter.update(phrases_counter)

			generate_output(all_phrases_counter)

			sample_size -= 1
			raw_input("bla: ")
			if sample_size == 0:
				break;

def main():

	if len(sys.argv) != 4:
		print 'Usage: python alt.py [e_file] [f_file] [aligned_file]'
		exit()

	e_path = sys.argv[1]
	f_path = sys.argv[2]
	aligned_path = sys.argv[3]
	max_length = 7

	phrase_extraction(e_path, f_path, aligned_path, max_length)


# 1\ Phrase extraction algorithm. Output: program and file with extracted phrases. The file should be of the form:  f ||| e ||| freq(f) freq(e) freq(f,e)
# 2\ Phrase translation probabilities: p(f|e) and p(f|e). Output: program and file of the form: f ||| e ||| p(f|e) p(e|f)
# 3\ Lexical translation probabilities (Koehn-Marcu-Och approach). Output: program and file of the form: f ||| e ||| p(f|e) p(e|f) l(f|e) l(e|f)
# 4\ The resulting files of (1-3) can be combined into one single file of the form:

if __name__=='__main__':
	main()