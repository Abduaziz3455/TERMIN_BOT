from difflib import get_close_matches

# from handlers.users.uzwords import words
from handlers.users.read_word import word_atama
words = word_atama().keys()


def checkWord(word, words=words):
    matches = set(get_close_matches(word, words, cutoff=0.5))
    available = False  # bunday so'z mavjud emas

    if word in matches:
        available = True
        matches = word

    # elif 'ҳ' in word:
    #     word = word.replace('ҳ', 'х')
    #     matches.update(get_close_matches(word, words))
    #
    # elif 'х' in word:
    #     word = word.replace('х', 'ҳ')
    #     matches.update(get_close_matches(word, words))

    return {'available': available, 'matches': matches}


if __name__ == '__main__':
    print(checkWord('ҳато'))
    print(checkWord('тариҳ'))
    print(checkWord('хато'))
    print(checkWord('олма'))
    print(checkWord('ҳат'))
    print(checkWord('ҳайт'))
