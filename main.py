import collections
import json
from io import StringIO
from time import sleep
import gtts
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

book_name = "No_More_Mr_Nice_Guy"
output_string = StringIO()
with open(f'{book_name}.pdf', 'rb') as fin:
    extract_text_to_fp(fin, output_string, laparams=LAParams(), output_type='html', codec=None)
print(output_string.getvalue())
file1 = open(f"{book_name}.html", "a")
file1.writelines(output_string.getvalue())

with open(f"{book_name}.html", mode="r") as file:
    website_html = file.read()
soup = BeautifulSoup(website_html, "html.parser")

all_clicked_links = soup.find_all("a", href=True)
all_pages = soup.find_all("a", href=False)
all_a_tags = soup.contents[0].find_all_next("a", href=False)
list_pages = [page.getText() for page in all_pages]
list_links = [link.getText() for link in all_clicked_links]
# print(f"Nombre of links: {len(list_links)}; {list_links}")
# print(f"Nombre of pages: {len(list_pages)}; {list_pages}")
# print(all_a_tags)
output = soup.get_text()
next_txt = False
page_content = []
previous_row = ''
all_pages_dict = {}
for row in output.splitlines():
    if row in list_pages:
        next_txt = True
        all_pages_dict[previous_row] = page_content
        page_content = []
    if next_txt:
        if len(page_content) == 0:
            previous_row = row
            page_content.append('')
        else:
            page_content.append(row)
# clean all pages dictionary
for k in all_pages_dict.copy():
    if not all_pages_dict[k] or ''.join(all_pages_dict[k]) == '':
        all_pages_dict.pop(k)
    else:
        all_pages_dict[k] = [item for item in all_pages_dict[k] if item != '']
# list of all book content titles
all_content_title = []
for key, value in all_pages_dict.items():
    all_content_title.append(value[0])
print(all_content_title)
# find occurrence of word 'chapter' in all pages
all_chapter_variations = ['CHAPTER', 'Chapter', 'C h a p t e r', 'C H A P T E R']
counter = 0
for txt in all_content_title:
    if any(s in txt for s in all_chapter_variations):
        # print(txt)
        counter += 1
chapter_percentage = counter/len(all_content_title)
# most_frequent_sentence = max(set(all_content_title), key=all_content_title.count)
print(chapter_percentage)
page_title_as_chapter = False
if chapter_percentage > 80:
    page_title_as_chapter = True

if not page_title_as_chapter:
    # add chapter number to all pages dictionary
    counter = 0
    for key, value in all_pages_dict.items():
        if any(s in all_pages_dict[key] for s in all_chapter_variations):
            counter += 1
        all_pages_dict[key].insert(0, f"chapter:{counter}")
else:
    # add chapter number to all pages dictionary if chapter occurs on top of each page
    first_chapter = True
    last_chapter = 'chapter:0'
    for key, value in all_pages_dict.items():
        if not any(s in all_pages_dict[key][0] for s in all_chapter_variations):
            if first_chapter:
                all_pages_dict[key].insert(0, f"chapter:{0}")
                first_chapter = False
            else:
                all_pages_dict[key].insert(0, f"{last_chapter}")
        else:
            last_chapter = all_pages_dict[key][0]

# create new dictionary that contains chapter numbers as keys
all_chapter_dict = collections.defaultdict(list)
for key, value in all_pages_dict.items():
    all_chapter_dict[value[0]].append(' '.join(value[1:]))
with open(f'{book_name}.json', 'w') as fp:
    json.dump(all_chapter_dict, fp,  indent=4)

# parse chapters one by one, then, convert each one from text to speech using gtts
print("text to speech processing...")
t = 0
for key, value in all_chapter_dict.items():
    if key == "chapter:9":
        # continue
        t += len(' '.join(value))
        print(f"Current chapter characters: {t} ")
        tts = gtts.gTTS(' '.join(value), lang="en", tld="ca")
        # save the audio file
        tts.save(f"./audio/{book_name}_{key}.mp3")
        print(f"{key}_{book_name}.mp3 saved Successfully")
        sleep(10)
print(f"{t} total characters.")
