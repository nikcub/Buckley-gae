import os
import sys

from struct import pack
from base64 import b64encode, b64decode

try:
  from Crypto.Hash import HMAC as hmac, SHA as sha1
  from Crypto.Random.random import getrandbits, randint, choice
except ImportError:
  import hmac
  from random import randint, choice
  try:
    from hashlib import sha1
  except ImportError:
    import sha as sha1
        
NUMBERS = [chr(i) for i in range(48, 58)]
UPPERCASE = [chr(i) for i in range(65, 91)]
LOWERCASE = [chr(i) for i in range(97, 123)]
PUNC = [chr(i) for i in [33, 35, 36, 42, 43, 46, 47, 64, 95]]
VOWELS = ['a','e','i','o','u']


def hash_password(password, salt):
  return gen_pbkdf1(password, salt, iterations=20000)


def gen_sha1(password, salt = "abcdefghijklmnopqrstuvwxyz", iterations=10000):
  """Python implementation for a slow password hash
  """
  h = sha1()
  h.update(password)
  h.update(salt)
  for x in range(iterations):
    h.update(h.digest())
  return h.hexdigest()


def gen_pbkdf1(password, salt, iterations=10000):
  """Simple implementation of pbkdf1 using iterations of sha1
  
  """
  O = sha1(password + salt).digest()
  for _ in xrange(2, iterations + 1):
    O = sha1(O).digest()
  return O


def gen_salt(length=64):
  """Returns 64-bit pseudo-radom (based on random.randint) salt
  
  """
  return "".join([pack("@H", randint(0, 0xffff)) for i in range(4)])


def gen_password(length=8, allowed_chars=""):
  """Generate a random password
  
  :param length: (Optional) Password length
  :param allowed_chars: (Optional) String of allowed chars
  """
  if len(allowed_chars) > 0:
    char_set = allowed_chars
  else:
    char_set = LOWERCASE + UPPERCASE + NUMBERS
  return ''.join([choice(char_set) for i in range(length)])[:length]


def file_hash(filedata):
  return sha1(filedata).hexdigest()


def gen_password_old(length = 10, num_punc = 1, sequence = None):
  """
  Generate a random password, where:

  :var    length      length of password, default 10
  :var    num_punc    minimum number of punctuation characters in pass
  :var    sequence    the sequence to generate from. vary to increase or decrease frequency of each
  """
  sequence = ['LOWERCASE', 'LOWERCASE', 'LOWERCASE', 'LOWERCASE', 'LOWERCASE', 'LOWERCASE', 'UPPERCASE', 'VOWELS', 'NUMBERS', 'PUNC']
  seq = [sequence[randint(0, len(sequence) - 1)] for i in range(0, 100)]
  # print sequence[random.randint(0, len(sequence) - 1)].upper()
  # seq = [LOWERCASE for i in range(0, 10)]
  # print locals()
  return "".join([globals()[i][randint(0, len(globals()[i]) - 1)] for i in seq])[0:length]


def test():
  password = gen_password(8)
  salt = gen_salt()
  t = gen_pbkdf1(password, salt, iterations = 100000)
  print "Hash %s with %s as %s" % (password, b64encode(salt), b64encode(t))


if __name__ == '__main__':
  test()
