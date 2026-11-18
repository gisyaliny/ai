"""Ollama native API exercise. Set OLLAMA_MODEL to a locally installed model."""
import json, os, urllib.request
from retrieval import retrieve
def answer(question):
    evidence=retrieve(question)
    if not evidence: return {'answer':'Insufficient evidence','sources':[]}
    model=os.environ.get('OLLAMA_MODEL')
    if not model: raise RuntimeError('Set OLLAMA_MODEL to an ID from ollama list')
    prompt='Use only the evidence below. Cite source IDs. If unsupported, say insufficient evidence.\n'+repr(evidence)+'\nQuestion: '+question
    req=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=json.dumps({'model':model,'messages':[{'role':'user','content':prompt}],'stream':False}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as r: result=json.load(r)
    return {'answer':result['message']['content'],'sources':[x[0] for x in evidence]}
if __name__=='__main__':
    print(json.dumps(answer('When does the library open?'),indent=2))
    print(json.dumps(answer('parking fees'),indent=2))
