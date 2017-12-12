from __future__ import division

import requests
from numpy import unique


def parse_nerur(home_url='http://www.nerur.com/music/ragalist.php'):
    raagas = {'melakarta': '', 'janya': ''}
    data = requests.get(home_url)
    lines = data.text.split('\n')
    start_ind = 0
    end_ind = 0
    for i in xrange(len(lines)):
        if 'mElakartha rAgAs' in lines[i]:
            start_ind = i + 1
        if start_ind != 0:
            if len(unique(list(lines[i]))) == 1:
                end_ind = i
                break
    raagas['melakarta'] = lines[start_ind + 1: end_ind - 1]

    janya_flag = False
    janya_lines = []
    for i in xrange(len(lines)):
        if not janya_flag and 'janya rAgAs' in lines[i]:
            janya_flag = True
        if janya_flag:
            parts = lines[i].split('|')
            if len(parts) > 2:
                janya_lines.append(lines[i])

            if len(unique(list(lines[i]))) == 1:
                break
    raagas['janya'] = janya_lines
    return raagas


def get_raagas(parsed_nerur_content):
    lines = parsed_nerur_content['melakarta']
    data = []

    for line in lines:
        parts = line.split('|')
        raaga_info = {'mela': parts[0].strip(), 'janya_to': None, 'name': parts[1].strip()}
        arohana = parts[2].strip().split()
        raaga_info['arohana'] = [i.strip() for i in arohana]
        avarohana = parts[3].strip().split()
        raaga_info['avarohana'] = [i.strip() for i in avarohana]

        data.append(raaga_info)

    lines = parsed_nerur_content['janya']
    svaras = ['S', 'R1', 'R2', 'R3', 'G1', 'G2', 'G3', 'M1', 'M2', 'P', 'D1', 'D2', 'D3', 'N1', 'N2', 'N3', 'S']

    for line in lines:
        parts = line.split('|')
        if len(parts) <= 2:
            continue

        raaga_info = {'mela': None, 'janya_to': parts[1].strip(), 'name': parts[0].strip()}

        arohana_data = parts[2].strip()
        for svara in svaras:
            if svara in arohana_data:
                arohana_data = arohana_data.replace(svara, '{0} '.format(svara))
        arohana_data = arohana_data.replace('  ', ' ')
        raaga_info['arohana'] = arohana_data.strip().split()

        avarohana_data = parts[3].strip()
        for svara in svaras:
            if svara in avarohana_data:
                avarohana_data = avarohana_data.replace(svara, '{0} '.format(svara))
        avarohana_data = avarohana_data.replace('  ', ' ')
        raaga_info['avarohana'] = avarohana_data.strip().split()

        data.append(raaga_info)

    return data
