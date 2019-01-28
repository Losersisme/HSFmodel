class Portfolio:

    def __init__(self, source=None, mode='ref'):
        import pandas as pd
        self.source = pd.read_csv(source, index_col=('QYEAR'))
        self.tlist = None

    def add(self, tickers):
        if self is None:
            self = Portfolio()
        if tickers is not None:
            fixed = []
            for item in tickers:
                if ' US Equity' not in item:
                    item += ' US Equity'
                fixed.append(item)
            if self.tlist is None:
                self.tlist = list(set(fixed))
            else:
                self.tlist += fixed
                self.tlist = list(set(self.tlist))
        return self

    def set_source(self, source):
        self.source = source

    def set_mode(self, mode):
        if mode != 'ref' or mode != 'fetch':
            raise ValueError('mode must be "ref" or "fetch"')
        else:
            self.mode = mode
            
    def _update(self):
        if self.source is None:
            raise ValueError('No source specified for Portfolio')
            
    def _calc_eqbeta(self):
        # calc the portfolio beta
        if source is None:
           raise ValueError('A data source must be specified to perform Porfolio functions in "ref" mode')

    def qtr_return(self, qyear='all'):
        if self.source is None or self.tlist is None:
            raise ValueError('No source specified for Portfolio')
        if qyear is 'all':
            return None
        # Use QYear class to verify format of input
        vyears = sorted(set(self.source.index.get_level_values(0).values))
        if qyear not in vyears:
            raise ValueError('Requested QYear is not in the data source, %s' % qyear)
        return str((self.source.loc[self.source['TICKER'].isin(self.tlist)].loc[qyear,'RETURN'].sum()) * 100) + '%'

    def beta(self, qyear='all'):
        if self.source is None or self.tlist is None:
            raise ValueError('No source specified for Portfolio')
        if qyear is 'all':
            return None
        # Use QYear class to verify format of input
        vyears = sorted(set(self.source.index.get_level_values(0).values))
        if qyear not in vyears:
            raise ValueError('Requested QYear not available in data source, %s' % qyear)
        return self.source.loc[self.source['TICKER'].isin(self.tlist)].loc[qyear,'ADJUSTED_BETA'].mean()
    
    def sharpe(self, qyear='all'):
        if self.source is None or self.tlist is None:
            raise ValueError('No source specified for Portfolio')
        if qyear is 'all':
            return None
        # Use QYear class to verify format of input
        vyears = sorted(set(self.source.index.get_level_values(0).values))
        if qyear not in vyears:
            raise ValueError('Requested QYear not available in data source, %s' % qyear)
        ret = self.source.loc[self.source['TICKER'].isin(self.tlist)].loc[qyear,'RETURN'].sum()
        std_ret = self.source.loc[self.source['TICKER'].isin(self.tlist)].loc[qyear,'RETURN'].std()
        return (ret - 0.029)/std_ret