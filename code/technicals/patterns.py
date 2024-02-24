import pandas as pd

'''
breakdown of each stratgey:

Single Candle Patterns
Hammer
downward trend followed by small body in top portion (green body) indicating postitve upward trend. Bullish trend

Hanging Man
upward trend followed by small body in top portion (red body) indicating negative downward trend. Bearish trend

Inverted hammer
downward trend followed by small body in bottom portion (green body) indicating postitve upward trend.

Shooting Star
upward trend followed by small body in bottom portion (red body) indicating negative downward trend.

Spinning Top
indicate neutrailty or unclear what direction trends might go in can be red or green candle with small body

Marubozu
Where candle is very large and body is around 100% of the candle range

Dual Candle Stick Patterns
Engulfing (Bullish or Bearish options)
    Bullish
    downward trend (so all red candles) then at bottom we have
    a smaller red candle and then right after it a very large green candle that is larger
    than the red candle before it. Trend is going to go up 

    Bearish
    upward trend (so all green candles) then at top we have a smaller green candle then right
    after it we have very larger red candle that is larger than previous green candle
    Trend is going to go down

Tweezer Top
Bearish - green one followed by red one
Body in bottom half of candle and they have very similar if not the same body height, low, open and close

Tweezer Bottom
Bullish - red one followed by green one
Bottom half of candle and they have very similar if not the same body height, low, open and close

Triple Candle Stick Pattern
Morning Star
downward trend then u have red candle then small either red or green candle then followed 
by green candle. This 3rd candle must be greater than midpoint of first candle in triplet

Evening Star
upward trend then green candle then small either green or red candle then followed by reversal candle
then red candle whos close price is below midpoint of first candle
'''

#my guesses for what an apprioate candle would look like for each of these patterns(percents of total candle)

#conditions: how far from the bottom is the candle so max is 75% from bottom
#second is body size must be less than 15%
HANGING_MAN_HEIGHT = 75.0 
HANGING_MAN_BODY = 15.0

#conditions: how far from bottom is the candle so around 25% from bottom 
#second is body size must be around 15% 
SHOOTING_STAR_HEIGHT = 25.0
SHOOTING_STAR_BODY = 15.0

#conditions: min height from bottom is 40% and max height is 60% 
#body size is around 15%
SPINNING_TOP_MIN = 40.0
SPINNING_TOP_MAX = 60.0
SPINNING_TOP_BODY = 15.0

#body % must be greater than around 98% so very large body
MARUBOZU = 98.0

#factor how checking how much bigger the second candle is compared to first (10%)
ENGULFING_FACTOR = 1.1

#1st candle out of the tree we want a large candle at least 90%
MORNING_STAR_PREV2_BODY = 90.0
#2nd candle we want to be really small so 10%
MORNING_STAR_PREV_BODY = 10.0

#body size min is 15
TWEEZER_BODY = 15.0
#percentage diff between two candles should be very similar so 0.01
TWEEZER_HL = 0.01
#up the candle max 40% 
TWEEZER_TOP_BODY = 40.0
#around 60% from bottom
TWEEZER_BOTTOM_BODY = 60.0

apply_marubozu = lambda x: x.body_perc > MARUBOZU

def apply_hanging_man(row):
    if row.body_bottom_perc > HANGING_MAN_HEIGHT:
        if row.body_perc < HANGING_MAN_BODY:
            return True
    return False

def apply_shooting_star(row):
    if row.body_top_perc < SHOOTING_STAR_HEIGHT:
        if row.body_perc < SHOOTING_STAR_BODY:
            return True
    return False

def apply_spinning_top(row):
    if row.body_top_perc < SPINNING_TOP_MAX:
        if row.body_bottom_perc > SPINNING_TOP_MIN:
            if row.body_perc < SPINNING_TOP_BODY:
                return True
    return False

def apply_engulfing(row):
    #directions must be different (must be red and green side by side)
    if row.direction != row.direction_prev:
        if row.body_size > row.body_size_prev * ENGULFING_FACTOR:
            return True
    return False

def apply_tweezer_top(row):
    #take postive value using abs
    if abs(row.body_size_change) < TWEEZER_BODY:
        #check if we changed direction and current direction is red(bearish)
        if row.direction == -1 and row.direction != row.direction_prev:
            #check if percentage changes match up to the constants
            if abs(row.low_change) < TWEEZER_HL and abs(row.high_change) < TWEEZER_HL:
                if row.body_top_perc < TWEEZER_TOP_BODY:
                    return True
    return False               

def apply_tweezer_bottom(row):
    if abs(row.body_size_change) < TWEEZER_BODY:
        if row.direction == 1 and row.direction != row.direction_prev:
            if abs(row.low_change) < TWEEZER_HL and abs(row.high_change) < TWEEZER_HL:
                if row.body_bottom_perc > TWEEZER_BOTTOM_BODY:
                    return True
    return False     

#add direction by default its 1
def apply_morning_star(row, direction=1):
    #1st candle at start of triple candle pattern is large enough
    if row.body_perc_prev_2 > MORNING_STAR_PREV2_BODY:
        #2nd candle in pattern is small enough
        if row.body_perc_prev < MORNING_STAR_PREV_BODY:
            #if current candle is same direction we are sending in
            #and first candle is not equal to that 3rd one
            if row.direction == direction and row.direction_prev_2 != direction:

                #now check bullish or bearish compare with midpoint 
                if direction == 1: #bullish reversal 
                    if row.mid_c > row.mid_point_prev_2:
                        return True
                else: #bearish reversal 
                    if row.mid_c < row.mid_point_prev_2:
                        return True
    return False

#apply candle stats 
#input is the panda dataframe
def apply_candle_props(df: pd.DataFrame):
    #copy dataframe
    df_an = df.copy()

    #we are trying to calc the aspects from the candle picture
    
    #direction: green or red candle will give us - # if red and +# if green vvvv
    direction = df_an.mid_c - df_an.mid_o

    #body_size this is the entire length of green or red part of candle
    #abs gives us back all postive numbers
    body_size = abs(direction)

    #now change the direction to 1 if green candle and -1 if red candle
    direction = [1 if x >= 0 else -1 for x in direction]

    #the entire length of the candle top to bottom
    full_range = df_an.mid_h - df_an.mid_l

    #total body percentage
    body_perc = (body_size / full_range) * 100

    #position of lower part of body and lower part, either open or close price depedning on candle color
    body_lower = df_an[['mid_c','mid_o']].min(axis=1) #min value of open and close price
    body_upper = df_an[['mid_c','mid_o']].max(axis=1) #max value of open and close price

    #percentages of upper and lower sections of candle
    body_bottom_perc = ((body_lower - df_an.mid_l) / full_range) * 100
    body_top_perc = 100 - ((( df_an.mid_h - body_upper) / full_range) * 100)

    #for triple stick patterns to get midpoints of a candle
    mid_point = full_range / 2 + df_an.mid_l

    #we percentage changes for low and the highs compared with prev candle
    #and percentage change for body size 
    low_change = df_an.mid_l.pct_change() * 100
    high_change = df_an.mid_h.pct_change() * 100
    body_size_change = body_size.pct_change() * 100

    #have calculations seperate up top^^
    #easier to split up code into claculations up top 
    #then have the assignemnts down below like such 
    df_an['body_lower'] = body_lower
    df_an['body_upper'] = body_upper
    df_an['body_bottom_perc'] = body_bottom_perc
    df_an['body_top_perc'] = body_top_perc
    df_an['body_perc'] = body_perc
    df_an['direction'] = direction
    df_an['body_size'] = body_size
    df_an['low_change'] = low_change
    df_an['high_change'] = high_change
    df_an['body_size_change'] = body_size_change
    df_an['mid_point'] = mid_point
    #since triple candle pattern require to go 2 back we use .shift to see 2 candles back
    df_an['mid_point_prev_2'] = mid_point.shift(2)
    #for dual stick patterns we need prev candle info so we use shift function to capture
    #previous candle stick data
    df_an['body_size_prev'] = df_an.body_size.shift(1)
    df_an['direction_prev'] = df_an.direction.shift(1)
    df_an['direction_prev_2'] = df_an.direction.shift(2)
    df_an['body_perc_prev'] = df_an.body_perc.shift(1)
    df_an['body_perc_prev_2'] = df_an.body_perc.shift(2)

    return df_an

def set_candle_patterns(df_an: pd.DataFrame):
    df_an['HANGING_MAN'] = df_an.apply(apply_hanging_man, axis=1)
    df_an['SHOOTING_STAR'] = df_an.apply(apply_shooting_star, axis=1)
    df_an['SPINNING_TOP'] = df_an.apply(apply_spinning_top, axis=1)
    df_an['MARUBOZU'] = df_an.apply(apply_marubozu, axis=1)
    df_an['ENGULFING'] = df_an.apply(apply_engulfing, axis=1)
    df_an['TWEEZER_TOP'] = df_an.apply(apply_tweezer_top, axis=1)
    df_an['TWEEZER_BOTTOM'] = df_an.apply(apply_tweezer_bottom, axis=1)
    df_an['MORNING_STAR'] = df_an.apply(apply_morning_star, axis=1)
    df_an['EVENING_STAR'] = df_an.apply(apply_morning_star, axis=1, direction=-1)

#take in dataframe and make new dataframe with candle properites apply the candle properties
def apply_patterns(df: pd.DataFrame):
    df_an = apply_candle_props(df)
    set_candle_patterns(df_an)
    return df_an