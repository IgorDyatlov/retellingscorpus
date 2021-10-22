import json
with open('data-20160406T0100.json', 'r', encoding='utf-8') as file:
    text = file.read()
text_loaded = json.loads(text)
print(text_loaded[0])

for one in text_loaded:
    if one['District'] == 'район Савёлки':
        count += 1
        print(one)
print(count)