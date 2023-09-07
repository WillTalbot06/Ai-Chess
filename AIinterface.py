import random

def randomMove(possibleMoves):
  return random.choice(possibleMoves)

def fixedPieceEvaluation(ScoredMoves):
  heighest = ('',0)
  for move in ScoredMoves:
    if move[1] > heighest[1]:
      heighest = move
  return heighest[0]

def aiPromotion():
  return 'Q'