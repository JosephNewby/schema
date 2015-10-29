from unittest import TestCase
import schema

"""
    Example usage:

    import schema

    # create source and candidate paths
    source_path     =  schema.Path().add_node(..)
    candidate_paths = [schema.Path().add_node(..), ..]

    # generate key paths and match
    keypathgen = schema.KeyPathGenerator(source_path, candidate_paths)
    source_key_path                  = keypathgen.source_key_path()
    matched_key_paths, matched_paths = keypathgen.matched_candidate_key_paths()

    # rank and print results
    ranker = schema.KeyPathRanker()
    for i,candidate_key_path in enumerate(matched_key_paths):
        rank = ranker.rank(source_key_path, candidate_key_path)
        print rank, matched_paths[i]

"""


class TestSchema(TestCase):
    def setUp(self):
        source_path = schema.Path()
        source_path.add_node(schema.SourceNode('Online Shopping', '', ['Books & Media']))
        source_path.add_node(schema.SourceNode('Books & Media', 'Online Shopping', ['Books']))
        source_path.add_node(schema.SourceNode('Books', 'Books & Media', ['Humor Books']))
        source_path.add_node(schema.SourceNode('Humor Books', 'Books', []))

        self.source_path = source_path

        candidate_path_books = schema.Path()
        candidate_path_books.add_node(schema.CandidateNode('Products'))
        candidate_path_books.add_node(schema.CandidateNode('Books'))

        self.candidate_path_books = candidate_path_books

        candidate_path_media = schema.Path()
        candidate_path_media.add_node(schema.CandidateNode('Products'))
        candidate_path_media.add_node(schema.CandidateNode('Media'))
        candidate_path_media.add_node(schema.CandidateNode('Humor'))

        self.candidate_path_media = candidate_path_media

    def test_generating_source_key_path(self):
        candidate_paths = [self.candidate_path_books, self.candidate_path_media]

        key_path_generator = schema.KeyPathGenerator(self.source_path, candidate_paths)

        source_key_path = key_path_generator.source_key_path()
        print source_key_path

    def test_example_usage(self):
        candidate_paths = [self.candidate_path_books, self.candidate_path_media]

        key_path_generator = schema.KeyPathGenerator(self.source_path, candidate_paths)

        source_key_path = key_path_generator.source_key_path()
        matched_key_paths, matched_paths = key_path_generator.matched_candidate_key_paths()

        key_path_ranker = schema.KeyPathRanker()

        print matched_key_paths

        for index, candidate_key_path in enumerate(matched_key_paths):
            print source_key_path
            print candidate_key_path
            rank = key_path_ranker.rank(source_key_path, candidate_key_path)
            print rank
            print matched_key_paths[index]

    def test_mapping_tubs(self):
        source_path = schema.Path()
        source_path.add_node(schema.SourceNode('Online Shopping', '', ['Home & Garden', 'Home Improvement', 'Tubs']))
        source_path.add_node(schema.SourceNode('Home & Garden', 'Online Shopping', ['Home Improvement', 'Tubs']))
        source_path.add_node(schema.SourceNode('Home Improvement', 'Home & Garden', ['Tubs']))
        source_path.add_node(schema.SourceNode('Tubs', 'Home Improvement', []))

        candidate_1 = schema.Path()
        candidate_1.add_node(schema.CandidateNode('Products'))
        candidate_1.add_node(schema.CandidateNode('Home, Garden & Tools'))
        candidate_1.add_node(schema.CandidateNode('Kitchen & Bath Fixtures'))

        candidate_2 = schema.Path()
        candidate_2.add_node(schema.CandidateNode('Products'))
        candidate_2.add_node(schema.CandidateNode('Home, Garden & Tools'))
        candidate_2.add_node(schema.CandidateNode('Tools & Home Improvement'))
        candidate_2.add_node(schema.CandidateNode('Kitchen & Bath Fixtures'))

        candidate_3 = schema.Path()
        candidate_3.add_node(schema.CandidateNode('Products'))
        candidate_3.add_node(schema.CandidateNode('Toys, Kids & Baby'))
        candidate_3.add_node(schema.CandidateNode('Baby'))
        candidate_3.add_node(schema.CandidateNode('Bathing'))
        candidate_3.add_node(schema.CandidateNode('Bathing tubs'))

        candidate_4 = schema.Path()
        candidate_4.add_node(schema.CandidateNode('Products'))
        candidate_4.add_node(schema.CandidateNode('Home, Garden & Tools'))
        candidate_2.add_node(schema.CandidateNode('Tools & Home Improvement'))
        candidate_4.add_node(schema.CandidateNode('Hardware'))
        candidate_4.add_node(schema.CandidateNode('Bath Hardware'))

        candidate_paths = [candidate_1, candidate_2, candidate_3, candidate_4]

        print source_path, candidate_paths

        key_path_generator = schema.KeyPathGenerator(source_path, candidate_paths)

        source_key_path = key_path_generator.source_key_path()
        matched_key_paths, matched_paths = key_path_generator.matched_candidate_key_paths()

        print source_key_path, matched_paths, matched_key_paths

        key_path_ranker = schema.KeyPathRanker()

        for index, candidate_key_path in enumerate(matched_key_paths):
            print index, key_path_ranker.rank(source_key_path, candidate_key_path)


class TestCheckIfListContainsASemanticMatchForTargetWord(TestCase):
    def setUp(self):
        self.list_of_words = [u'someone', u'roomy']

    def test_returns_true_for_100_percent_match(self):
        semantic_match_found = schema.check_if_list_contains_a_semantic_match_for_target_word(u'someone',
                                                                                              self.list_of_words)
        self.assertTrue(semantic_match_found)

    def test_returns_true_for_80_percent_match(self):
        semantic_match_found = schema.check_if_list_contains_a_semantic_match_for_target_word(u'room',
                                                                                              self.list_of_words)
        self.assertTrue(semantic_match_found)

    def test_returns_false_for_less_than_80_percent_match(self):
        semantic_match_found = schema.check_if_list_contains_a_semantic_match_for_target_word(u'some',
                                                                                              self.list_of_words)
        self.assertFalse(semantic_match_found)

    def test_returns_false_when_target_word_is_falsy(self):
        semantic_match_found = schema.check_if_list_contains_a_semantic_match_for_target_word(u'', self.list_of_words)
        self.assertFalse(semantic_match_found)

    def test_returns_false_when_list_of_words_is_falsy(self):
        semantic_match_found = schema.check_if_list_contains_a_semantic_match_for_target_word(u'someone', [])
        self.assertFalse(semantic_match_found)


class TestTheseWordsAreSimilar(TestCase):
    def test_returns_true_when_both_words_are_identical(self):
        identical_word = 'friend'
        self.assertTrue(schema.these_words_are_similar(identical_word, identical_word))

    def test_returns_true_when_80_percent_of_the_characters_in_two_words_match(self):
        word_a = 'word'
        word_b = 'words'
        self.assertTrue(schema.these_words_are_similar(word_a, word_b))

    def test_returns_false_when_either_word_is_falsy(self):
        word = ''
        self.assertFalse(schema.these_words_are_similar(word, word))

    def test_returns_false_when_less_than_80_percent_of_the_characters_in_two_words_match(self):
        word_a = 'word'
        word_b = 'more words'
        self.assertFalse(schema.these_words_are_similar(word_a, word_b))
