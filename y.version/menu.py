slova = ['hello','hi','cool','great','hi','dge','lol','night']

def printing():
    for x in current_ids:
        current_words.append(slova[x])
    new_word = ' '.join(current_words)
    print(new_word)


word = input('say')
print(word)

index_word = slova.index(word)
current_ids = [slova.index(word)]

    
while True:
    current_words = []
    user = input('where')
    
    if user == '>+':
        if current_ids[-1] == len(slova)-1:
            printing()
        else:
            current_ids.append(current_ids[-1] + 1)
            printing()
    if user == '<+':
        if current_ids[0] == 0:
            printing()
        else:
            current_ids[:0] = [current_ids[0]-1]
            printing()
    if user == '<-':
        if len(current_ids) == 1:
            printing()
        else:
            current_ids.pop()
            printing()
    if user == '>-':
        if len(current_ids) == 1:
            printing()
        else:
            current_ids.pop(0)
            printing()