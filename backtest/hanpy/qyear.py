# Wrapper class for Q-year format string values
class QYear:
    
    def __init__(self, label=None):
        if label is None:
            self.label = None
            self.year = 0
            self.quarter = 0
        elif len(label) != 6:
            raise ValueError('%s does not match correct value format: "YYYYQ#"' % label)
        else:
            self.label = label
            self.year = int(label[0:4])
            self.quarter = int(label[5])
    
    def __str__(self):
        return self.label
    
    def __repr__(self):
        return '<QYear year:%d, quarter:%d, label:%s>' % (self.year, self.quarter, self.label)
            
    def from_value(self, year, quarter):
        self.set_year(year)
        self.set_quarter(quarter)
        return self

    def set_year(self, year):
        self.year = year
        self.label = str(self.year) + 'Q' + str(self.quarter)
        return self

    def set_quarter(self, quarter):
        if quarter > 4 or quarter < 0:
            raise ValueError('Q-year quarter value must be between 1 and 4')
        self.quarter = quarter
        self.label = str(self.year) + 'Q' + str(self.quarter)
        return self

    # shift() - adds or subtracts quarters/years from a QYear object
    def shift(self, qMove, inplace=False):
        tempy = self.year
        tempq = self.quarter
        while qMove != 0:
            if qMove > 0:
                if tempq == 4:
                    tempy += 1
                    tempq = 1
                else:
                    tempq += 1
                qMove -= 1                   
            else:
                if tempq == 1:
                    tempy -= 1
                    tempq = 4
                else:
                    tempq -= 1
                qMove += 1
        if inplace:
            self.set_year(tempy)
            self.set_quarter(tempq)
            return self
        else:
            return QYear().set_year(tempy).set_quarter(tempq)
    
    # split() 
    def make_range(self, count, output='list', style='string'):
        out = []
        out.append(str(self))
        while count != -1 or count != 1:
            if count > 0:
                out.append(str(self.shift(1)))
                count -= 1
            else:
                out.insert(0, str(self.shift(-1)))
                count += 1
        return out

# q_diff() - returns the number of quarters between the start of q1 and the end of q2
#   a negative return value indicates that q1 occurs after q2
#   a positive return value indicates that q1 occurs before q2
#   a return value of 0 indicates that q1 and q2 are the same quarter
def q_diff(q1, q2):
    q1 = QYear(str(q1))
    q2 = QYear(str(q2))
    out = 0
    ydiff = q1.year - q2.year
    if ydiff > 0:
        out += -((ydiff - 1) * 4 + (4 - q1.quarter) + (4 - q2.quarter))
    elif ydiff < 0:
        out += -((ydiff - 1) * 4 + (4 - q1.quarter) + (4 - q2.quarter))
    else:
        out += q2.quarter - q1.quarter
    return out
    
# q_fill() - returns a list of all QYear labels from X to Y
def q_fill(start, end, output='list', style='string'):
    start = QYear(str(start))
    end = QYear(str(end))
    out = []
    out.append(start.label)
    diff = q_diff(start, end)
    while diff != 0:
        if diff < 0:
            start = start.shift(-1)
            out.append(start.label)
            diff = q_diff(start, end)
        elif diff > 0:
            start = start.shift(1)
            out.append(start.label)
            diff = q_diff(start, end)
    return out
    