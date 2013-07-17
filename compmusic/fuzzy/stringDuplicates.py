import lcs
import damerauLevenshtein as levenshtein

def _stripChars(word, chars):
	"""
	_stripChars(word, chars)
	
	This functions removes all the occurrences of specified characters from
	a word. The arguments word and chars should be string and list
	respectively.
	"""
	result = ""
	for char in word:
		if char not in chars:
			result = result+char
	return result

def _similarity(x, y):
	"""
	_similarity(x, y)
	
	This function measures string similarity between x and y.
	The function returns:
	0.8*(len(LongestCommonSubsequence(x, y))) + 
	0.2*1/(DamerauLevenshteinDistance(x, y))
	
	LCS and Levenshtein are, by trial and error, found to be 
	compensating for each others errors. Hence their combination
	in most cases seems to be one of the good solutions.
	 
	Eg: For Abhogi and Behag, LCS gives a high similarity
	score of 3, which is balanced by the Levenshtein's distance
	of 4, thus penalizing it.
	"""

	len_thresh = 0.75 
	# beyond this difference of ratio between lengths, they are deemed different terms

	if len(y) == 0:
		return 0
	ratio = 1.0*len(x)/len(y)
	if ratio > 1:
		ratio = 1/ratio;
	if ratio < len_thresh:
		return 0

	subseq = lcs.lcs(x, y)
	dldist = levenshtein.dameraulevenshtein(x, y)
	if dldist == 0:
		dldist = 1
		
	w1 = 0.8
	w2 = 0.2
	return w1*(1.0*len(subseq)/max([len(x), len(y)])) + (w2*1.0/dldist);
	
def stringDuplicates(term, origTerms, simThresh=0.8, n=100, stripped=False, recursion=2):
	"""
	Parameters:
	
	stringDuplicates(term="all", origTerms, simThresh=0.8, n=100, stripped=False, recursion=2)
	
	term: The default value is "all", in which case the matches for 
	all the	terms are output. If a specific term name is given, only
	its nearest	matches are output.
	
	origTerms: The list of all the terms to be matched against. 
	
	simThresh: Similarity threshold. Increasing it emphasizes that for
	two term names to be deemed similar, the constraints are higher.
	
	n: Max number of results.
	
	stripped: If True, all the terms are stripped off the vowels and 'h'
	before comparison.
	
	recursion: If it is 1, the immediate matches only are returned. 
	If it is 2, The matches for the matched term names are also
	included, and so on.
	
	Return values:
	For term = "all", a dictionary with of the format {"term": [match1, match2, ...]}
	For a specific term name, a list of duplicates.
	"""
	terms = origTerms[:]
	if recursion <= 0: return
	
	if term == "all":
		duplicates = {}
		analyzed = []
		for r in terms:
			if r not in analyzed:
				duplicates[r] = stringDuplicates(r, terms, simThresh, n, stripped, recursion)
				analyzed.extend(duplicates[r])
				analyzed = list(set(analyzed))
			else: continue
		return duplicates
	else:
		unwantedChars = ['a', 'e', 'i', 'o', 'u', 'h', ' ']
		strippedTerms = []
		if stripped:
			term = _stripChars(term, unwantedChars)
			for i in terms:
				strippedTerms.append(_stripChars(i, unwantedChars))
		else:
			strippedTerms = terms
		l = len(strippedTerms)
		
		similarities = [0] * l
		for i in xrange(0, l):
			similarities[i] = _similarity(term, strippedTerms[i])
		
		duplicates = []
		if n > l: n = l
		for i in xrange(n):
			ind = similarities.index(max(similarities))
			s = similarities.pop(ind)
			term_match = terms.pop(ind)
			if s >= simThresh:
				duplicates.append(term_match)
				if recursion > 1:
					nextNearest = stringDuplicates(term_match, terms, simThresh, n, stripped, recursion-1)
					if nextNearest:
						duplicates.extend(nextNearest)
						del nextNearest
		return list(set(duplicates))