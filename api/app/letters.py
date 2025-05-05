from dataclasses import dataclass
from typing import Literal, List
import copy
import re
import random
import jaconv

@dataclass
class ConvLetter:
    letter: str
    alphabet: list[str]
    consonant: str
    vowel: str
    is_y: bool = False
    is_w: bool = False
    suffix: str = ""
    long_vowel: bool = False
    small_vowel: bool = False

SpecialChars = Literal["N", "Tu", "LongV", "SmallV"]

@dataclass
class Letter:
    letter: str
    weight: float
    consonant: str | None
    consonant_class: str | None
    vowel: str | None
    not_after: List[SpecialChars]
    is_y: bool = False
    is_w: bool = False
    soft: bool = False
    special: SpecialChars | None = None
    not_first: bool = False
    not_last: bool = False
       
@dataclass
class LetterSet:
    letters: list[str]
    alphabet: str
    vowels: str
    consonant: str
    consonant_class: str
    weights: list[float]
    not_after: list[SpecialChars]
    is_y: bool = False
    is_w: bool = False
    soft: bool = False
    
lettersets = [
    LetterSet(["あ", "い", "う", "え", "お"], "", "aiueo", "", "", [22, 26, 20, 24, 20], ["Tu"], soft=True),
    LetterSet(["や", "ゆ", "いぇ", "よ"], "y", "aueo", "", "", [5, 8, 2, 5], ["Tu"], is_y=True),
    LetterSet(["わ", "うぃ", "うぇ", "うぉ"], "w", "aieo", "", "", [4, 2, 2, 2], ["Tu"], is_w=True),
    LetterSet(["は", "ひ", "へ", "ほ"], "h", "aieo", "h", "h", [10, 8, 4, 4], ["Tu"]),
    LetterSet(["ひゃ", "ひゅ", "ひぇ", "ひょ"], "hy", "aueo", "h", "h", [1, 1, 1, 1], ["Tu"], is_y=True),
    LetterSet(["か", "き", "く", "け", "こ"], "k", "aiueo", "k", "k", [10, 7, 10, 5, 5], []),
    LetterSet(["きゃ", "きゅ", "きょ"], "ky", "auo", "k", "k", [1, 1, 1], [], is_y=True),
    LetterSet(["くぁ", "くぃ", "くぇ", "くぉ"], "qu", "aieo", "k", "k", [1, 1, 1, 1], [], is_w=True),
    LetterSet(["が", "ぎ", "ぐ", "げ", "ご"], "g", "aiueo", "g", "k", [5, 5, 5, 2, 2], []),
    LetterSet(["ぎゃ", "ぎゅ", "ぎょ"], "gy", "auo", "g", "k", [1, 1, 1], [], is_y=True),
    LetterSet(["ぐぁ", "ぐぃ", "ぐぇ", "ぐぉ"], "gw", "aieo", "g", "k", [1, 1, 1, 1], [], is_w=True),
    LetterSet(["ぱ", "ぴ", "ぷ", "ぺ", "ぽ"], "p", "aiueo", "p", "k", [5, 5, 3, 3, 3], []),
    LetterSet(["ぴゃ", "ぴゅ", "ぴょ"], "py", "auo", "p", "k", [1, 1, 1], [], is_y=True),
    LetterSet(["ば", "び", "ぶ", "べ", "ぼ"], "b", "aiueo", "b", "k", [2, 3, 1, 1, 1], []),
    LetterSet(["びゃ", "びゅ", "びょ"], "by", "auo", "b", "k", [1, 1, 1], [], is_y=True),
    LetterSet(["た", "てぃ", "とぅ", "て", "と"], "t", "aiueo", "t", "k", [4, 8, 7, 5, 4], []),
    LetterSet(["てゃ", "てゅ", "てょ"], "ty", "auo", "t", "k", [1, 1, 1], [], is_y=True),
    LetterSet(["だ", "でぃ", "どぅ", "で", "ど"], "d", "aiueo", "d", "k", [3, 6, 3, 3, 3], []),
    LetterSet(["でゅ"], "dy", "u", "d", "k", [1], [], is_y=True),
    LetterSet(["さ", "すぃ", "す", "せ", "そ"], "s", "aiueo", "s", "s", [10, 7, 10, 5, 5], []),
    LetterSet(["すゅ"], "sy", "u", "s", "s", [1], [], is_y=True),
    LetterSet(["ざ", "ずぃ", "ず", "ぜ", "ぞ"], "z", "aiueo", "z", "s", [5, 6, 7, 5, 5], []),
    LetterSet(["ずゅ"], "zy", "u", "z", "s", [1], [], is_y=True),
    LetterSet(["つぁ", "つぃ", "つ", "つぇ", "つぉ"], "ts", "aiueo", "ts", "s", [2, 2, 1, 1, 1], []),
    LetterSet(["つゅ"], "tsy", "u", "ts", "s", [1], [], is_y=True),
    # LetterSet(["づぁ", "づぃ", "づ", "づぇ", "づぉ"], "dz", "aiueo", "z", "s", [], []),
    # LetterSet(["づゅ"], "dzy", "u", "z", "s", [], [], is_y=True),
    LetterSet(["しゃ", "し", "しゅ", "しぇ", "しょ"], "sh", "aiueo", "sh", "s", [3, 2, 3, 3, 3], []),
    LetterSet(["じゃ", "じ", "じゅ", "じぇ", "じょ"], "j", "aiueo", "j", "s", [2, 3, 4, 2, 2], []),
    LetterSet(["ちゃ", "ち", "ちゅ", "ちぇ", "ちょ"], "ch", "aiueo", "ch", "s", [4, 5, 4, 3, 3], []),
    # LetterSet(["ぢゃ", "ぢ", "ぢゅ", "ぢぇ", "ぢょ"], "dj", "aiueo", "j", "s", [], []),
    LetterSet(["ふぁ", "ふぃ", "ふ", "ふぇ", "ふぉ"], "f", "aiueo", "f", "s", [3, 3, 8, 3, 3], []),
    LetterSet(["ふゃ", "ふゅ", "ふょ"], "fy", "auo", "f", "s", [1, 1, 1], [], is_y=True),
    LetterSet(["ゔぁ", "ゔぃ", "ゔ", "ゔぇ", "ゔぉ"], "v", "aiueo", "v", "s", [1, 2, 4, 1, 1], []),
    LetterSet(["ゔゅ"], "vy", "u", "v", "s", [1], [], is_y=True),
    LetterSet(["な", "に", "ぬ", "ね", "の"], "n", "aiueo", "n", "n", [10, 7, 5, 8, 8], ["Tu"]),
    LetterSet(["にゃ", "にゅ", "にぇ", "にょ"], "ny", "aueo", "n", "n", [1, 1, 1, 1], ["Tu"], is_y=True),
    LetterSet(["ま", "み", "む", "め", "も"], "m", "aiueo", "m", "n", [6, 7, 5, 7, 7], ["Tu"]),
    LetterSet(["みゃ", "みゅ", "みぇ", "みょ"], "my", "aueo", "m", "n", [1, 1, 1, 1], ["Tu"], is_y=True),
    LetterSet(["ら", "り", "る", "れ", "ろ"], "r", "aiueo", "r", "n", [10, 8, 12, 8, 5], ["Tu"]),
    LetterSet(["りゃ", "りゅ", "りょ"], "ry", "auo", "r", "n", [1, 1, 1], ["Tu"], is_y=True),
]

letters_for_parse = sum([
    [ConvLetter(ls.letters[i], [ls.alphabet, ls.vowels[i]], ls.consonant, ls.vowels[i], ls.is_y, ls.is_w)
     for i in range(len(ls.vowels))] for ls in lettersets
], [])

letters = sum(
    [
        [Letter(ls.letters[i], ls.weights[i], ls.consonant, ls.consonant_class, ls.vowels[i], ls.not_after, ls.is_y, ls.is_w, ls.soft)
            for i in range(len(ls.vowels))]
        for ls in lettersets
    ],
    [
        Letter("っ", 30, None, None, None, ["Tu", "N", "LongV"], soft=True, special="Tu", not_first=True, not_last=True),
        Letter("ん", 25, None, None, None, ["Tu", "N"], soft=True, special="N", not_first=True),
        Letter("ー", 12, None, None, None, ["Tu", "N", "LongV"], soft=True, special="LongV", not_first=True),
        Letter("～", 5, None, None, None, ["Tu", "N", "LongV", "SmallV"], soft=True, special="SmallV", not_first=True),
    ]
)

long_vowel_map = {"a": "ā", "i": "ī", "u": "ū", "e": "ē", "o": "ō"}
small_vowel_map = {"a": "ぁ", "i": "ぃ", "u": "ぅ", "e": "ぇ", "o": "ぉ"}

def parse_word_for_conv(word):
    word = jaconv.kata2hira(word)
    parsed_letters: list[ConvLetter] = []
    while word:
        if word[0] == "ん":
            parsed_letters[-1].suffix = "n"
            word = word[1:]
            continue
        if word[0] == "っ":
            parsed_letters[-1].suffix = "tu"
            word = word[1:]
            continue
        if word[0] == "ー":
            parsed_letters[-1].long_vowel = True
            word = word[1:]
            continue
        if word[0] in ["ぁ", "ぃ", "ぅ", "ぇ", "ぉ"]:
            parsed_letters[-1].small_vowel = True
            word = word[1:]
            continue
        found = False
        for l in sorted(letters_for_parse, key=lambda x: -len(x.letter)):
            if word.startswith(l.letter):
                parsed_letters.append(copy.deepcopy(l))
                word = re.sub(rf"^{l.letter}", "", word)
                found = True
                break
        if found:
            continue
        raise Exception(f"letter not found: {word}")
    return parsed_letters

def parse_word(word):
    word = jaconv.kata2hira(word)
    parsed_letters: list[Letter] = []
    while word:
        if word[0] in ["ぁ", "ぃ", "ぅ", "ぇ", "ぉ"]:
            word = re.sub(r"^.", "～", word)
        word = re.sub(r"^ぢ", "じ", word)
        word = re.sub(r"^づぁ", "ざ", word)
        word = re.sub(r"^づぇ", "ぜ", word)
        word = re.sub(r"^づぉ", "ぞ", word)
        word = re.sub(r"^づ", "ず", word)
        found = False
        for l in sorted(letters, key=lambda x: -len(x.letter)):
            if word.startswith(l.letter):
                parsed_letters.append(copy.deepcopy(l))
                word = re.sub(rf"^{l.letter}", "", word)
                found = True
                break
        if found:
            continue
        raise Exception(f"letter not found: {word}")
    return parsed_letters

def generate_word(min_length=3, max_length=8):
    lengths = list(range(min_length, max_length + 1))
    length = random.choices(lengths, weights=[0.2 if l in [min_length, max_length] else 1 for l in lengths])[0]
    choiced_letters: list[Letter] = []
    for i in range(length):
        letter_candidates = [l for l in letters if not (i == 0 and l.not_first) and
                                                not (i == length - 1 and l.not_last) and
                                                not (i > 0 and (sp := choiced_letters[-1].special) and sp in l.not_after)]
        choiced = random.choices(letter_candidates, weights=[l.weight for l in letter_candidates])[0]
        choiced_letters.append(choiced)
    return choiced_letters

def to_disp_word(word: list[Letter]) -> str:
    disp_word = ""
    for i, letter in enumerate(word):
        disp_letter = letter.letter
        if i > 0 and word[i - 1].special == "Tu" and letter.consonant in ["j", "z"]:
            disp_letter = disp_letter.translate(str.maketrans({"ざ": "づぁ", "じ": "ぢ", "ず": "づ", "ぜ": "づぇ", "ぞ": "づぉ"}))
        if letter.special == "SmallV":
            disp_letter = small_vowel_map.get(word[i - 1].vowel, "")
        disp_word += disp_letter
    return disp_word