"""Pure positive-area terrain dependency closure; no geometry or acceptance edits."""


def intersects(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def union(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def closure(initial, nodes):
    assert len({n['url'] for n in nodes}) == len(nodes)
    bounds, required = list(initial), set()
    assert bounds[0] < bounds[2] and bounds[1] < bounds[3]
    rounds = []
    while True:
        added = []
        # Evaluate one complete round against the same envelope. Input ordering
        # must not change the final dependency set or envelope.
        for node in nodes:
            if node['url'] not in required and any(intersects(bounds, b) for b in [node['coarseBounds'], *node['packedBounds']]):
                added.append(node)
        if not added:
            return dict(bounds=bounds, requiredUrls=sorted(required), rounds=rounds)
        rounds.append(sorted(n['url'] for n in added))
        for node in added:
            required.add(node['url'])
            bounds = union(bounds, node['coarseBounds'])
            for box in node['packedBounds']:
                bounds = union(bounds, box)
