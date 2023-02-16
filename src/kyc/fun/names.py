from kyc import Candidate
from fuzzywuzzy import fuzz
from utils import Log
import re
from utils import JSONFile
from gig import Ent, EntType
log = Log('names')


def clean(name):
    name = name.lower()
    # remove all non alphabetical
    name = re.sub('[^a-z ]', '', name)
    # remove all double spaces
    name = re.sub('\\s+', ' ', name).strip()
    return name


def get_names(candidates):
    MIN_NAME_LEN = 2
    names = []
    for candidate in candidates:
        full_name = clean(candidate.name)
        names_for_candidate = full_name.lower().split(' ')
        names_for_candidate = list(
            filter(
                lambda name: len(name) >= MIN_NAME_LEN, names_for_candidate
            )
        )
        names += names_for_candidate
    return names


def count_names_raw():
    candidates = Candidate.list_all()
    JSONFile('data/fun/name_to_cluster_key.json').read()
    names = get_names(candidates)
    name_to_n = {}
    for name in names:
        name_to_n[name] = name_to_n.get(name, 0) + 1
    name_to_n = dict(
        sorted(name_to_n.items(), key=lambda item: item[1], reverse=True)
    )
    return name_to_n


def get_unique_names():
    names = get_names()
    return list(sorted(set(names)))


def build_cluster_predata():
    RATIO_LIMIT = 80
    unique_names = get_unique_names()
    n_original = len(unique_names)
    log.debug(f'{n_original=}')

    n = n_original
    unique_names = unique_names[:n]

    idx = {}
    for i in range(n - 1):
        name_i = unique_names[i]
        for j in range(i + 1, n):
            name_j = unique_names[j]
            if name_i[0] != name_j[0]:
                continue

            name_j = unique_names[j]
            ratio = fuzz.ratio(name_i, name_j)
            if ratio > RATIO_LIMIT:
                print(f'\t\t{i},{j}){name_i} {name_j} {ratio}', end='\r')

                if i not in idx:
                    idx[i] = {}
                idx[i][j] = ratio

    JSONFile('data/fun/unique_names.json').write(unique_names)
    JSONFile('data/fun/name_to_matches.json').write(idx)
    return unique_names, idx


def build_name_clusters():
    name_to_n = count_names_raw()
    unique_names = JSONFile('data/fun/unique_names.json').read()
    name_to_matches = JSONFile('data/fun/name_to_matches.json').read()
    reverse_unique = dict(
        list(map(lambda item: (item[1], item[0]), enumerate(unique_names)))
    )

    i_to_n_similar = {}
    for i_str in name_to_matches:
        i = (int)(i_str)
        for j_str in name_to_matches[i_str]:
            j = (int)(j_str)
            score = (int)(name_to_matches[i_str][j_str])
            if score > 90:
                i_to_n_similar[i] = i_to_n_similar.get(i, 0) + 1
                i_to_n_similar[j] = i_to_n_similar.get(j, 0) + 1
    i_to_n_similar = dict(
        sorted(i_to_n_similar.items(), key=lambda item: item[1], reverse=True)
    )
    i_by_importance = [reverse_unique[name] for name in name_to_n.keys()]
    log.debug(i_by_importance[:10])

    def get_score(i, j):
        str_i = str(i)
        str_j = str(j)
        if str_i in name_to_matches and str_j in name_to_matches[str_i]:
            return name_to_matches[str_i][str_j]
        if str_j in name_to_matches and str_i in name_to_matches[str_j]:
            return name_to_matches[str_j][str_i]
        return 0

    clusters = {}
    for i in i_by_importance:
        found_cluster = False
        for j in clusters:
            score = get_score(i, j)
            if score > 80:
                clusters[j].append(i)
                found_cluster = True
                break
        if not found_cluster:
            clusters[i] = []
            name_i = unique_names[i]
            print(f'\t\t{i} {name_i}', end='\r')

    name_to_cluster_key = {}
    for j in clusters:
        for i in clusters[j]:
            name_to_cluster_key[unique_names[i]] = unique_names[j]

    JSONFile('data/fun/name_to_cluster_key.json').write(name_to_cluster_key)


def count_names(district_id):
    candidates_all = Candidate.list_all()
    candidates = list(filter(lambda candidate: district_id in candidate.district_id, candidates_all))

    n_candidates = len(candidates)

    
    name_to_cluster_key = JSONFile('data/fun/name_to_cluster_key.json').read()
    names = get_names(candidates)
    name_to_n = {}
    for name in names:
        cluster_key = name_to_cluster_key.get(name, name)
        name_to_n[cluster_key] = name_to_n.get(cluster_key, 0) + 1
    
    print(f'(n={n_candidates:,})')
    name_to_n = dict(
        sorted(name_to_n.items(), key=lambda item: item[1], reverse=True)
    )
    for name in list(name_to_n.keys())[:20]:
        n = name_to_n[name]
        p = n / n_candidates
        print(f'{name.title()} ({p:.0%})')

def count_mohameds(district_id):
    candidates_all = Candidate.list_all()
    candidates = list(filter(lambda candidate: district_id in candidate.district_id, candidates_all))

    n_candidates = len(candidates)
    name_to_cluster_key = JSONFile('data/fun/name_to_cluster_key.json').read()
    
    names = get_names(candidates)
    name_to_n = {}
    for name in names:
        cluster_key = name_to_cluster_key.get(name, name)
        if cluster_key not in ['mohamad', 'muhammadu']:
            continue
        name_to_n[name] = name_to_n.get(name, 0) + 1

    print(f'(n={n_candidates:,})')
    name_to_n = dict(
        sorted(name_to_n.items(), key=lambda item: item[1], reverse=True)
    )
    for name in list(name_to_n.keys())[:20]:
        n = name_to_n[name]
        p = n / n_candidates
        print(f'{name.title()} ({p:.0%})')

    


if __name__ == '__main__':
    district_ents = Ent.list_from_type(EntType.DISTRICT)
    for ent in district_ents:
        print(ent.name + ' District')
        count_names(ent.id)
        print('-' * 32)

    print('Sri Lanka')
    count_names('LK-')
    print('-' * 32)


    
