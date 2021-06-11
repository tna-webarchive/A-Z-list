import pandas as pd
import sys, os


### Takes argument from command line
destination = sys.argv[1]
os.system('git pull')
full_list = pd.read_excel('Full List.xlsx')

#####WRITE HTML
ABC = 'abcdefghijklmnopqrstuvwxyz'
head = '<h2 name="{lower}">{upper}</h2>'
body = ' <li><a title="This link opens in a new window" href="{URL}" target="_blank" rel="noopener noreferrer">{name}</a></li>'

with open('HTML_template.txt', 'r') as source:
    text = source.read()

#### Goes through each letter, writing the relevant HTML lines.
for letter in ABC:
    section = full_list[full_list['sort'].str.startswith(letter)]
    if len(section) > 0:
        text += head.replace('{lower}', letter).replace('{upper}', letter.upper())
        text += '\n<ul>\n\n'
        lines = section.apply(lambda x: body.replace('{URL}', x['Archive URL']).replace('{name}', x['Site Name']), axis=1)
        text +='\n'.join(lines)
        text +='\n\n</ul>\n'
    full_list = full_list[~full_list['sort'].str.startswith(letter)]

### 0-9 section
text += head.replace('{lower}', '0-9').replace('{upper}', '0-9')
text += '\n<ul>\n\n'
lines = full_list.apply(lambda x: body.replace('{URL}', x['Archive URL']).replace('{name}', x['Site Name']), axis=1)
text += '\n'.join(lines)
text += '\n\n</ul>'


with open(f'{destination}', 'w', encoding='utf-8') as dest:
    dest.write(text)