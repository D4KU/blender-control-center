import json
import re


def serialize_ctrls(context):
    vl = context.view_layer
    controls = []
    for c in context.scene.ctrls:
        states = []
        refattr = c.refpropstr
        targets = vl.layer_collection.children if c.action == 'COL' \
            else vl.objects

        for s in c.states:
            matches = []
            if s.matchby == 'REF':
                for p in s.patterns:
                    match = p[refattr]
                    if match:
                        matches.append(match.name)
            else:
                for t in targets:
                    for p in s.patterns:
                        if re.fullmatch(p.name, t.name):
                            matches.append(t.name)
                            break

            states.append({
                'name': s.name,
                'targets': matches,
            })
        controls.append({
            'name': c.name,
            'type': c.type,
            'action': c.action,
            'states': states,
        })

    return {'controls': controls}


def write(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
