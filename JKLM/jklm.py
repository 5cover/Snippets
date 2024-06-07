#!/bin/env python3
from collections import Counter
from multiprocessing import Pool

with open('data/syllables-min1.txt', 'r') as file:
# Invariant : syllables are uppercase and devoid of diacritics
    syllables = Counter(line.rstrip() for line in file)
syllablesCount = sum(syllables.values())

def get_score(word: str) -> int:
    """Computes the easiness score of a word in the game JKLM.fun.
    This score represents the probability of the word being valid, based on the available syllables."""
    return sum(count for s, count in syllables.items() if s in word)

def get_best_words(words: list[str]) -> list[tuple[int, str]]:
    with Pool() as p:
        scores = p.map(get_score, words)
    return sorted(zip(scores, words), key=lambda kvp: kvp[0], reverse=True)

def get_best_word(words: list[str]) -> tuple[int, str]:
    with Pool() as p:
        scores = p.map(get_score, words)
    return max(zip(scores, words), key=lambda kvp: kvp[0])

# Order words by the number of distinct syllables, prioritizing common ones
with open('data/liste_mots_all.txt', 'r') as file:
# Invariant : words are uppercase, devoid of diacriticts, and sorted alphabetically
    # Must not be generator to work well with Pool.map
    words = [line[:-1] for line in file]

def show_word_leaderboard():
    for score, word in get_best_words(words):
        print(f"{word} : {score/syllablesCount:.2%}")

def show_optimal_words():
    global syllablesCount
    global syllables
    while len(syllables) > 0:
        # Get the best word
        best_word_score, best_word = get_best_word(words)
        # Remove all syllables it occupies the word
        syllables_in_word = {s for s in syllables if s in best_word}
        print(f"{best_word} : {best_word_score/syllablesCount:.2%} {syllables_in_word}")
        syllables = {s: count for s, count in syllables.items() if s not in syllables_in_word}

show_optimal_words()

# todo : ponderate by amount of distinct letters