"""A provenance-preserving graph retrieval exercise, not the GraphRAG framework."""
EDGES=[('Ada','works_on','Project Atlas','S1'),('Project Atlas','uses','Sensor Q','S2'),('Sensor Q','located_in','Lab West','S3')]
def walk(start, depth=2):
    frontier={start}; found=[]
    for _ in range(depth):
        selected=[e for e in EDGES if e[0] in frontier and e not in found]
        found.extend(selected);frontier={e[2] for e in selected}
    return found
if __name__=='__main__':
    assert [x[3] for x in walk('Ada')]==['S1','S2']
    assert walk('Unknown')==[]
    print(walk('Ada'));print('PASS: two-hop path and missing entity')
