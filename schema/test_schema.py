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

    def test_example_usage(self):
        pass

"""
    from schema.worddisambiguation import list_all_sets_of_synonyms_for_the_word, get_related


    class TestListAllSetsOfSynonymsForTheWord(TestCase):
        def test_the_word_friend_has_5_sets_of_synonyms(self):
            sets_synonyms_for_the_word_friend = list_all_sets_of_synonyms_for_the_word('friend')
            self.assertEquals(5, len(sets_synonyms_for_the_word_friend))


    class TestGetRelated(TestCase):
        def test_friend_has_5_related_synonym(self):
            sets_synonyms_for_the_word_friend = list_all_sets_of_synonyms_for_the_word('friend')
            related = get_related(sets_synonyms_for_the_word_friend[0])
            self.assertEquals(5, len(related))
"""
