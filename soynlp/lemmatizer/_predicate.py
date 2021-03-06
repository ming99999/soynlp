""" TERM DEFINITION
(l, r) : L and R position subwords
root : root of Adjective and Verb
ending : suffix, canonical form of ending

roots : set of root including Adjectives and Verbs
composable_roots : roots that can be compounded with other prefix
    - [] + 하다 : 덕질+하다, 냐옹+하다, 냐옹+하냥
endings : set of ending
pos_l_features : canonical form set of roots (L subwords)
pos_composable_l_features : canonical form set of composable roots (L subwords)
lrgraph : L-R graph including [Root + Ending], Adverbs, 
          and maybe some Noun + Josa
"""

from soynlp.utils import LRGraph
from soynlp.utils import get_process_memory
from soynlp.utils import EojeolCounter
from soynlp.utils.utils import installpath

class EomiExtractor:

    def __init__(self, nouns, noun_pos_features=None, roots=None, verbose=True):

        if not noun_pos_features:
            noun_pos_features = self._load_default_noun_pos_features()

        if not roots:
            roots = self._load_default_roots()

        self.nouns = nouns
        self.pos_features = noun_pos_features
        self.roots = roots
        self.verbose = verbose
        self.lrgraph = None

    def _load_default_noun_pos_features(self):
        path = '%s/trained_models/noun_predictor_ver2_pos' % installpath
        with open(path, encoding='utf-8') as f:
            pos_features = {word.split()[0] for word in f}
        return pos_features

    def _load_default_roots(self):
        dirs = '%s/lemmatizer/dictionary/default/Root' % installpath
        paths = ['%s/Adjective.txt', '%s/Verb.txt']
        paths = [p % dirs for p in paths]
        roots = set()
        for path in paths:
            with open(path, encoding='utf-8') as f:
                for line in f:
                    roots.add(line.split()[0])
        return roots

    @property
    def is_trained(self):
        return self.lrgraph

    def train(self, sentences, min_eojeol_count=2,
        filtering_checkpoint=100000):

        check = filtering_checkpoint > 0

        if self.verbose:
            print('[Eomi Extractor] counting eojeols', end='')

        # Eojeol counting
        counter = {}

        def contains_noun(eojeol, n):
            for e in range(2, n + 1):
                if eojeol[:e] in self.nouns:
                    return True
            return False

        for i_sent, sent in enumerate(sentences):

            if check and i_sent > 0 and i_sent % filtering_checkpoint == 0:
                counter = {
                    eojeol:count for eojeol, count in counter.items()
                    if count >= min_eojeol_count
                }

            if self.verbose and i_sent % 100000 == 99999:
                message = '\r[Eomi Extractor] n eojeol = {} from {} sents. mem={} Gb{}'.format(
                    len(counter), i_sent + 1, '%.3f' % get_process_memory(), ' '*20)
                print(message, flush=True, end='')

            for eojeol in sent.split():

                n = len(eojeol)

                if n <= 1 or contains_noun(eojeol, n):
                    continue

                counter[eojeol] = counter.get(eojeol, 0) + 1

        if self.verbose:
            message = '\r[Eomi Extractor] counting eojeols was done. {} eojeols, mem={} Gb{}'.format(
                len(counter), '%.3f' % get_process_memory(), ' '*20)
            print(message)

        counter = {
            eojeol:count for eojeol, count in counter.items()
            if count >= min_eojeol_count
        }

        self._num_of_eojeols = sum(counter.values())
        self._num_of_covered_eojeols = 0

        if self.verbose:
            print('[Eomi Extractor] complete eojeol counter -> lr graph')

        self.lrgraph = EojeolCounter()._to_lrgraph(
            counter,
            l_max_length=10,
            r_max_length=9
        )

        if self.verbose:
            print('[Eomi Extractor] has been trained. mem={} Gb'.format(
                '%.3f' % get_process_memory()))

def predict_r(r, minimum_r_score=0.3, debug=False):
    raise NotImplemented

def _predict_r(features, r):
    raise NotImplemented

def _exist_longer_l(l, r):
    raise NotImplemented

def _has_composable_l(l, r):
    raise NotImplemented

def _refine_features(features, r):
    return [(l, count) for l, count in features if
        (l in pos_l_features and not _exist_longer_l(l, r))]