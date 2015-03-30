import codecs
import re

from BeautifulSoup import BeautifulSoup
import requests


def get_session():
    login_url = 'https://www.swarganga.org/index.php'
    payload = {'uname': 'gopala.koduri@gmail.com', 'psswd': 'compmusic123', 'remember': 'on',
               'x': '52', 'y': '24', 'verifylogin': '1', 'redirect': 'https://www.swarganga.org/index.php'}
    s = requests.Session()
    s.post(login_url, data=payload)
    return s


def get_entries(html_source_file):
    """
    The input to this file is a cached/saved html page of artist/raaga/taalabase on swarganga.
    Makes sure that the page shows all the entries before saving it on disk.
    """
    data = codecs.open(html_source_file, encoding='utf-8').read()
    soup = BeautifulSoup(data)
    res = soup.findAll('tr', {'class': re.compile('baserow*')})

    entries = []
    for row in res:
        cols = row.findAll('td')
        if len(cols) < 4:
            continue
        link_data = cols[0].find('a')
        link_data = dict(link_data.attrs)
        entries.append(link_data['href'])
    return entries


def get_artist(url, session=None):
    if session:
        s = session
    else:
        s = get_session()
    res = s.get(url)
    soup = BeautifulSoup(res.text)

    t = soup.find('table', attrs={'class': 'details'})
    trs = t.findAll('tr')
    artist_info = {'name': trs[0].text}
    for tr in trs:
        tds = tr.findAll('td')
        if len(tds) < 2:
            continue
        artist_info[tds[0].text.lower()] = tds[1].text
    tds = trs[1].findAll('td')
    artist_info['image'] = tds[2].find('img').attrs[0][1]

    artist_info['bio'] = artist_info['short bio :']
    if len(artist_info['bio']) > 331:  # This is to remove the disclaimer put by swarganga
        artist_info['bio'] = artist_info['bio'][331:]
    artist_info['instrument'] = artist_info['speciality']
    artist_info['guru'] = artist_info['guruadd a guru']
    artist_info.pop('short bio :')
    artist_info.pop('speciality')
    artist_info.pop('guruadd a guru')
    artist_info.pop('disciple treeadd a disciple')
    return artist_info


def get_raaga(url, session=None):
    if session:
        s = session
    else:
        s = get_session()
    res = s.get(url)
    soup = BeautifulSoup(res.text)

    t = soup.find('table', attrs={'class': 'details'})
    trs = t.findAll('tr')
    raaga_info = {'name': trs[0].text}

    for tr in trs[1:5]:
        tds = tr.findAll('td')
        raaga_info[tds[0].text.lower()] = tds[1].text
        raaga_info[tds[2].text.lower()] = tds[3].text

    description = False
    for tr in trs[5:]:
        if description:
            description = tr.text
            break
        if tr.text.lower() == 'notes':
            description = True
    if description:
        raaga_info['description'] = description
    else:
        raaga_info['description'] = ''
    return raaga_info


def get_taala(url, session=None):
    if session:
        s = session
    else:
        s = get_session()
    res = s.get(url)
    soup = BeautifulSoup(res.text)

    t = soup.find('table', attrs={'class': 'details'})
    trs = t.findAll('tr')
    taala_info = {'name': trs[0].text}

    for tr in trs[1:4]:
        tds = tr.findAll('td')
        taala_info[tds[0].text.lower()] = tds[1].text
        taala_info[tds[2].text.lower()] = tds[3].text

    #TODO Bols are to be obtained calling a javascript function
    # ind = 0
    # for tr in trs:
    #     ind += 1
    #     if tr.text == 'Bol':
    #         break

    taala_info.pop('')
    return taala_info