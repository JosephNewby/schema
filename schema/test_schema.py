from unittest import TestCase
import schema


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


class TestFindTheMostAccurateMeaningOfACategoryGivenItsContext(TestCase):

    def test_returns_most_accurate_definition_for_tubs(self):
        category = 'Tubs'
        context = ['Home Improvement']
        expected_definition = 'a relatively large open container that you fill with water and use to wash the body';
        synset = schema.find_the_most_accurate_meaning_of_a_category_given_its_context(category, context)
        self.assertEqual(expected_definition, synset.definition())