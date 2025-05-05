from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDRegressor
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
import random
from .letters import Letter, parse_word, to_disp_word, generate_word

def extract_features(word: list[Letter] | str):
    if isinstance(word, str):
        word = parse_word(word)
    length = len(word)
    rhythm = ["-" if i > 0 and l.soft else "+" for i, l in enumerate(word)]
    soft_count = rhythm.count("-")
    special_count = len([l for l in word if l.special])
    y_count = len([l for l in word if l.is_y])
    w_count = len([l for l in word if l.is_w])
    jp_2chars_count = len([l for l in word if len(l.letter) > 1])
    
    consonants = [l.consonant or "A" for l in word if l.consonant is not None]
    consonant_classes = [l.consonant_class or "A" for l in word if l.consonant_class is not None]
    vowels = [l.vowel for l in word if l.vowel]
    jp_lengths = [len(l.letter) for l in word]
    yw_classes = ["s" if l.special else "y" if l.is_y else "w" if l.is_w else "n" for l in word]
    vowel_yw_classes = ["-" if l.special else "y" + l.vowel if l.is_y else "w" + l.vowel if l.is_w else l.vowel for l in word]
    
    ngram_features = {}
    def add_ngram_count(key):
        ngram_features[key] = min(ngram_features.get(key, 0) + 1, 2)
    def add_2grams(lst, key):
        grams = [f"{lst[i]}_{lst[i+1]}" for i in range(len(lst) - 1)]
        for gram in grams:
            add_ngram_count(f"{key}:{gram}")
    add_2grams(consonants, "consonant_2gram")
    add_2grams(consonant_classes, "consonant_class_2gram")
    add_2grams(vowels, "vowel_2gram")
    add_2grams(jp_lengths, "jp_length_2gram")
    add_2grams(yw_classes, "yw_class_2gram")
    add_2grams(vowel_yw_classes, "vowel_yw_class_2gram")
    add_2grams([l.letter for l in word], "letter_2gram")
    add_2grams(rhythm, "rhythm_2gram")
    
    features = {
        "length": length,
        "soft_ratio": soft_count / length,
        "special_ratio": special_count / length,
        "y_count": y_count,
        "w_count": w_count,
        "jp_2chars_count": jp_2chars_count,
        "jp_length": sum(jp_lengths),
        f"rhythm_startswith:{''.join(rhythm[:2])}": 1,
        f"rhythm_endswith:{''.join(rhythm[-2:])}": 1,
        f"startswith:{word[0].letter}": 1,
        f"endswith:{word[-1].letter}": 1,
        f"consonant_startswith:{word[0].consonant}": 1,
        f"consonant_endswith:{word[-1].consonant}": 1,
        f"vowel_startswith:{word[0].vowel}": 1,
        f"vowel_endswith:{word[-1].vowel}": 1,
        **ngram_features,
    }
    return features

def convert_to_features(words: list[list[Letter]] | list[str]):
    features = [extract_features(w) for w in words]
    return features

class NumericSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return [{k: v for k, v in sample.items() if ":" not in k} for sample in X]

class CategoricalSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return [{k: v for k, v in sample.items() if ":" in k} for sample in X]
    
def create_model(words_with_preference: list[tuple[list[Letter] | str, float]]):
    words = [w[0] for w in words_with_preference]
    preferences = [w[1] for w in words_with_preference]
    features = convert_to_features(words)
    pipeline = Pipeline([
        ("features", FeatureUnion([
            ("num", Pipeline([
                ("select", NumericSelector()),
                ("vec", DictVectorizer()),
                ("scaler", StandardScaler(with_mean=False)),
            ])),
            ("cat", Pipeline([
                ("select", CategoricalSelector()),
                ("vec", DictVectorizer()),
                ("tfidf", TfidfTransformer()),
            ])),
        ])),
        ("reg", SGDRegressor()),
    ])
    pipeline.fit(features, preferences)
    return pipeline

def evaluate_words(words: list[list[Letter]] | list[str], pipeline: Pipeline):
    features = convert_to_features(words)
    scores = pipeline.predict(features)
    disp_words = [w if isinstance(w, str) else to_disp_word(w) for w in words]
    ranked = sorted(zip(disp_words, scores), key=lambda x: -x[1])
    return ranked

def pick_candidates(num, pipeline: Pipeline):
    eval_words = [generate_word() for _ in range(num * 100)]
    ranked = evaluate_words(eval_words, pipeline)
    # for w, s in ranked[:num*50]:
    #     print(f"{w}  {s}")
    sorted_words = [w[0] for w in ranked]
    top_count = int(num * 0.9)
    other_count = num - top_count
    top_candidates = random.sample(sorted_words[:num*3], top_count)
    other_candidates = random.sample(sorted_words[num*3:], other_count)
    candidates = [*top_candidates, *other_candidates]
    random.shuffle(candidates)
    return candidates