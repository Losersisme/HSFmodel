
class CutoffScoreConfig:
    
    def __init__(self, cutoff, mag=1):
        if '%' in str(cutoff):
            self.style = 'percentile'
        else:
            self.style = 'value'
        self.cutoff = float(str(cutoff).split('%')[0])
        self.mag = mag
        self.scores = [1*mag, 0]
        self.composite = None
        
    def applyto(self, array, weight='higher'):
        import numpy as np
        arrayFixed = array[~np.isnan(array)]
        if weight != 'higher' and weight != 'lower':
            raise ValueError('weight must be "higher" or "lower"')
        if weight == 'higher':
            self.composite = ('higher', (1.00, np.percentile(arrayFixed, 100-self.cutoff)))
        else:
            self.composite = ('lower', (1.00, np.percentile(arrayFixed, self.cutoff)))
        return self
    
def score(composite, val):
    if composite[0] == 'higher':
        # Higher values score better
        score = 0
        for pair in composite[1:]:
            if val >= pair[1]:
                score = pair[0]
        return score
    elif composite[0] == 'lower':
        # Lower values score better
        score = 0
        for pair in composite[1:]:
            if val <= pair[1]:
                score = pair[0]
        return score
    else:
        raise ValueError('Invalid composite score')