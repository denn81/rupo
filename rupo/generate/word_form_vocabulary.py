# -*- coding: utf-8 -*-
import numpy as np
from collections import defaultdict, Counter
from typing import List, Dict, Tuple
from rupo.generate.word_form import WordForm
from rupo.generate.grammeme_vectorizer import GrammemeVectorizer


class WordFormVocabulary(object):
    def __init__(self):
        self.word_forms = []  # type: List[WordForm]
        self.word_form_indices = {}  # type: Dict[WordForm, int]
        self.lemma_to_word_form_indices = defaultdict(lambda: list())  # type: Dict[str, List[int]]
        self.text_to_lemma_gram = defaultdict(lambda: list())  # type: Dict[str, List[Tuple[str, int]]]
        self.lemma_gram_to_word_form_index = {}  # type: Dict[Tuple[str, int], int]
        self.lemma_counter = Counter()
        self.sorted = False

    def load_from_corpus(self, filename: str, grammeme_vectorizer: GrammemeVectorizer):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                if line == "\n":
                    continue
                form, lemma, pos_tag, grammemes = line.split("\t")[:4]
                vector_name = pos_tag + "#" + grammemes
                self.add_word_form(form, lemma + "_" + pos_tag, grammeme_vectorizer.name_to_index[vector_name])

    def add_word_form(self, text: str, lemma: str, gram_vector_index: int):
        word_form = WordForm(lemma, gram_vector_index, text)
        lemma_gram = (lemma, gram_vector_index)
        self.lemma_counter[lemma] += 1
        if word_form not in self.word_form_indices:
            self.word_forms.append(word_form)
            index = len(self.word_forms) - 1
            self.word_form_indices[word_form] = index
            self.lemma_to_word_form_indices[lemma].append(index)
            self.text_to_lemma_gram[text].append(lemma_gram)
            self.lemma_gram_to_word_form_index[lemma_gram] = index
        self.sorted = False
                
    def get_word_form(self, lemma, gram_vector_index):
        return self.word_forms[self.lemma_gram_to_word_form_index[(lemma, gram_vector_index)]].text
    
    def get_lemma_gram_by_text(self, text):
        return self.text_to_lemma_gram[text]
    
    def choice_word(self):
        return self.word_forms[np.random.randint(0, len(self.word_forms))]
    
    def get_paradigm(self, lemma):
        return self.lemma_to_word_form_indices[lemma]
    
    def get_word_form_index(self, word_form):
        return self.word_form_indices[word_form]
            
    def get_word_form_by_index(self, index):
        return self.word_forms[index]

    def get_word_form_index_min(self, word_form, size):
        return min(self.get_word_form_index(word_form), size)

    def sort(self):
        new_vocab = WordFormVocabulary()
        for lemma, _ in self.lemma_counter.most_common():
            for index in self.lemma_to_word_form_indices[lemma]:
                word_form = self.word_forms[index]
                new_vocab.add_word_form(word_form.text, word_form.lemma, word_form.gram_vector_index)
        self.word_forms = new_vocab.word_forms
        self.word_form_indices = new_vocab.word_form_indices
        self.lemma_to_word_form_indices = new_vocab.lemma_to_word_form_indices
        self.text_to_lemma_gram = new_vocab.text_to_lemma_gram
        self.lemma_gram_to_word_form_index = new_vocab.lemma_gram_to_word_form_index
        self.sorted = True
