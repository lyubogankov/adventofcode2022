'''
shape points
    1   rock     = A = X
    2   paper    = B = Y
    3   scissors = C = Z

outcome points
    0   loss
    3   tie
    6   win
'''
# encoding knowledge into constants / dicts

ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'
WIN = 'win'
TIE = 'tie'
LOSS = 'loss'
input_decoder = {
    'A' : ROCK,
    'B' : PAPER,
    'C' : SCISSORS,
    
    'X' : LOSS,
    'Y' : TIE,
    'Z' : WIN,
}
shape_points = {
    ROCK : 1,
    PAPER : 2,
    SCISSORS : 3,
}
outcome_points = {
    WIN : 6,
    TIE : 3,
    LOSS : 0
}
outcomes = {
    # (opp_shape, our_shape) : outcome
    
    (ROCK, PAPER) : WIN,
    (ROCK, ROCK) : TIE,
    (ROCK, SCISSORS) : LOSS,
    
    (PAPER, PAPER) : TIE,
    (PAPER, ROCK) : LOSS,
    (PAPER, SCISSORS) : WIN,

    (SCISSORS, PAPER) : LOSS,
    (SCISSORS, ROCK) : WIN,
    (SCISSORS, SCISSORS) : TIE,
}

strategy_guide = 'input.txt'
total_score = 0
with open(strategy_guide, 'r') as strategyguide:
    for line in strategyguide.readlines():
        # parse line, convert to program representation
        opponent_symbol, our_symbol = line.replace('\n', '').split(' ')
        opponent_shape = input_decoder[opponent_symbol]
        desired_outcome = input_decoder[our_symbol]
        # outcome (known from strat guide)
        total_score += outcome_points[desired_outcome]
        # shape -- what shape do we need for intended outcome?
        for (opp_shape, our_shape), outcome in outcomes.items():
            if opp_shape == opponent_shape and outcome == desired_outcome:
                total_score += shape_points[our_shape]
                break
print(f'Total score using {strategy_guide}: {total_score}')


# reflection
#
# In the constants section, I only needed to change to input decoder to map X, Y, Z from shapes -> desired outcomes.
# The remainder of the program changed a bit to look up shape from outcome, but other than that flowed mostly the same.