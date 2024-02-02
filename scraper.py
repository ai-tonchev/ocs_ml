def scrape_chapter(book_id: str, chapter_num, DEBUG: bool = False):
    chapter = {}

    url = f'https://azbyka.ru/biblia/?{book_id}.{chapter_num}&utfcs'

    res = r.get(url)
    soup = BeautifulSoup(res.content)

    #extract book name and chapter number
    title_block = soup.find('span', {'class': 'title__chapters-selector'})

    if title_block is not None:
        book_title = title_block.text.replace('\n', '').replace('\t', '').replace('\xa01', '').replace(', Глава', '')
    else:
        book_title = soup.h1.span.text.replace('\n', '').replace('\t', '').replace('\xa01', '').replace(', Глава', '')
        
    chapter['book_id'] = book_id
    chapter['book'] = book_title
    chapter['number'] = chapter_num

    #extract verses
    verses = []

    contents = soup.find('div', {'class':'tbl-content kafizm'}).find_all('div')
    if DEBUG:
        contents = contents[:3]
        
    for div in contents:
        div_class = [i for i in div.get('class')] if div.get('class') else []
        if div_class:
            if div_class[0] == 'verse':
                verses.append(div.text.replace('\n', ''))

    chapter['verses'] = verses

    return chapter


def scrape_book(book_id: str, DEBUG: bool = False):

    url = f'https://azbyka.ru/biblia/?{book_id}.1&utfcs'
    res = r.get(url)
    soup = BeautifulSoup(res.content)

    title_block = soup.find('span', {'class': 'title__chapters-selector'})

    if title_block is not None:
        book_title = title_block.text.replace('\n', '').replace('\t', '').replace('\xa01', '').replace(', Глава', '')
    else:
        book_title = soup.h1.span.text.replace('\n', '').replace('\t', '').replace('\xa01', '').replace(', Глава', '')

    chapter_section = soup.find('ul', {'class': 'chapters'}).find_all('li')
    chapter_list = [int(li.text) for li in chapter_section]
    if DEBUG:
        chapter_list=chapter_list[:3]

    book = {}
    book['book_id'] = book_id
    book['title'] = book_title
    chapters = [scrape_chapter(book_id, i+1, DEBUG=DEBUG) for i in chapter_list]
    book['chapters'] = chapters

    return book

def scrape_bible(output_file: str = None, DEBUG: bool = False):
    url = 'https://azbyka.ru/biblia/?utfcs'
    res = r.get(url)
    soup = BeautifulSoup(res.content)
    

    bib = {}
    
    new_book_ids = []
    NT_block = soup.find('div', {'class':'col-new'}).find_all('span', {'class': 'book-title'})
    for span in NT_block:
        book_id = span.a.get('href').replace('/biblia/?','').replace('.1&utfcs', '')
        new_book_ids.append(book_id)

    old_book_ids = []
    OT_block = soup.find('div', {'class':'col-old'}).find_all('span', {'class': 'book-title'})
    for span in OT_block:
        book_id = span.a.get('href').replace('/biblia/?','').replace('.1&utfcs', '')
        old_book_ids.append(book_id)
    
    print('Scraping New Testament:')
    NT = {}
    for book_id in new_book_ids:
        print(f'\t{book_id}')
        NT[book_id] = scrape_book(book_id, DEBUG=DEBUG)

    print('Scraping Old Testament:')
    OT = {}
    for book_id in old_book_ids:
        print(f'\t{book_id}')
        OT[book_id] = scrape_book(book_id, DEBUG=DEBUG)


    bib['NT'] = NT
    bib['OT'] = OT

    if output_file:
        print(f'Writing output to {output_file}')
        with open(output_file, 'w') as f:
            json.dump(bib, f)

    return bib