import random

def makeRandomString(length):
    keyword = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']
    result = ''
    for i in range (length):
        result += keyword[random.randrange(0, 36)]
    return result

def makeRandomColor():
    keyword = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    return '#' + keyword[random.randrange(10, 16)] + keyword[random.randrange(0, 16)] \
           + keyword[random.randrange(10, 16)] + keyword[random.randrange(0, 16)] \
           + keyword[random.randrange(10, 16)] + keyword[random.randrange(0, 16)]