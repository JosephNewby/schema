from __future__ import division

import itertools, re, Levenshtein
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance
from nltk.corpus import wordnet as wn

''' Rewrites of the major algorithms from the white paper '''


def check_if_list_contains_a_semantic_match_for_target_word(target_word, list_of_words):
    if not target_word or not list_of_words:
        return False

    target_word_components = split_composite_word(target_word)
    product = itertools.product(list_of_words, target_word_components)

    for (word, target_word_component) in product:
        if these_words_are_similar(word, target_word_component):
            return True

    return False


def these_words_are_similar(word_a, word_b):
    if not word_b or not word_b:
        return False

    min_percent_of_similarities = 0.8

    number_of_character_differences = Levenshtein.distance(word_a, word_b)

    length_of_longest_word = max(len(word_a), len(word_b))

    percentage_of_similarities = 1 - number_of_character_differences / length_of_longest_word

    return percentage_of_similarities >= min_percent_of_similarities


def split_composite_word(word):
    delimiters = ', | & | and '
    lowercase_word = word.lower()
    return re.split(delimiters, lowercase_word)


def find_the_most_accurate_meaning_of_a_category_given_its_context(category, context):
    """
    Disambiguation
    """
    highest_sense_score = 0
    synset_with_the_highest_sense_score = None

    for category_synset in wn.synsets(category):
        sense_score = 0
        related_synsets = get_related_synsets(category_synset)

        product = itertools.product(related_synsets, context)

        for (related_synset, context_word) in product:
            gloss = related_synset.definition()
            sense_score += _longest_common_substring(gloss, context_word)

        if sense_score > highest_sense_score:
            highest_sense_score = sense_score
            synset_with_the_highest_sense_score = category_synset

    return synset_with_the_highest_sense_score


def get_related_synsets(synset):
    related_synsets = [synset]
    related_synsets.extend(synset.hypernyms())
    related_synsets.extend(synset.hyponyms())
    related_synsets.extend(synset.part_meronyms())
    related_synsets.extend(synset.part_holonyms())
    return related_synsets


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def _split_composite(w):
    ''' Splits composite category name w into a set of individual classes:
    a split term set W. '''
    m = re.split(', | & | and ', w)
    return set([s.lower() for s in m])


def _longest_common_substring(wa, wb):
    ''' Which computes the length of the longest common sequence of consecutive
    characters between two strings, corrected for length of the longest string,
    resulting in an index in the range [0; 1]. '''
    (s1, s2) = (wa, wb) if len(wa) > len(wb) else (wb, wa)
    m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in xrange(1, 1 + len(s1)):
        for y in xrange(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    lcs = s1[x_longest - longest: x_longest]
    return len(lcs) / len(s1)


def _contains_as_separate_component(wa, wb):
    ''' Indicates whether string wa contains string wb as separate part (middle
    of another word is not suffcient) '''
    if wb in wa:
        return True
    return False


class ExtendedSplitTermSet(object):
    ''' Generates a split term set for the given category, using parent
        and children as context. '''

    def __init__(self, wcategory, wparent, Wchildren):
        self.wcategory = wcategory
        self.wparent = wparent
        self.Wchildren = Wchildren

    def split_terms(self):
        ''' Returns the extended split term set. '''
        Wcategory = _split_composite(self.wcategory)
        Wparent = _split_composite(self.wparent) if self.wparent else set()
        Wchild = set()
        for w in self.Wchildren:
            Wchild = Wchild | _split_composite(w)
        Wcontext = Wchild | Wparent
        extendedSplitTermSet = set()
        for wsrcSplit in Wcategory:
            extendedTermSet = self.disambiguate(wsrcSplit, Wcontext)
            if extendedTermSet:
                extendedTermSet = set([l.name() for l in extendedTermSet.lemmas()])
                extendedTermSet = extendedTermSet | set([wsrcSplit])
                extendedSplitTermSet = extendedSplitTermSet | extendedTermSet
        return extendedSplitTermSet

    def disambiguate(self, w, Wcontext):
        ''' Disambiguates a word using a set of context words, resulting in a set of
        correct synonyms. '''
        z = self.get_synsets(w)
        bestscore = 0
        bestsynset = None
        for s in z:
            sensescore = 0
            r = set(self.get_related(s))
            p = itertools.product(r, Wcontext)
            for (sr, w) in p:
                gloss = self.get_gloss(sr)
                sensescore += _longest_common_substring(gloss, w)
            if sensescore > bestscore:
                bestscore = sensescore
                bestsynset = s
        return bestsynset

    def get_synsets(self, w):
        ''' Gives all synonym sets (representing one sense in WordNet), of which word
        w is a member. '''
        return wn.synsets(w)

    def get_related(self, S):
        ''' Gives synonym sets directly related to synset S in WordNet, based on
        hypernymy, hyponymy, meronymy and holonymy. Result includes synset S as well.
        '''
        related = [S]
        related.extend(S.hypernyms())
        related.extend(S.hyponyms())
        related.extend(S.part_meronyms())
        related.extend(S.part_holonyms())
        return related

    def get_gloss(self, S):
        ''' Returns the gloss associated to a synset S in WordNet. '''
        return S.definition()


class SemanticMatcher(object):
    ''' Semantic matcher class. '''

    def match(self, E, wtarget, tnode):
        ''' Returns true if a semantic match exists between the ExtendedSplitTermSet (E)
        and wtarget, with a node matching threshold specified by tnode. '''
        Wtarget = _split_composite(wtarget)
        subSetOf = True
        if not E:
            return False
        for SsrcSplit in E:
            matchFound = False
            p = itertools.product([SsrcSplit], Wtarget)
            for (wsrcSplitSyn, wtargetSplit) in p:
                edit_dist = Levenshtein.distance(unicode(wsrcSplitSyn), unicode(wtargetSplit))
                similarity = 1 - edit_dist / max(len(wsrcSplitSyn), len(wtargetSplit))
                if _contains_as_separate_component(wsrcSplitSyn, wtargetSplit):
                    matchFound = True
                elif similarity >= tnode:
                    matchFound = True
            if matchFound == False:
                subSetOf = False
        return subSetOf


class SourceNode(object):
    ''' Repesents a node in the source path. '''

    def __init__(self, wcategory, wparent, Wchildren):
        self.key = None
        self.wcategory = wcategory
        self.wparent = wparent
        self.Wchildren = Wchildren
        self.m = SemanticMatcher()

        e = ExtendedSplitTermSet(wcategory, wparent, Wchildren)
        self.split_terms = e.split_terms()

    def __repr__(self):
        return str("{0}".format(self.wcategory))

    def __eq__(self, target):
        ''' Two source nodes are equal if their extended split terms are the
            equivalent.'''
        return self.split_terms == target.split_terms

    def matches_candidate(self, candidate_node, tnode):
        return self.m.match(self.split_terms, candidate_node.wtarget, tnode)


class Path(object):
    ''' Repesents a path, which is an ordered list of node objects. '''

    def __init__(self):
        self.nodes = []

    def __iter__(self):
        return iter(self.nodes)

    def __getitem__(self, key):
        return self.nodes.__getitem__(key)

    def __repr__(self):
        return str(self.nodes)

    def add_node(self, node):
        ''' Add a SourceNode object to the path. '''
        self.nodes.append(node)
        return self


class CandidateNode(object):
    ''' Repesents a node in the candidate path. '''

    def __init__(self, wtarget):
        self.key = None
        self.wtarget = wtarget

    def __repr__(self):
        return self.wtarget


class KeyPathGenerator(object):
    ''' Candidate Target Path Key Generator '''

    def __init__(self, source_path, candidate_paths):
        self.source_path = source_path
        self.candidate_paths = candidate_paths
        self.matched_candidate_paths = []
        self.node_key_counter = 0
        self.tnode = 0.8

        self._key_source_path(source_path)
        self.matched_candidate_paths = self._match_candidate_paths(candidate_paths)

        for candidate_path in self.matched_candidate_paths:
            self._key_candidate_path(candidate_path)

    def _key_source_path(self, source_path):
        """
        Returns a keyed source path for the given source path.
        """
        for i, a in enumerate(source_path):
            if i == 0:
                if a.key is None:
                    a.key = unichr(self.node_key_counter)
                    self.node_key_counter += 1
            for j, b in enumerate(source_path[i + 1:]):
                if a == b:
                    b.key = a.key
                    break
                else:
                    if b.key is None:
                        b.key = unichr(self.node_key_counter)
                        self.node_key_counter += 1

    def source_key_path(self):
        """ Returns the source key path. """
        path = [n.key for n in self.source_path]
        return ''.join(path) if len(path) > 1 else path[0]

    def matched_candidate_key_paths(self):
        ''' Returns a tuple containing a list of candidate key paths and their
            matching candidate paths. '''
        keyed_paths = []
        matched_paths = []
        for candidate_path in self.matched_candidate_paths:
            path = [n.key for n in candidate_path]
            path = ''.join(path) if len(path) > 1 else path[0]
            keyed_paths.append(path)
            matched_paths.append(candidate_path)
        return (keyed_paths, matched_paths)

    def _match_candidate_paths(self, candidate_paths):
        ''' Returns the list of candidate paths that match the source path. '''
        matched_candidate_paths = set()
        for candidate_path in candidate_paths:
            m = self._match_candidate_path(candidate_path)
            if m is True:
                matched_candidate_paths.update([candidate_path])
                continue
        return matched_candidate_paths

    def _match_candidate_path(self, candidate_path):
        for a in self.source_path:
            for b in candidate_path:
                if a.matches_candidate(b, self.tnode):
                    return True

    def _key_candidate_path(self, candidate_path):
        ''' Returns a keyed candidate path for the given candidate path. '''
        matchFound = False

        for a in self.source_path:
            for b in candidate_path:
                if a.matches_candidate(b, self.tnode):
                    b.key = a.key
                    matchFound = True

        for b in candidate_path:
            if b.key is None:
                b.key = unichr(self.node_key_counter)
                self.node_key_counter += 1


class KeyPathRanker(object):
    ''' Candidate Target Key Path Ranker '''

    def rank(self, src, tgt):
        ''' Returns the rank of the source and target paths. '''
        p = len(set(tgt) - set(src))
        a = normalized_damerau_levenshtein_distance(unicode(src), unicode(tgt)) + p
        b = max(len(src), len(tgt)) + p
        candidateScore = 1 - (a / b)
        return candidateScore
