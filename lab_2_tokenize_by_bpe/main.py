"""
Lab 2
BPE and machine translation evaluation
"""
import json
import math


def prepare_word(
    raw_word: str, start_of_word: str | None, end_of_word: str | None
) -> tuple[str, ...] | None:
    """
    Tokenizes word into unigrams and appends end-of-word token
    :param raw_word: original word
    :param start_of_word: a token that signifies the start of word
    :param end_of_word: a token that signifies the end of word
    :return: preprocessed word
    """
    if not isinstance(raw_word, str) or\
            not (isinstance(start_of_word, str) or start_of_word is None) or\
            not (isinstance(end_of_word, str) or end_of_word is None):
        return None
    token_list = list(raw_word)
    if start_of_word is not None:
        token_list.insert(0, start_of_word)
    if end_of_word is not None:
        token_list.append(end_of_word)
    return tuple(token_list)



def collect_frequencies(
    text: str, start_of_word: str | None, end_of_word: str
) -> dict[tuple[str, ...], int] | None:
    """
    Counts number of occurrences of each word
    :param text: original text with no preprocessing
    :param start_of_word: a token that signifies the start of word
    :param end_of_word: a token that signifies the end of word
    :return: dictionary in the form of <preprocessed word: number of occurrences>
    """
    if not isinstance(text, str) or\
            not isinstance(start_of_word, str | None) or\
            not isinstance(end_of_word, str):
        return None
    split_text = text.split()
    tokens_dictionary = {}
    for token in split_text:
        split_word = prepare_word(token, start_of_word, end_of_word)
        if split_word is None:
            return None
        if split_word not in tokens_dictionary:
            tokens_dictionary[split_word] = split_text.count(token)
    return tokens_dictionary


def count_tokens_pairs(
    word_frequencies: dict[tuple[str, ...], int]
) -> dict[tuple[str, str], int] | None:
    """
    Counts number of occurrences of each pair of subsequent tokens
    :param word_frequencies: dictionary in the form of <preprocessed word: number of occurrences>
    :return: dictionary in the form of <token pair: number of occurrences>
    """
    if not isinstance(word_frequencies, dict):
        return None
    pairs_dictionary = {}
    for token in word_frequencies:
        for index in range(len(token) - 1):
            token_pair = (token[index], token[index + 1])
            if token_pair not in pairs_dictionary:
                pairs_dictionary[token_pair] = 0
            pairs_dictionary[token_pair] += word_frequencies[token]
    return pairs_dictionary

def merge_tokens(
    word_frequencies: dict[tuple[str, ...], int], pair: tuple[str, str]
) -> dict[tuple[str, ...], int] | None:
    """
    Updates word frequency dictionary by replacing a pair of token with a merged one
    :param word_frequencies: dictionary in the form of <preprocessed word: number of occurrences>
    :param pair: a pair of tokens to be merged
    :return: dictionary in the form of <preprocessed word: number of occurrences>
    """
    if not isinstance(word_frequencies, dict) or not isinstance(pair, tuple):
        return None
    merge_token_dictionary = {}
    for token in word_frequencies:
        token_list = list(token)
        if pair[0] in token and pair[1] in token:
            for index in range(len(token_list) - 1):
                if (token[index], token[index + 1]) == pair:
                    token_list[index: index + 2] = [''.join(pair)]
            merge_token_dictionary[tuple(token_list)] = word_frequencies[token]
        else:
            merge_token_dictionary[token] = word_frequencies[token]
    return merge_token_dictionary

def train(
    word_frequencies: dict[tuple[str, ...], int] | None, num_merges: int
) -> dict[tuple[str, ...], int] | None:
    """
    Creates required number of new tokens by merging existing ones
    :param word_frequencies: dictionary of a kind <preprocessed word: number of occurrences>
    :param num_merges: required number of new tokens
    :return: dictionary in the form of <preprocessed word: number of occurrences>
    """
    if not isinstance(word_frequencies, dict) or not isinstance(num_merges, int):
        return None
    while num_merges > 0:
        num_of_pairs = count_tokens_pairs(word_frequencies)
        if num_of_pairs is None:
            break
        if num_merges > len(num_of_pairs):
            num_merges = len(num_of_pairs)
        pairs_list = sorted(num_of_pairs.items(),
                            key=lambda x: (-x[1], -len(''.join(x[0])),
                                           ''.join(x[0])))
        word_frequencies = merge_tokens(word_frequencies, pairs_list[0][0])
        if word_frequencies is None:
            return None
        num_merges -= 1
    return word_frequencies

def get_vocabulary(
    word_frequencies: dict[tuple[str, ...], int], unknown_token: str
) -> dict[str, int] | None:
    """
    Establishes correspondence between tokens and its integer identifier
    :param word_frequencies: dictionary in the form of <preprocessed word: number of occurrences>
    :param unknown_token: a token to signify an unknown token
    :return: dictionary in the form of <token: identifier>
    """
    if not isinstance(word_frequencies, dict) or\
            not isinstance(unknown_token, str):
        return None
    list_of_tokens = set()
    get_vocabulary_dict = {}
    for tuples in word_frequencies.keys():
        for word in tuples:
            list_of_tokens.add(word)
            for token in word:
                list_of_tokens.add(token)
    list_of_tokens.add(unknown_token)
    right_order = sorted(list_of_tokens, key=lambda item: (-len(item), item))
    for index, token in enumerate(right_order):
        get_vocabulary_dict[token] = index
    return get_vocabulary_dict

def decode(
    encoded_text: list[int] | None, vocabulary: dict[str, int] | None, end_of_word_token: str | None
) -> str | None:
    """
    Translates encoded sequence into decoded one
    :param encoded_text: a sequence of token identifiers
    :param vocabulary: dictionary in the form of <token: identifier>
    :param end_of_word_token: an end-of-word token
    :return: decoded sequence
    """
    if not isinstance(encoded_text, list) or\
            not isinstance(vocabulary, dict) or\
            not (isinstance(end_of_word_token, str) or end_of_word_token is None):
        return None
    inverted_vocabulary = {value: token for token, value in vocabulary.items()}
    decoding = ''
    for number in encoded_text:
        for key in inverted_vocabulary:
            if key != number:
                continue
            token = inverted_vocabulary[number]
            if end_of_word_token is not None and end_of_word_token in token:
                token = token.replace(end_of_word_token, ' ')
            decoding += token
    return decoding

def tokenize_word(
    word: tuple[str, ...], vocabulary: dict[str, int], end_of_word: str | None, unknown_token: str
) -> list[int] | None:
    """
    Splits word into tokens
    :param word: preprocessed word
    :param vocabulary: dictionary in the form of <token: identifier>
    :param end_of_word: an end-of-word token
    :param unknown_token: token that signifies unknown sequence
    :return: list of token identifiers
    """
    if not isinstance(word, tuple) or\
        not isinstance(vocabulary, dict) or\
        not (isinstance(end_of_word, str) or end_of_word is None) or\
            not isinstance(unknown_token, str):
        return None
    string_word = ''.join(word)
    res_string = ''.join(word)
    sorted_vocabulary = sorted(list(vocabulary.keys()), key=lambda item: (-len(item), item))
    for token in sorted_vocabulary:
        if token in string_word:
            res_string = res_string.replace(token, str(vocabulary[token]) + ' ')
    for symbol in string_word:
        if symbol not in sorted_vocabulary:
            res_string = res_string.replace(symbol, str(vocabulary[unknown_token]) + ' ')
    result_of_encoding = res_string.split()
    encoded_list = []
    for number in result_of_encoding:
        encoded_list.append(int(number))
    return encoded_list

def load_vocabulary(vocab_path: str) -> dict[str, int] | None:
    """
    Reads and retrieves dictionary of type <token: identifier>
    :param vocab_path: path to the saved vocabulary
    :return: dictionary in the form of <token: identifier>
    """
    if not isinstance(vocab_path, str):
        return None
    with open(vocab_path, 'r', encoding='utf-8') as file:
        vocabulary = json.load(file)
    if not isinstance(vocabulary, dict):
        return None
    return vocabulary


def encode(
    original_text: str,
    vocabulary: dict[str, int] | None,
    start_of_word_token: str | None,
    end_of_word_token: str | None,
    unknown_token: str,
) -> list[int] | None:
    """
    Translates decoded sequence into encoded one
    :param original_text: original text
    :param vocabulary: dictionary in the form of <token: identifier>
    :param start_of_word_token: a start-of-word token
    :param end_of_word_token: an end-of-word token
    :param unknown_token: token that signifies unknown sequence
    :return: list of token identifiers
    """
    if not isinstance(original_text, str) or\
        not isinstance(vocabulary, dict) or\
        not (isinstance(start_of_word_token, str)
             or start_of_word_token is None) or\
        not (isinstance(end_of_word_token, str)
             or end_of_word_token is None) or\
            not isinstance(unknown_token, str):
        return None
    split_text = original_text.split()
    list_of_indexes = []
    for word in split_text:
        prepared_word = prepare_word(word, start_of_word_token, end_of_word_token)
        if prepared_word is None:
            return None
        tokens_indexes = tokenize_word(prepared_word, vocabulary, end_of_word_token, unknown_token)
        if tokens_indexes is None:
            return None
        list_of_indexes.extend(tokens_indexes)
    return list_of_indexes

def collect_ngrams(text: str, order: int) -> list[tuple[str, ...]] | None:
    """
    Extracts n-grams from the given sequence
    :param text: original text
    :param order: required number of elements in a single n-gram
    :return: sequence of n-grams
    """
    list_of_new_tokens = []
    if not isinstance(text, str) or\
            not isinstance(order, int) :
        return None
    for index in range(len(text) - order + 1):
        list_of_new_tokens.append(tuple(text[index:index + order]))
    return list_of_new_tokens

def calculate_precision(
    actual: list[tuple[str, ...]], reference: list[tuple[str, ...]]
) -> float | None:
    """
    Compares two sequences by virtue of Precision metric
    :param actual: predicted sequence of n-grams
    :param reference: expected sequence of n-grams
    :return: value of Precision metric
    """
    if not isinstance(actual, list) or\
            not isinstance(reference, list):
        return None
    if len(actual) == 0:
        return 0
    count_similar_tokens = 0
    set_actual = list(set(actual))
    set_reference = list(set(reference))
    max_length = max(len(set_actual), len(set_reference))
    for token in set_actual:
        if token in set_reference:
            count_similar_tokens += 1
    precision = count_similar_tokens/max_length
    return precision


def geo_mean(precisions: list[float], max_order: int) -> float | None:
    """
    Computes geometric mean of sequence of values
    :param precisions: sequence of Precision values
    :param max_order: maximum length of n-gram considered
    :return: value of geometric mean of Precision metric
    """
    if not isinstance(precisions, list) or\
            not isinstance(max_order, int):
        return None
    num = 1.0
    for oder in range(max_order):
        if precisions[oder] < 0:
            return 0.0
        num = num * precisions[oder]
    return float(math.pow(num, (1/max_order)))

def calculate_bleu(actual: str | None, reference: str, max_order: int = 3) -> float | None:
    """
    Compares two sequences by virtue of BLEU metric
    :param actual: predicted sequence
    :param reference: expected sequence
    :param max_order: max length of n-gram to consider for comparison
    :return: value of BLEU metric
    """
    if not isinstance(actual, str) or\
        not isinstance(reference, str) or\
            not isinstance(max_order, int):
        return None
    actual_ngrams = []
    reference_ngrams = []
    result_of_precision = []
    for order in range(max_order):
        a_ngrams = collect_ngrams(actual, order + 1)
        r_ngrams = collect_ngrams(reference, order + 1)
        if a_ngrams is None or r_ngrams is None:
            return None
        actual_ngrams.append(a_ngrams)
        reference_ngrams.append(r_ngrams)
    for a_ngrams, r_ngrams in zip(actual_ngrams, reference_ngrams):
        precision = calculate_precision(a_ngrams, r_ngrams)
        if precision is None:
            return None
        result_of_precision.append(precision)
    bleu = geo_mean(result_of_precision, max_order)
    if bleu is None:
        return None
    return bleu * 100
