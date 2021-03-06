from __future__ import division
import core
import random

from sklearn import preprocessing

class Dataset(object):
    def __init__(self):
        self.data = []
        self.params = {}

    def readFile(self, localfile, classCol=None, ignoreCol=None, weights=None):
        f = open(localfile, "r")
        self.params['Clusters'] = {}
        classList = []
        features = []
        for cols in [raw.strip().split(',') for raw in f]:
            features.append(cols)
        # random.shuffle(features)

        for columns in features:
            if classCol is not None:
                currClass = columns[classCol]
                del columns[classCol]
                if ignoreCol is not None:
                    del columns[ignoreCol]
                self.data.append([float(col) for col in columns])

                if currClass in self.params['Clusters'].keys():
                    self.params['Clusters'][currClass] += 1
                else:
                    self.params['Clusters'][currClass] = 1
                classList.append(currClass)
            else:
                self.data.append([float(col) for col in columns])
        if len(classList) > 0:
            if isinstance(classList[0], str):
                self.params['ClusterMap'] = self.toIntList(classList)
            else:
                self.params['ClusterMap'] = sorted(classList)

        self.params['Size'] = len(self.data)
        self.params['Features'] = len(self.data[0])
        self.params['Classes'] = len(self.params['Clusters'].keys()) if 'Clusters' in self.params else None
        self.params['Feature weights'] = weights
        self.normalize()

    def readArray(self, arr, weights):
        self.data = [[float(t[0]), float(t[1])] for t in arr]
        random.shuffle(self.data)

        self.params['Size'] = len(self.data)
        self.params['Features'] = len(self.data[0])
        self.params['Classes'] = len(self.params['Clusters'].keys()) if 'Clusters' in self.params else None
        self.params['Feature weights'] = weights
        self.params['ClusterMap'] = None

        self.normalize()

    def normalize(self):

        for dim in range(self.getColNum()):
            min_d, max_d = min([t[dim] for t in self.data]), max([t[dim] for t in self.data])
            for t in self.data:
                t[dim] -= min_d
                if max_d != min_d:
                    t[dim] /= (max_d - min_d)

        # self.data = preprocessing.scale(self.data)
        # najmanji_broj = min([koord for tocka in self.data for koord in tocka])
        # najveci_broj = max([koord for tocka in self.data for koord in tocka])
        # self.data = [[(dim - najmanji_broj) / (najveci_broj - najmanji_broj) for dim in tocka] for tocka in self.data]

        #print najveci_broj

    def getColNum(self):
        return len(self.data[0])

    def getRowNum(self):
        return len(self.data)

    # colormap ovdje mora sadrzavati sve brojeve od 0 do max(colormap)
    def getFitnessOf(self, config, colormap):
        particija = [[] for x in range(len(set(colormap)))]
        for i, t in enumerate(self.data):
           particija[colormap[i] - 1].append(t)
        testni = core.Kromosom(config, [], True)
        return testni.fitness(particija)

    def getOptimalFitness(self, config):
        return self.getFitnessOf(config, self.params['ClusterMap'])

    def toIntList(self, classes):
        class_map = {}
        class_list = []
        i = 0
        for c in classes:
            if c in class_map:
                class_list.append(class_map[c])
            else:
                i = i + 1
                class_map[c] = i
                class_list.append(i)
        return class_list


class Iris(Dataset):

    def __init__(self):
        super(Iris, self).__init__()
        weights = [0.7826, -0.4194, 0.9490, 0.9565]
        self.localfile = '../data/iris.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile, classCol=4, weights=weights)

class Wine(Dataset):

    def __init__(self):
        super(Wine, self).__init__()
        self.localfile = '../data/wine.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile, classCol=0)

class Cancer(Dataset):

    def __init__(self):
        super(Cancer, self).__init__()
        self.localfile = '../data/breast-cancer-wisconsin.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile)

class Glass(Dataset):

    def __init__(self):
        super(Glass, self).__init__()
        weights = [-0.1642, 0.5030, -0.7447, 0.5988, 0.1515, -0.0100, 0.0007, 0.5751, -0.1879 ]
        self.localfile = '../data/glass.data'
        Dataset.__init__(self)
        Dataset.readFile(self, self.localfile, classCol=10, ignoreCol=0, weights=weights)

class Naive(Dataset):
    def __init__(self):
        super(Naive, self).__init__()
        weights = [1, 1]
        tocke = [(36, 39), (20, 42), (26, 27), (23, 43), (32, 33), (24, 39), (36, 39), (23, 32), (36, 44), (24, 37),
             (26, 31), (27, 30), (37, 45), (37, 28), (24, 25), (29, 44), (29, 26), (31, 28), (32, 35), (36, 27),
             (34, 26), (30, 30), (22, 27), (22, 42), (30, 35), (23, 40), (32, 27), (32, 28), (26, 33), (20, 39),
             (30, 40), (28, 33), (26, 42), (45, 50), (52, 53), (57, 45), (48, 36), (55, 54), (49, 55), (49, 45),
             (56, 51), (46, 52), (55, 49), (58, 52), (59, 38), (65, 47), (47, 38), (51, 43), (57, 45), (48, 39),
             (56, 41), (59, 53), (49, 52), (57, 37), (60, 54), (58, 54), (62, 44), (56, 46), (56, 39), (56, 49),
             (57, 54), (53, 36), (48, 48), (46, 43), (61, 45), (62, 49), (52, 54), (56, 80), (63, 78), (56, 64),
             (62, 70), (62, 67), (73, 79), (57, 68), (68, 79), (61, 69), (64, 71), (59, 76), (67, 69), (56, 67),
             (59, 61), (71, 66), (59, 79), (61, 66), (63, 66), (65, 67), (65, 75), (56, 60), (62, 60), (70, 76),
             (74, 70), (74, 80), (58, 68), (62, 65), (65, 77), (56, 73), (58, 67), (63, 64), (56, 79), (61, 62)]
        Dataset.__init__(self)
        Dataset.readArray(self, tocke, weights)

