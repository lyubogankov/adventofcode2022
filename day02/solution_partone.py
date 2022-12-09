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
shapes = {
    'A' : ROCK,
    'X' : ROCK,
    'B' : PAPER,
    'Y' : PAPER,
    'C' : SCISSORS,
    'Z' : SCISSORS,
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
        # parse line, convert to shapes
        opponent_symbol, our_symbol = line.replace('\n', '').split(' ')
        opponent_shape = shapes[opponent_symbol]
        our_shape      = shapes[our_symbol] 
        # outcome
        outcome = outcomes[(opponent_shape, our_shape)]
        total_score += outcome_points[outcome]
        # shape points
        total_score += shape_points[our_shape]
print(f'Total score using {strategy_guide}: {total_score}')
