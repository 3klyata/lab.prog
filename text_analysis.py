from config import *
from logger import Logger

class TextAnalysis:
    def __init__(self) -> None:
        self.logger = Logger()
    def analyze(self):
        pass

class CountAbsoluteWordforms(TextAnalysis):
    def analyze(self, tokenized_text):
        self.logger.log_data("Пошук словоформ")
        wordforms_dict = {}
        for token in tokenized_text:
            token = token.lower()
            if token in PUNCTUATION_CHARS:
                self.logger.log_data(f"Токен-знак {token} пропущено")
                continue
            if not token in wordforms_dict.keys():
                self.logger.log_data(f"Нова словоформа додано до підрахунку: {token}")
                wordforms_dict[token] = 0
            wordforms_dict[token] += 1
            self.logger.log_data(f"Збільшина кількість входження словоформи {token}. Кількість: {wordforms_dict[token]}")
        return wordforms_dict

class CountExclamatorySentence(TextAnalysis):
    def analyze(self, tokenized_text):
        self.logger.log_data("Пошук окличних речень")
        tokens = tokenized_text.copy()
        exclamation_sequence = False
        exclamation_count = 0
        for index, token in enumerate(tokens):
            if index == 0:
                continue
            if token == '!' and tokens[index - 1] == '\n':
                self.logger.log_data(f"Знак оклику на початку речення, позиція знаку {index}, пропущено")
                continue
            if token == '!' and not exclamation_sequence:
                exclamation_count += 1
                exclamation_sequence = True
                self.logger.log_data(f"Додано окличне речення, позиція знаку {index}")
            if token != '!' and exclamation_sequence:
                exclamation_sequence = False
        return exclamation_count

class FlexionHighlighting(TextAnalysis):

    def highlight_end(self, noun, number):
        end = noun[:-number:1]+"-"+noun[-number:]
        return end

    def number_end_letters(self, word):
        phoneme_noun = word 
        for end in END_TO_CHECK:
            if phoneme_noun.endswith(end):
                ending = self.highlight_end(phoneme_noun, len(end))  
                self.logger.log_data(f"Знайдено закінчення слова {phoneme_noun}: {ending}")
                return ending
        self.logger.log_data(f"Слово {phoneme_noun} має нульове закінчення")
        return  phoneme_noun + "-0"  
        
    def analyze(self, tokenized_text):
        self.logger.log_data("Пошук закінчень")
        if len(tokenized_text) > 1:
            self.logger.log_data(f"Введено декілька слів: {tokenized_text}")
            tokenized_text_set = list(set(tokenized_text))
            for ind, word in enumerate(tokenized_text_set):
                tokenized_text_set[ind] = self.number_end_letters(word) 
            return tokenized_text_set
        else:
            self.logger.log_data(f"Введено  слово: {tokenized_text[0]}")
            return self.number_end_letters(tokenized_text[0]) 


class TextAnalizer:
    def text_analysis(self, text, analisis_strategy):
        tokenized_text = self.text_tokenization(text)
        return analisis_strategy.analyze(tokenized_text)

    def text_tokenization(self, text):
        for punctuation in PUNCTUATION_CHARS:
            text = text.replace(punctuation, f" {punctuation} ")

        text_tokens = text.split(' ')
        text_tokens = list(filter(lambda x: x != '', text_tokens))
        return text_tokens

