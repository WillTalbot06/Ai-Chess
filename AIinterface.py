import random

def randomMove(possibleMoves):
  return random.choice(possibleMoves)

def fixedPieceEvaluation(ScoredMoves):
  if ScoredMoves == []:
    print("No scored moves to Eval")
  heighest = [ScoredMoves.pop(0)]
  for move in ScoredMoves:
    if move[1] > heighest[0][1]:
      heighest = [move]
    elif move[1] == heighest[0][1]:
      if move not in heighest:
        heighest.append(move)
  return random.choice(heighest)

def aiPromotion():
  return 'Q'