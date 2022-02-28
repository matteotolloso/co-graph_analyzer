import re
import json
from sys import argv
import sys
import requests

def build_dataset(pubMedFilePath : str , pathToSave : str) -> dict:
    
    articlesStr : list[str] = []
    content = ''
    with open(pubMedFilePath,'r') as file:
        content = file.read()
    
    articlesStr = list(map(lambda x: x.replace('\n      ', ' '), content.split("\n\n")))

    dict = {}
    for art in articlesStr:

        # PubMed ID
        match = re.search('^PMID- (.*)$', art, re.MULTILINE)
        if match is None:
            continue
        pmid = match.group(1)

        # Title
        match = re.search('^TI  - (.*)$', art, re.MULTILINE)
        if match is None:
            continue
        ti = match.group(1)

        # Abstract
        match = re.search('^AB  - (.*)$', art, re.MULTILINE)
        if match is None:
            continue
        ab = match.group(1)

        # NLM Medical Subject Headings (MeSH) controlled vocabulary
        mh = re.findall('^MH  - (.*)$', art, re.MULTILINE)
        
        # Includes chemical, protocol or disease terms. May also a number assigned by the Enzyme Commission or by the Chemical Abstracts Service.
        rn = re.findall('^RN  - (.*)$', art, re.MULTILINE)

        # Non-MeSH subject terms (keywords) either assigned by an organization identified by the Other Term Owner, or generated by the author and submitted by the publisher
        ot = re.findall('^OT  - (.*)$', art, re.MULTILINE)

        dict[pmid] = {'Title' : ti, 'Abstract' : ab, 'MeSH' : mh, 'RNnumber': rn, 'OtherTerm': ot, 'bioBERT_entities': [] }

    base_url : str = "https://bern.korea.ac.kr/pubmed/"
    i = 0
    for id in dict.keys():
        i+=1
        print('processing article', i, 'of', len(dict.keys()))
        url = base_url + id
        response = requests.get(url, verify=False).json()
        denotations = response[0].get('denotations')
        for den in denotations:
            begin = den.get('span').get('begin')
            end = den.get('span').get('end')
            entity_type = den.get('obj')
            entity_name = response[0].get('text')[begin:end]
            dict[id].get('bioBERT_entities').append((entity_name, entity_type))
        
    dataset_string_json = json.dumps(dict, indent=4)

    with open(pathToSave, 'w') as file:
        file.write(dataset_string_json)
        
        
    return dict

if __name__ == "__main__":
   build_dataset(sys.argv[1], sys.argv[2])