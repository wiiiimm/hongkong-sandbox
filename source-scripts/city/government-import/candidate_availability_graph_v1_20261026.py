"""Validate exact proposed candidate availability edges; no approval semantics."""


def validate(uids, pairs):
    assert uids and len(uids)==len(set(uids))
    edges=[tuple(value.split(','))for value in pairs]
    assert len(edges)==len(set(edges)),'Duplicate availability edge'
    assert all(len(edge)==2 and edge[0]!=edge[1] and set(edge)<=set(uids)for edge in edges),'Invalid availability endpoint'
    peers={uid:sorted(v for u,v in edges if u==uid)for uid in uids}
    done,visiting,ordered=set(),set(),[]
    def visit(uid):
        if uid in done:return
        assert uid not in visiting,'Proposed candidate availability cycle'
        visiting.add(uid)
        for peer in peers[uid]:visit(peer)
        visiting.remove(uid);done.add(uid);ordered.append(uid)
    for uid in uids:visit(uid)
    return peers,ordered
