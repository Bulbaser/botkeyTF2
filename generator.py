import string
import random

# Генератор комментария
def gener():
    letters = string.ascii_lowercase
    com = ''.join(random.sample(letters, 6))
    return com