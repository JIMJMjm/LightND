import statsmodels.api as sm

from config import read_json, CONFIG

RLM_NEIGHBOR_RANGE = CONFIG['RLM_NEIGHBOR_RANGE']


def curve(x, y):
    X = sm.add_constant(x)
    model = sm.RLM(y, X).fit()
    slope = model.params[1]
    intercept = model.params[0]
    return slope, intercept


def fillter(pots, barrier, loose=RLM_NEIGHBOR_RANGE):
    re = []
    le, ri = barrier - loose, barrier + loose
    for i in INTERVAL:
        if le < i < barrier:
            le = i
        if barrier < i < ri:
            ri = i

    for pot in pots:
        if le <= pot[0] <= ri:
            re.append(pot)
    return re


def packed(num):
    dd = curve(*zip(*fillter(pos, num)))
    evaluation = num * dd[0] + dd[1]
    print([float(i) for i in dd], '\n', f'Anticipation: {evaluation}')
    return evaluation


INTERVAL = (22284, 27476, 103972, 105781)
pos = read_json('samples.json')


if __name__ == '__main__':
    print(packed(87909))
