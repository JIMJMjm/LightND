import statsmodels.api as sm
import json


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def curve(x, y):
    X = sm.add_constant(x)

    model = sm.RLM(y, X).fit()

    slope = model.params[1]
    intercept = model.params[0]

    return slope, intercept


def classify(match):
    L1 = []
    L2 = []
    L3 = []
    L4 = []
    for i in match:
        if i[0] < 27476:
            L1.append(i)
        elif i[0] < 103972:
            L2.append(i)
        elif i[0] < 105781:
            L3.append(i)
        else:
            L4.append(i)
    return L1, L2, L3, L4


def unzip(mat):
    x = [i[0] for i in mat]
    y = [i[1] for i in mat]
    return x, y


def fillter(pots, barrier, loose=1000):
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
    dd = curve(*unzip(fillter(pos, num)))
    print(dd)
    evaluation = num * dd[0] + dd[1]
    print(evaluation)
    return evaluation


INTERVAL = (22284, 27476, 103972, 105781)
pos = read_json('samples.json')
