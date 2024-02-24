import pandas as pd

#take in dataframe, s is standard dev
def BollingerBands(df: pd.DataFrame, n=20, s=2):
    #calc typical price, dataframe is made up of bunch of series stuck next to each other
    #all have index next to series 
    #will be temp series used for calc
    typical_p = ( df.mid_c + df.mid_h + df.mid_l ) / 3
    #col of dataframe, rolling end period standard dev
    stddev = typical_p.rolling(window=n).std()
    df['BB_MA'] = typical_p.rolling(window=n).mean()
    df['BB_UP'] = df['BB_MA'] + stddev * s 
    df['BB_LW'] = df['BB_MA'] - stddev * s
    return df

#we need ATR to calcaute keltner channels 
def ATR(df: pd.DataFrame, n=14):
    prev_c = df.mid_c.shift(1)
    tr1 = df.mid_h - df.mid_l
    tr2 = abs(df.mid_h - prev_c)
    tr3 = abs(prev_c - df.mid_l)
    #max with axis one will give max value in dataframe 
    #we have 3 cols vv and from those we will get max value
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    df[f"ATR_{n}"] = tr.rolling(window=n).mean()
    return df

def KeltnerChannels(df: pd.DataFrame, n_ema=20, n_atr=10):
    #ewm is exponted weighted moving, 
    df['EMA'] = df.mid_c.ewm(span=n_ema, min_periods=n_ema).mean()
    df = ATR(df, n=n_atr)
    c_atr = f"ATR_{n_atr}"
    #upper line
    df['KeUp'] = df[c_atr] * 2 + df.EMA
    #lower line
    df['KeLo'] = df.EMA - df[c_atr] * 2
    #we dont need ATR col so we will get rid of it here vvvv
    df.drop(c_atr, axis=1, inplace=True)
    return df


def RSI(df: pd.DataFrame, n=14):
    alpha = 1.0 / n
    gains = df.mid_c.diff() #writen as change in code source

    #logic i wrote in notebook so 0 is if it wasnt a gain or loss and 
    #postive number tells us gain or loss amount
    wins = pd.Series([ x if x >= 0 else 0.0 for x in gains ], name="wins") #it was called gain
    #turn into postive value
    losses = pd.Series([ x * -1 if x < 0 else 0.0 for x in gains ], name="losses") #called loss in source code

    wins_rma = wins.ewm(min_periods=n, alpha=alpha).mean()
    losses_rma = losses.ewm(min_periods=n, alpha=alpha).mean()

    rs = wins_rma / losses_rma

    df[f"RSI_{n}"] = 100.0 - (100.0 / (1.0 + rs))
    return df

def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9):

    #exponeital moving weighted average for 2 lines
    ema_long = df.mid_c.ewm(min_periods=n_slow, span=n_slow).mean()
    ema_short = df.mid_c.ewm(min_periods=n_fast, span=n_fast).mean()
    
    df['MACD'] = ema_short - ema_long
    df['SIGNAL'] = df.MACD.ewm(min_periods=n_signal, span=n_signal).mean()
    df['HIST'] = df.MACD - df.SIGNAL

    return df





























