"""Small lexical retrieval baseline; no model or third-party packages required."""
import re
DOCS = {
    'S1': 'The library opens at 09:00 on weekdays.',
    'S2': 'The library closes at 17:00 on weekdays.',
    'S3': 'The makerspace requires a safety induction before equipment use.'
}
def retrieve(query, k=2):
    words=set(re.findall(r'\w+', query.lower()))-{'the','a','at','on','is','what','when','does'}
    scored=[(len(words & set(re.findall(r'\w+', text.lower()))), key, text) for key,text in DOCS.items()]
    return [(key,text) for score,key,text in sorted(scored,reverse=True) if score>0][:k]
if __name__=='__main__':
    assert retrieve('library opens')[0][0]=='S1'
    assert retrieve('parking fees')==[]
    print(retrieve('library opens'))
    print('PASS: known and unsupported retrieval cases')
