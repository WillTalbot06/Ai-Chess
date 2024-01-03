import pygame, sys, time, copy
from pygame.locals import QUIT
import AIinterface as interface

SIZE = 328
SQUARESIZE = SIZE / 8
WINDOWSIZE = (SIZE + SQUARESIZE, SIZE + 2 * SQUARESIZE)
WINDOWWIDTH, WINDOWHEIGHT = WINDOWSIZE

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
MAGENTA = (255,0,255)
CYAN = (0,255,255)
BOARD_COLOURS = [(244,164,96), (139,69,19)]
BACK_COLOUR = BLACK

pygame.init()
screen = pygame.display.set_mode(WINDOWSIZE)
font = pygame.font.Font(None, int(SQUARESIZE))
pygame.display.set_caption("Chess")
screen.fill(BACK_COLOUR)
pygame.mouse.set_cursor(pygame.cursors.diamond)

playTxtMoves = False
AIType = 'minimaxNode'
whiteAI = False
blackAI = False
SEARCHDEPTH = 1 #For original minimax (minimaxRec)
MAXDEPTH = 2 # for new minimax (minimaxNode)

class Piece:
  def __init__(self,type,colour,start):
    self.type = type
    self.colour = colour
    #Gets code in format colourType. Useful for references
    for piece in piecesCodes:
      if piece[1] == self.type:
        self.code = self.colour[0].lower() + piece[0]
    self.id = self.code + str(start)
    if self.type == 'Pawn':
      self.EnPassant = False #if piece has been taken by enpassant so it can be deleted later
    if self.type == 'King':
      self.castleing = None #stores which way to castle. If not then none
   
  def __str__(self):
    return f"{self.code} {self.GetPosition()}"

  def __eq__(self,piece):
    try:
      return self.id == piece.id
    except:
      return False

  def __repr__(self):
    return str(self)

  def GetPosition(self):
    for i in range(8):
      for j in range(8):
        if board.board[i][j] == self:
          return (j,i) #in form x,y

  def reset(self):
    for piece in piecesCodes:
      if piece[1] == self.type:
        self.code = self.colour[0].lower() + piece[0]

class Board:
  def __init__(self,setup=True):
    #Creates board
    board = []
    for i in range(8):
      board.append([None]*8)
    if setup:
      #Creates and places pieces
      for colour in range(2):
        row = colour
        if colour == 1:
          row = 7
    
        board[row][0] = Piece(piecesCodes[1][1],colours[colour],0)
        board[row][7] = Piece(piecesCodes[1][1],colours[colour],7)
        board[row][1] = Piece(piecesCodes[4][1],colours[colour],1)
        board[row][6] = Piece(piecesCodes[4][1],colours[colour],6)
        board[row][2] = Piece(piecesCodes[2][1],colours[colour],2)
        board[row][5] = Piece(piecesCodes[2][1],colours[colour],5)
        board[row][3] = Piece(piecesCodes[3][1],colours[colour],3)
        board[row][4] = Piece(piecesCodes[5][1],colours[colour],4)
    
        #Places pawns
        for i in range(8):
          if colour == 0:
            board[1][i] = Piece(piecesCodes[0][1],colours[colour],i)
          else:
            board[6][i] = Piece(piecesCodes[0][1],colours[colour],i)
  
    self.board = board
    self.Promotionable = []
    self.EnPassantable = []
    self.MovedPieces = []
    self.SavedMoves = []


  def __str__(self):
    txt = '\n'
    for i in range(9):
      for j in range(9):
        if i == 0 and j == 0:
          txt += "  "
        elif i == 0:
          txt += " " + chr(96+j) + " "
        elif j == 0:
          txt += " " + str(9-i) + " "
        elif self.board[i-1][j-1] != None:
          txt += self.board[i-1][j-1].code + " "
        else:
          txt += "   "
      txt += '\n'
    txt += '\n'
    return txt

  def Draw(self,selected=None):
    #Draws each piece on the board. Doesn't draw selected piece
    if selected != None:
      currentX,currentY = selected.GetPosition()
    for i in range(8):
      for j in range(8):
        pygame.draw.rect(screen,BOARD_COLOURS[(i+j) % 2],
                        pygame.Rect(SQUARESIZE*j,SQUARESIZE*i,SQUARESIZE,SQUARESIZE))
        if self.board[i][j] != None:
          piece = self.board[i][j]
          if selected != None:
            currentX,currentY = selected.GetPosition()
            if currentX != j or currentY != i:
              screen.blit(pieceImgs[piece.code], (SQUARESIZE*j, SQUARESIZE*i))
          else:
            screen.blit(pieceImgs[piece.code], (SQUARESIZE*j, SQUARESIZE*i))

    #draws selected piece
    if selected != None:
      x,y = pygame.mouse.get_pos()
      x -= SQUARESIZE / 2
      y -= SQUARESIZE / 2
      pos = x,y
      screen.blit(pieceImgs[self.board[currentY][currentX].code], pos)

  def GetKingsPosition(self):
    loc = []
    for j in range(8):
      for i in range(8):
        if self.board[i][j] != None and self.board[i][j].type == 'King':
          loc.append(self.board[i][j])
        if len(loc) == 2:
          return loc
    print("only one king")
    print(loc[0].id)
    print(board)

class Player:
  def __init__(self,colour,cursor=pygame.cursors.diamond,ai=False,type='Random'):
    self.colour = colour
    self.ai = ai
    self.playTime = 0
    self.cursor = cursor
    self.check = False
    self.aitype = type

  def __str__(self):
    return self.colour

  def __eq__(self,other):
    if isinstance(other,Player):
      return self.colour == other.colour
    return False

  def getPieces(self,position=False):
    pieces = []
    for i in range(8):
      for j in range(8):
        piece = board.board[i][j]
        if piece != None and piece.colour == self.colour:
          if position:
            pieces.append([piece,j,i])
          else:
            pieces.append(piece)
    return pieces

  def aiMove(self):
    if self.aitype == 'Random':
      return interface.randomMove(self.getPossibleMoves())
    if self.aitype == 'minimaxRec':
      moves = moveScoring(self,0)
      print(moves)
      move = interface.fixedPieceEvaluation(moves)
      print("Chosen move:",move)
      return move[0]
    if self.aitype == 'minimaxNode':
      move = minMax(Node(None,0,colours.index(self.colour)),False)
      print(move)
      return move[1]
  
  def getPossibleMoves(self):
    pieces = self.getPieces(True)
    possibleMoves = []
    for piece in pieces:
      x = piece[1]
      y = piece[2]
      piece = piece[0]
      for i in range(8):
        for j in range(8):
          valid = False
          if piece.type == 'Pawn' and (self.colour == 'White' and j<=y and j >= y-2 or self.colour == 'Black' and j>=y and j <= y+2) and abs(x-i) <= 1:
            valid = True
          elif piece.type == 'Bishop' and abs(y-j) == abs(x-i) and self.clear(x,y,i,j):
            valid = True
          elif piece.type == 'Rook' and (x == i or y == j) and self.clear(x,y,i,j):
            valid = True
          elif piece.type == 'King' and (abs(y-j) <= 1 and abs(x-i) <= 1 or abs(x-i) <= 3 and y==j and self.clear(x,y,i,j)):
            valid = True
          elif piece.type == 'Knight' and (abs(y-j) == 1 and abs(x-i) == 2 or abs(y-j) == 2 and abs(x-i) == 1):
            valid = True
          elif piece.type == 'Queen' and (x == i or y == j or abs(y-j) == abs(x-i)) and self.clear(x,y,i,j):
            valid = True
          if valid and board.board[j][i] != None and board.board[j][i].colour == self.colour:
            valid = False
          if valid:
            if LegalMove(x,y,i,j,self.colour,False):
              possibleMoves.append(formatMove(x,y,i,j,Save=False))
              if piece.type == 'King' and (abs(x-i)>1 or abs(y-j)>1):
                print(f"{piece} is castleing from {x},{y} to {i},{j}, {possibleMoves[-1]}")
    return possibleMoves

  def clear(self,x,y,i,j):
    if x == i:#same column
      k=1
      if y>j:
        k = -1
      for s in range(y+k,j,k):
        if board.board[s][x] != None:
          return False
      return True
    if y == j:#same row
      k=1
      if x>i:
        k = -1
      for s in range(x+k,i,k):
        if board.board[y][s] != None:
          return False
      return True
    if abs(y-j) == abs(x-i):#on diagonal
      if y-j == x-i:#\ diagonal
        k = 1
        if j < y:
          k = -1
        d = x-y
        for s in range(y+k,j,k):
          if board.board[s][s+d] != None:
            return False
        return True
      #/ diagonal
      k = 1
      if y > j:
        k = -1
      d = x+y
      for s in range(y+k,j,k):
        if board.board[s][d-s] != None:
          return False
      return True
    print(f"End of clear {x},{y} to {i},{j}")

class Node:
  def __init__(self,move,depth,prevPlayerID):
    self.move = move #move that has/will be done
    self.playerID = (prevPlayerID+1) % 2 #player whose turn is
    #id 1 is white, id 0 is black
    self.depth = depth #the layer of nodes this node is on
    self.children = []
    self.board = copy.deepcopy(board)
    self.originalPieces = []
    self.colour = colours[self.playerID]
    for k in range(8):
      for j in range(8):
        piece = self.board.board[k][j]
        if piece != None and piece.colour != self.colour and piece.type != 'King':
          self.originalPieces.append(piece)
    self.score = 0

  def isRoot(self):
    return self.move == None

  def isLeaf(self):
    return self.depth >= MAXDEPTH

  def CreateChildren(self):
    moves = Players[1-self.playerID].getPossibleMoves()
    for move in moves:
      self.children.append(Node(move,self.depth+1,self.playerID))
  
  def Score(self):
    #compare changes
    newPieces = []
    file = ''
    for i in range(8):
      for j in range(8):
        piece = board.board[i][j]
        if piece != None and piece.colour != self.colour and piece.type != 'King':
          newPieces.append(piece)
          file += str(piece)+', '
    value = 0
    if len(self.originalPieces) > len(newPieces):
      for piece in self.originalPieces:
        if piece not in newPieces:
          value += Values[piece.code[1]]
    
    if len(self.originalPieces) < len(newPieces):
      print("Scoring: more new pieces")
    return value

  def __str__(self):
    return str(self.move)
    

def performMove(move,colour):
  currentX,currentY,newX,newY,promotionPiece = GetMove(colour,move)
  piece = board.board[currentY][currentX]
  if LegalMove(currentX,currentY,newX,newY,colour):
    print(board.EnPassantable)
    for passantPiece in board.EnPassantable:
      if passantPiece.colour == colours[(i+1)%2]:
        #removes all passantable pieces from other colour
        board.EnPassantable.remove(passantPiece)
    print(board.EnPassantable)
    return True,piece,promotionPiece
  print("ILLEGAL MOVE GENERATED BY AI")
  return False,piece,promotionPiece

def doMove(node):
  legal,piece,promotionPiece = performMove(node.move,colours[node.playerID])
  promo = False
  checkmate = False
  stalemate = False
  validMoves = True
  if legal:
    if piece in board.Promotionable:
      if promotionPiece == None:
        promotionPiece = interface.aiPromotion()
      if promotionPiece != None:
        print(f"{piece} is promoting to {promotionPiece}")
        x,y = piece.GetPosition()
        for p in piecesCodes:
          if p[0] == promotionPiece:
            code = p[1]
        board.board[y][x].type = code
        board.board[y][x].reset()
        promo = True
        board.Promotionable.remove(piece)
    
    kings = board.GetKingsPosition()
    for king in kings:
      if inCheckmate(king):
        checkmate = True
        validMoves = False
  
    if not checkmate and Stalemate(Players[(i+1)%2]):
      stalemate = True
      validMoves = False
      print("Stalemate so no valid moves left")
  else:
    print(f"Illegal Move by AI {node.playerID}: {node.move}")
  return promo,checkmate,stalemate,validMoves

def minMax(node, isMaximisingPlayer,alpha = (-10000000,),beta = (10000000,)):
  global board
  promo,checkmate,stalemate = False,False,False
  if node.move is not None:#there is a move to do
    #Do move
    promo,checkmate,stalemate,validMoves = doMove(node)
    if node.isLeaf() or not validMoves:
      #eval move
      score = node.Score()
      if checkmate:
        score += Values['checkmate']
      if promo:
        score += Values['promo']
      if stalemate:
        score = 0
      if isMaximisingPlayer:
        score = -score
      #undo move
      board = copy.deepcopy(node.board)
      #return score
      return (score,node.move)
  node.CreateChildren()
  if isMaximisingPlayer:
    bestScore = (-10000000,)
    for child in node.children:
      scoreOfChild = minMax(child,False,alpha,beta)
      if scoreOfChild[0] > bestScore[0]:
        bestScore = (scoreOfChild[0],child.move)
      if bestScore[0] > alpha[0]:
        alpha = bestScore
      if beta[0] <= alpha[0]:
        break
  else:
    bestScore = (10000000,)
    for child in node.children:
      scoreOfChild = minMax(child,True,alpha,beta)
      if scoreOfChild[0] < bestScore[0]:
        bestScore = (scoreOfChild[0],child.move)
      if bestScore[0] < beta[0]:
        beta = bestScore
      if beta[0] <= alpha[0]:
        break
  #Once done all the leaf node under node
  #eval move
  score = node.Score()
  if checkmate:
    score += Values['checkmate']
  if promo:
    score += Values['promo']
  if stalemate:
    score = 0
  #add score to the best of the children
  if isMaximisingPlayer:
    score = -score
  score = bestScore[0]+score
  #undo move
  board = copy.deepcopy(node.board)
  return (score,bestScore[1])

def SaveToFile(txt):
  #used to debug
  with open("log.txt","a") as f:
    f.write(txt+"\n")

def moveScoring(origPlayer,depth,originalBoard=None):
  global board
  if originalBoard == None:
    originalBoard = copy.deepcopy(board)
  if depth % 2 != 0:
    player = Players[1-Players.index(origPlayer)]
  else:
    player = origPlayer
  colour = player.colour
  posNeg = 1
  if player == origPlayer:
    posNeg = -1
  moves = player.getPossibleMoves()
  ScoredMoves = []
  
  i = colours.index(colour)
  originalPieces = []
  for k in range(8):
    for j in range(8):
      piece = originalBoard.board[k][j]
      if piece != None and piece.colour != colour and piece.type != 'King':
        originalPieces.append(piece)

  for move in moves:
    value = 0
    checkmate = False
    validMoves = True #If there is any valid moves after this move
    #do move
    valid,piece,promotionPiece = performMove(move,colour)
    #value move
    if valid:
      if piece in board.Promotionable:
        if promotionPiece == None:
          promotionPiece = interface.aiPromotion()
        if promotionPiece != None:
          print(f"{piece} is promoting to {promotionPiece}")
          x,y = piece.GetPosition()
          for p in piecesCodes:
            if p[0] == promotionPiece:
              code = p[1]
          board.board[y][x].type = code
          board.board[y][x].reset()
          value += Values['promo']
          board.Promotionable.remove(piece)
          
      kings = board.GetKingsPosition()
      for king in kings:
        if inCheckmate(king):
          value += Values['checkmate']
          checkmate = True
          validMoves = False
          
      if not checkmate and Stalemate(Players[(i+1)%2]):
        value = 0
        validMoves = False
        print("Stalemate so no valid moves left")

        
    #compare changes
    newPieces = []
    for i in range(8):
      for j in range(8):
        piece = board.board[i][j]
        if piece != None and piece.colour != colour and piece.type != 'King':
          newPieces.append(piece)
    
    if len(originalPieces) > len(newPieces):
      for piece in originalPieces:
        if piece not in newPieces:
          value += Values[piece.code[1]]
    if len(originalPieces) < len(newPieces):
      print("Scoring: more new pieces")
    if depth != SEARCHDEPTH and validMoves:
      depthvalue = interface.fixedPieceEvaluation(moveScoring(origPlayer,depth+1))[1]
      value += posNeg*depthvalue
    ScoredMoves.append([move,value])
    board = copy.deepcopy(originalBoard)
  return ScoredMoves
  
def DrawClock():
  for c in range(2):
    player = Players[c]
    minutes = int(player.playTime // 60)
    seconds = int(player.playTime % 60)
    outputString = player.colour + " {0:02}:{1:02}".format(minutes,seconds)
    if player.colour == 'White':
      outputString = "|" + outputString
    text = font.render(outputString, True, WHITE)
    screen.blit(text, ((SIZE / 2)*c, SIZE))

def DrawCheck():
  for p in range(2):
    player = Players[p]
    if player.check:
      text = font.render("Check", True, WHITE)
      screen.blit(text, ((SIZE / 2)* p, SIZE + SQUARESIZE))

def DrawScreen(selected=None):
  pygame.draw.rect(screen, BACK_COLOUR, pygame.Rect(0,0,WINDOWWIDTH,WINDOWHEIGHT))
  board.Draw(selected)
  for i in range(len(promotionPieces)):
    screen.blit(pieceImgs[promotionPieces[i].code], (SIZE, SQUARESIZE * (i+2)))
  DrawClock()
  DrawCheck()
  pygame.display.update()

def ValidMove(currentX, currentY, newX, newY, doMove=True):
  piece = board.board[currentY][currentX]
  if piece == None:
    return False
  if board.board[newY][newX] != None and piece.colour == board.board[newY][newX].colour:
    return False
  if newX > 7 or newX < 0 or newY > 7 or newY < 0:
    return False
  if newX == currentX and newY == currentY:
    return True

  function = globals()["Valid"+piece.type+"Move"]
  if function(currentX, currentY, newX, newY, doMove):
    return True
  return False

def ValidPawnMove(currentX, currentY, newX, newY, doMove=True):
  piece = board.board[currentY][currentX]
  begin = False
  attack = False
  EnPassant = False

  if (currentY == 6 and piece.colour == 'White') or (currentY == 1 and piece.colour == 'Black'):
    begin = True
  if (piece.colour == 'White' and newY > currentY) or (piece.colour == 'Black' and newY < currentY):
    return False    

  if board.board[newY][newX] != None:
    attack = True

  if piece.colour == 'White':
    if board.board[newY + 1][newX] in board.EnPassantable and board.board[newY + 1][newX].code == 'bP' and board.board[newY][newX] == None:
      if doMove:
        board.board[newY + 1][newX].EnPassant = True
      EnPassant = board.board[newY + 1][newX]
    if newY == currentY - 1 and (newX == currentX + 1 or newX == currentX - 1) and (attack or EnPassant):
      #if attacking or enpassanting then can go diagonally
      return True

    if not begin:
      if newY >= currentY - 1 and newY <= currentY and newX == currentX and not attack:
        #Move forward 1
        return True
      return False

    if newY >= currentY - 2 and newY <= currentY and newX == currentX and not attack:
      #Move forward 1 or 2
      if board.board[currentY - 1][newX] != None:
        #Piece in way
        return False
      if newY == currentY - 2:
        #if forward 2
        if doMove:
          board.EnPassantable.append(piece)
      return True
    return False

  if piece.colour == 'Black':
    if board.board[newY - 1][newX] in board.EnPassantable and board.board[newY - 1][newX].code == 'wP' and board.board[newY][newX] == None:
      if doMove:
        board.board[newY - 1][newX].EnPassant = True
      EnPassant = board.board[newY - 1][newX]
    if newY == currentY + 1 and (newX == currentX + 1 or newX == currentX - 1) and (attack or EnPassant):
      #if attacking or enpassanting then can go diagonally
      return True

    if not begin:
      if newY <= currentY + 1 and newY >= currentY and newX == currentX and not attack:
        #Move forward 1
        return True
      return False

    if newY <= currentY + 2 and newY >= currentY and newX == currentX and not attack:
      #Move forward 1 or 2
      if board.board[currentY + 1][newX] != None:
        #Piece in way
        return False
      if newY == currentY + 2:
        #if forward 2
        if doMove:
          board.EnPassantable.append(piece)
      return True
    return False
  print("Valid Pawn Error")
  return None

def ValidRookMove(currentX, currentY, newX, newY, doMove=True):
  grid = board.board #Easier to refer to
  if newX == currentX:
    for y in range(1, abs(currentY - newY)):
      if currentY < newY:
        if grid[currentY + y][currentX] != None:
          return False
      else:
        if grid[currentY - y][currentX] != None:
          return False
    return True
  if newY == currentY:
    for x in range(1, abs(currentX - newX)):
      if currentX < newX:
        if grid[currentY][currentX + x] != None:
          return False
      else:
        if grid[currentY][currentX - x] != None:
          return False
    return True
  return False

def ValidBishopMove(currentX, currentY, newX, newY, doMove=True):
  grid = board.board
  if abs(newX - currentX) == abs(newY - currentY):
    for i in range(1, abs(currentY - newY)):
      if currentY < newY and currentX < newX:
        if grid[currentY + i][currentX + i] != None:
          return False
      elif currentY < newY and currentX > newX:
        if grid[currentY + i][currentX - i] != None:
          return False
      elif currentY > newY and currentX < newX:
        if grid[currentY - i][currentX + i] != None:
          return False
      else:
        if grid[currentY - i][currentX - i] != None:
          return False
    return True
  return False

def ValidQueenMove(currentX,currentY,newX,newY, doMove=True):
  if ValidRookMove(currentX,currentY,newX,newY, doMove) or ValidBishopMove(currentX,currentY,newX,newY, doMove):
    return True
  return False

def ValidKnightMove(currentX,currentY,newX,newY, doMove=True):
  if abs(newX - currentX) == 1 and abs(newY - currentY) == 2:
    return True
  if abs(newX - currentX) == 2 and abs(newY - currentY) == 1:
    return True
  return False

def ValidKingMove(currentX,currentY,newX,newY, doMove=True):
  if newX <= currentX + 1 and newX >= currentX - 1 and newY <= currentY + 1 and newY >= currentY - 1:
    return True
  if newY != currentY:
    return False
  kingside = True
  if newX == 2:
    kingside = False
  if (newX == 2 or newX == 6) and ValidCastle(currentX, currentY, kingside, doMove):
    return True
  return False

def ValidCastle(x,y,Kingside=True, doMove=True):
  king = board.board[y][x]
  if Kingside:
    rookX = 7
  else:
    rookX = 0
  rook = board.board[y][rookX]
  if king in board.MovedPieces or rook in board.MovedPieces:
    return False
  if inCheck(king):
    return False
  if rook == None or rook.type != 'Rook':
    return False
  if rook.colour != king.colour:
    return False
  if Kingside:
    for i in range(1,3):
      if board.board[y][x+i] != None:
        return False
      board.board[y][x+i] = king
      board.board[y][x] = None
      if inCheck(king):
        board.board[y][x] = king
        board.board[y][x+i] = None
        return False
      board.board[y][x] = king
      board.board[y][x+i] = None
      
  else:
    for i in range(1,3):
      if board.board[y][x-i] != None:
        return False
      board.board[y][x-i] = king
      board.board[y][x] = None
      if inCheck(king):
        board.board[y][x] = king
        board.board[y][x-i] = None
        return False
      board.board[y][x] = king
      board.board[y][x-i] = None
  if doMove:
    king.castleing = Kingside
  return True
      
def inCheck(king):
  if king == None or king.type != 'King':
    print("not king")
    return False
  x,y = king.GetPosition()
  #Check for pawns
  if king.colour == 'Black':
    #checks bottom left and right squares
    for i in range(-1,2,2):
      if x+i >= 0 and x+i < 8 and y+1 < 8:
        place = board.board[y+1][x+i]
        if place != None and place.code == 'wP':
          return True
  elif king.colour == 'White':
    for i in range(-1,2,2):
      #checks for top left and right squares
      if x+i >= 0 and x+i < 8 and y-1 >= 0:
        place = board.board[y-1][x+i]
        if place != None and place.code == 'bP':
          return True
  #Check for rooks and queens horizontally
  for i in range(8):
    place = board.board[y][i]
    if place != None and place.colour != king.colour and i != x:
      if place.type == 'Queen' or place.type == 'Rook':
        if ValidRookMove(i,y,x,y):
          return True
  #Check for rooks and queens vertically
  for i in range(8):
    place = board.board[i][x]
    if place != None and place.colour != king.colour and i != y:
      if place.type == 'Queen' or place.type == 'Rook':
        if ValidRookMove(x,i,x,y):
          return True
  #Check for bishop and queen in diagonals
  for i in range(1,8):
    # ++ direction
    if x+i < 8 and y+i < 8:
      place = board.board[y+i][x+i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x+i,y+i,x,y):
          return True
    # -- direction
    if x-i >= 0 and y-i >= 0:
      place = board.board[y-i][x-i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x-i,y-i,x,y):
          return True
    # +- direction
    if x-i >= 0 and y+i < 8:
      place = board.board[y+i][x-i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x-i,y+i,x,y):
          return True
    # -+ direction
    if x+i < 8 and y-i >= 0:
      place = board.board[y-i][x+i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x+i,y-i,x,y):
          return True
  #Checks for knights
  for i in range(-2,3,4):
    for j in range(-1,2,2):
      if y+i >= 0 and y+i < 8 and x+j >= 0 and x+j < 8:
        place = board.board[y+i][x+j]
        if place != None and place.type == 'Knight' and place.colour != king.colour:
          return True
      if y+j >= 0 and y+j < 8 and x+i >= 0 and x+i < 8:
        place = board.board[y+j][x+i]
        if place != None and place.type == 'Knight' and place.colour != king.colour:
          return True
  #Check spaces arround king
  for i in range(-1,2):
    for j in range(-1,2):
      if y+i >= 0 and y+i < 8 and x+j >= 0 and x+j < 8 and not (j == 0 and i == 0):
        place = board.board[y+i][x+j]
        if place != None and place.colour != king.colour and place.type == 'King':
          return True
  return False

def getCheckingPieces(king):
  x,y = king.GetPosition()
  checkingPieces = []
  opponentPieces = Players[1-colours.index(king.colour)].getPieces()
  for piece in opponentPieces:
    currentX,currentY = piece.GetPosition()
    if ValidMove(currentX,currentY,x,y,False):
      checkingPieces.append(piece)
  return checkingPieces
  

def inCheckmate(king):
  if not inCheck(king):
    for p in range(2):
      if Players[p].check:
        if Players[p].colour == king.colour:
          Players[p].check = False
    return False
  Players[colours.index(king.colour)].check = True
  colour = king.colour
  x,y = king.GetPosition()

  #checks if king can move
  for i in range(-1,2):
    for j in range(-1,2):
      if y + i >= 0 and y + i < 8 and x + j >= 0 and x + j < 8 and not (i==0 and j==0):
        if board.board[y+i][x+j] == None or (board.board[y+i][x+j] != None and board.board[y+i][x+j].colour != colour):
          if not stillInCheck(x,y,x+j,y+i,king):
            print(f"King can move to {x+j}, {y+i}")
            return False
            
  checkingPieces = getCheckingPieces(king)
  playerPieces = Players[colours.index(king.colour)].getPieces()
  #Called double checkmate
  if len(checkingPieces) > 1:
    return True
  #checks if a piece can take out the checking pieces
  checkingPiece = checkingPieces[0]
  checkingPieceX,checkingPieceY = checkingPiece.GetPosition()
  for piece in playerPieces:
    pieceX,pieceY = piece.GetPosition()
    if piece.type != 'King' and ValidMove(pieceX,pieceY,checkingPieceX,checkingPieceY,False):
      if not stillInCheck(pieceX,pieceY,checkingPieceX,checkingPieceY,king):
        print(f"{piece} can take out {checkingPiece}")
        return False

  #checks if piece can get in way of checking rook or queen
  if checkingPiece.type == 'Queen' or checkingPiece.type == 'Rook':
    if x != checkingPieceX and y == checkingPieceY:
      if checkingPieceX > x:
        #p is direction
        p = -1
      else:
        p = 1
      for i in range(0, (x-checkingPieceX),p):
        for piece in playerPieces:
          pieceX,pieceY = piece.GetPosition()
          if piece.type != 'King' and ValidMove(pieceX,pieceY,checkingPieceX+i,checkingPieceY,False):
            if not stillInCheck(pieceX,pieceY,checkingPieceX+i,checkingPieceY,king):
              print(f"{piece} can move to {checkingPieceX+i},{checkingPieceY}")
              return False
    elif x == checkingPieceX and y != checkingPieceY:
      if checkingPieceY < y:
        p = 1
      else:
        p = -1
      for i in range(0, (y-checkingPieceY),p):
        for piece in playerPieces:
          pieceX,pieceY = piece.GetPosition()
          if piece.type != 'King' and ValidMove(pieceX,pieceY,checkingPieceX,checkingPieceY+i,False):
            if not stillInCheck(pieceX,pieceY,checkingPieceX,checkingPieceY+i,king):
              print(f"{piece} can move to {checkingPieceX},{checkingPieceY+i}")
              return False
  #checks if piece can get in way of checking queen or bishop
  if checkingPiece.type == 'Queen' or checkingPiece.type == 'Bishop':
    if (x > checkingPieceX and y > checkingPieceY) or (x < checkingPieceX and y < checkingPieceY):
      if checkingPieceY < y:
        p = 1
      else:
        p = -1
      for i in range(0,(y-checkingPieceY),p):
        for piece in playerPieces:
          pieceX,pieceY = piece.GetPosition()
          if piece.type != 'King' and ValidMove(pieceX,pieceY,checkingPieceX+i,checkingPieceY+i,False):
            if not stillInCheck(pieceX,pieceY,checkingPieceX+i,checkingPieceY+i,king):
              print(f"{piece} can move to {checkingPieceX+i},{checkingPieceY+i}")
              return False
    elif  (x > checkingPieceX and y < checkingPieceY) or (x < checkingPieceX and y > checkingPieceY):
      if checkingPieceY < y:
        p = 1
      else:
        p = -1
      for i in range(0,(y-checkingPieceY),p):
        for piece in playerPieces:
          pieceX,pieceY = piece.GetPosition()
          if piece.type != 'King' and ValidMove(pieceX,pieceY,checkingPieceX-i,checkingPieceY+i,False):
            if not stillInCheck(pieceX,pieceY,checkingPieceX-i,checkingPieceY+i,king):
              print(f"{piece} can move to {checkingPieceX-i},{checkingPieceY+i}")
              return False
  print("Chackmate")
  return True

def stillInCheck(currentX,currentY,newX,newY,king):
  newPlace = board.board[newY][newX]
  oldPlace = board.board[currentY][currentX]
  board.board[currentY][currentX] = None
  board.board[newY][newX] = oldPlace
  if inCheck(king):
    board.board[currentY][currentX] = oldPlace
    board.board[newY][newX] = newPlace
    return True
  board.board[currentY][currentX] = oldPlace
  board.board[newY][newX] = newPlace
  return False

def Stalemate(player):
  pieces = player.getPieces()
  if len(pieces) == 1:
    if pieces[0].type == 'King':
      opieces = Players[1-Players.index(player)].getPieces()
      if len(opieces) == 1:
        if opieces[0].type == 'King':
          return True
  if player.getPossibleMoves() != []:
    return False
  print("\nStalemate\n\n")
  return True

def DoMove(currentX,currentY,newX,newY,piece):
  if piece not in board.MovedPieces:
    board.MovedPieces.append(piece)
  for piece in board.EnPassantable:
    if piece.EnPassant:
      if piece.colour == 'White':
        y = 4
      else:
        y = 3
      removed = False
      for x in range(8):
        if board.board[y][x] == piece:
          board.board[y][x] = None
          removed = True
      if not removed:
        print("En Passanted Piece not removed")
  if piece.type == 'Pawn':
    if piece.colour == 'White':
      if newY == 0:
        board.Promotionable.append(piece)
    else:
      if newY == 7:
        board.Promotionable.append(piece)

def LegalMove(currentX,currentY,newX,newY,colour,doMove=True):
  kings = board.GetKingsPosition()
  piece = board.board[currentY][currentX]
  if kings[0].colour == colour:
    king = kings[0]
  elif kings[1].colour == colour:
    king = kings[1]
  

  if inCheck(king):
    if ValidMove(currentX,currentY,newX,newY,doMove):
      originalNewPlace = board.board[newY][newX]
      originalCurrentPlace = board.board[currentY][currentX]
      board.board[currentY][currentX] = None
      board.board[newY][newX] = originalCurrentPlace

      
      if piece == king:
        if inCheck(king):
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
          return False
        else:
          if doMove:
            if piece not in board.MovedPieces:
              board.MovedPieces.append(piece)
            board.board[newY][newX] = originalNewPlace
            board.board[currentY][currentX] = originalCurrentPlace
            formatMove(currentX,currentY,newX,newY)
            board.board[currentY][currentX] = None
            board.board[newY][newX] = originalCurrentPlace
          else:
            board.board[newY][newX] = originalNewPlace
            board.board[currentY][currentX] = originalCurrentPlace
          return True
      else:
        if inCheck(king):
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
          return False
        if doMove:
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
          formatMove(currentX,currentY,newX,newY)
          board.board[currentY][currentX] = None
          board.board[newY][newX] = originalCurrentPlace
          DoMove(currentX,currentY,newX,newY,piece)
        else:
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
        return True
  else:
    if ValidMove(currentX,currentY,newX,newY,doMove):
      originalNewPlace = board.board[newY][newX]
      originalCurrentPlace = board.board[currentY][currentX]
      board.board[currentY][currentX] = None
      board.board[newY][newX] = originalCurrentPlace
      if piece == king:
        if inCheck(king):
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
          return False
        else:
          if doMove:
            if piece not in board.MovedPieces:
              board.MovedPieces.append(piece)
            board.board[newY][newX] = originalNewPlace
            board.board[currentY][currentX] = originalCurrentPlace
            formatMove(currentX,currentY,newX,newY,castle=piece.castleing)
            board.board[currentY][currentX] = None
            board.board[newY][newX] = originalCurrentPlace
            if piece.castleing != None:
              if piece.castleing:#kingside
                newRookX = 5
                currentRookX = 7
              else:
                newRookX = 3
                currentRookX = 0
              board.board[newY][newRookX] = board.board[newY][currentRookX]
              board.board[newY][currentRookX] = None
              piece.castleing = None
          else:
            board.board[newY][newX] = originalNewPlace
            board.board[currentY][currentX] = originalCurrentPlace
          return True
      else:#not in check, valid move, not king
        if inCheck(king):
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
          return False
        if doMove:
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
          formatMove(currentX,currentY,newX,newY)
          board.board[currentY][currentX] = None
          board.board[newY][newX] = originalCurrentPlace
          DoMove(currentX,currentY,newX,newY,piece)
        else:
          board.board[newY][newX] = originalNewPlace
          board.board[currentY][currentX] = originalCurrentPlace
        return True
    return False

def formatMove(currentX,currentY,newX,newY,castle=None,Save=True):
  move = ''
  piece = board.board[currentY][currentX]
  if Save and piece.colour == 'White':
    board.SavedMoves.append(' 1. ')
  if piece.type != 'Pawn':
    move += piece.code[1]
  if castle != None:
    if castle:
      move = 'O-O'
    else:
      move = 'O-O-O'
    if Save:
      move += ' '
  else:
    #choices
    choices = [board.board[currentY][currentX]]
    for otherPiece in Players[colours.index(choices[0].colour)].getPieces():
      if otherPiece.type == choices[0].type and otherPiece not in choices:
        x,y = otherPiece.GetPosition()
        if LegalMove(x,y,newX,newY,choices[0].colour,doMove=False):
          choices.append(otherPiece)


    if piece.type == 'Pawn' and len(choices) == 1 and currentX != newX:
      move += chr(currentX+97)
    elif len(choices) == 2:
      x,y = choices[1].GetPosition()
      if currentX == x:
        move += str(8-currentY)

      else:
        move += chr(currentX+97)
    move += chr(newX+97)
    move += str(8-newY)
    if Save:
      move += ' '
  
  
  if not Save:
    return move
  board.SavedMoves.append(move)
  
def SaveGame():
  with open('SaveMoves.txt', 'w') as f:
    board.SavedMoves[0] = '1. '
    for move in board.SavedMoves:
      f.write(move)

def GetMove(colour,move=None):
  if move == None:
    if Moves == []:
      print("Finished moves")
    pos = Moves[0]
    del Moves[0]
  else:
    pos = move
  promotionPiece = None
  if '=' in pos:
    if pos[-2] == '=':
      promotionPiece = pos[-1]
      pos = pos[:-2]
    else:
      promotionPiece = pos[-1]
      pos = pos[:-3]
  if pos[-1] == '+' or pos[-1] == '#':
    pos = pos[:-1]
  if 'x' in pos:
    pos = pos.replace('x','')
  if move == None:
    print("Move:",pos)
  castle = False
  if pos == 'O-O':
    piece = 'King'
    if colour == 'White':
      newY = 7
    elif colour == 'Black':
      newY = 0
    newX = 6
    castle = True
  elif pos =='O-O-O':
    piece = 'King'
    if colour == 'White':
      newY = 7
    elif colour == 'Black':
      newY = 0
    newX = 2
    castle = True
  else:
    piece = ''
    newX = ord(pos[-2])-97
    newY = 8-int(pos[-1])
    for code in piecesCodes:
      if pos[0] in code:
        piece = code[1]
    if piece == '':
      piece = 'Pawn'
    choice = None #used to store which piece moves if multiple can go to the location
    if (len(pos) > 2 and piece != 'Pawn' or len(pos) == 3 and piece == 'Pawn') and (ord(pos[-3]) > 48 and ord(pos[-3]) <= 56 or ord(pos[-3]) >= 97 and ord(pos[-3]) <= 104):
      choice = pos[-3]
      if choice.isnumeric():
        choice = int(choice)
    currentX,currentY = GetStart(colour,piece,newX,newY,choice)
  if castle:
    currentY = newY
    currentX = 4
  return currentX,currentY,newX,newY,promotionPiece

def GetStart(colour,pieceType,newX,newY,choice):
  startingPos = None
  player = Players[0]
  if player.colour != colour:
    player = Players[1]
  for piece in player.getPieces():
    if piece.type == pieceType:
      x,y = piece.GetPosition()
      if ValidMove(x,y,newX,newY,False):
        if startingPos == None:
          startingPos = (x,y)
        else:
          if choice != None:
            posX,posY = startingPos
            if isinstance(choice,str):
              if posX == ord(choice)-97:
                startingPos = posX,posY
              elif x == ord(choice)-97:
                startingPos = x,y
              else:
                print("invalid choice str")
            elif isinstance(choice,int):
              if posY == 8-int(choice):
                startingPos = posX,posY
              elif y == 8-int(choice):
                startingPos = x,y
              else:
                print("invalid choice int")
          else:
            print(startingPos, "can go or", x,y, "can go. no choice")
  if startingPos == None:
    print("startingPos None")
    startingPos = 0,0
  return startingPos

def GetMoves(filename='Moves.txt'):
  moves = []
  with open(filename,'r') as f:
    for line in f:
      unformatted = line.replace('\n','')
  formatted = unformatted.split('  ')
  if formatted[-1] == '':
    del formatted[-1]
    formatted[-1] += '  '
  for round in formatted:
    if round != '':
      temp = round.split(' ')
      moves.append(temp[1])
      moves.append(temp[2])
  while moves[-1] == '':
    del moves[-1]
  print(moves)
  return moves
  

with open('log.txt','w') as file:
  file.write('')

piecesCodes = [["P", "Pawn"], ["R", "Rook"], ["B", "Bishop"], ["Q", "Queen"], ["N", "Knight"], ["K", "King"]]
colours = ["Black", "White"]
Values = {'P':10,'N':30,'B':35,'R':50,'Q':90,'K':900,'promo':7000,'checkmate':1000000}

pieceImgs = {}
for colour in colours:
  for piece in piecesCodes:
    code = colour[0].lower()+piece[0]
    img = pygame.image.load(code + ".png").convert_alpha(screen)
    pieceImgs[code] = pygame.transform.scale(img, (SQUARESIZE,SQUARESIZE))
promotionPieces = []
for p in range(1,5):
  promotionPieces.append(Piece(piecesCodes[p][1],"White",'p'))
Players = []
for i in range(2):
  Players.append(Player(colours[i]))
if whiteAI:
  Players[1].ai = True
if blackAI:
  Players[0].ai = True
Players[1].aitype = AIType
Players[0].aitype = AIType
global board
board = Board()

if playTxtMoves:
  Moves = GetMoves()
else:
  Moves = []

lasttime = time.time()
contime = lasttime
play = True
i = 1
selected = None
PromotionWait = False

DrawScreen(selected)
print(Players[i].colour+"'s turn")
print(board)
while play:
  if Moves == [] and Players[i].ai:
    #AI move selection
    DrawScreen(None)
    Moves.append(Players[i].aiMove())
  if Moves == [] and not Players[i].ai:
    DrawScreen(selected)
    Players[i].playTime += time.time() - contime
    contime = time.time()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        play = False
        SaveGame()
        print("Program Closed")
        winner = 'No-one'
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and selected == None and not PromotionWait:
          #if clicked and not piece selected and not promoting a piece
          currentPos = event.pos
          currentX, currentY = currentPos
          if currentX < SIZE and currentX > 0 and currentY < SIZE and currentY > 0:
            #if in board
            currentX = int(currentX//SQUARESIZE)
            currentY = int(currentY//SQUARESIZE)
            if board.board[currentY][currentX] != None and board.board[currentY][currentX].colour == colours[i]:
              #if piece is player's colour
              selected = board.board[currentY][currentX]
              print(f"You are moving {board.board[currentY][currentX]}")
              
        elif event.button == 1 and selected != None:
          #if clicked and piece selected
          newPos = event.pos
          newX,newY = newPos
          piece = board.board[currentY][currentX]
          if piece in board.Promotionable and newX < WINDOWWIDTH and newX > SIZE and newY < SIZE - 2 * SQUARESIZE and newY > 2 * SQUARESIZE:
            #if promoting piece and valid area
            type = promotionPieces[int(newY // SQUARESIZE) - 2].type
            board.board[currentY][currentX].type = type
            board.board[currentY][currentX].reset()
            selected = board.board[currentY][currentX]
            board.Promotionable.remove(piece)
            board.SavedMoves[-1] = board.SavedMoves[-1][:-1] + '=' + type + ' '
            kings = board.GetKingsPosition()
            for king in kings:
              if inCheckmate(king):
                winner = colours[1-colours.index(king.colour)]
                play = False
            if play and Stalemate(Players[(i+1)%2]):
              play = False
              winner = 'Stalemate'
          elif newX < SIZE and newX > 0 and newY < SIZE and newY > 0:
            #if on board
            newX = int(newX // SQUARESIZE)
            newY = int(newY // SQUARESIZE)
            if currentY == newY and currentX == newX:
              selected = None
            elif LegalMove(currentX,currentY,newX,newY,colours[i]):
              for passantPiece in board.EnPassantable:
                if passantPiece.colour == colours[(i+1)%2]:
                  #removes all passantable pieces from other colour
                  board.EnPassantable.remove(passantPiece)
              if piece in board.Promotionable:
                PromotionWait = piece
              else:
                PromotionWait = False

              kings = board.GetKingsPosition()
              for king in kings:
                if inCheckmate(king):
                  winner = colours[1-colours.index(king.colour)]
                  play = False
              if play and Stalemate(Players[(i+1)%2]):
                play = False
                winner = 'Stalemate'
                  
              if not PromotionWait:
                i = (i + 1) % 2
                print(f"You moved {piece} to ({currentX+1},{currentY+1})")
                print()
                print(Players[i].colour+"'s turn")
                print(board)
              else:
                print(f"You moved {piece} to ({currentX+1},{currentY+1})")
              selected = None
              pygame.mouse.set_cursor(Players[i].cursor)
        elif event.button == 3 and selected != None:
          selected = None
          print("Deselected")
        elif event.button == 1 and PromotionWait:
          pos = event.pos
          x,y = pos
          if x < WINDOWWIDTH and x > SIZE and y < SIZE - 2 * SQUARESIZE and y > 2 * SQUARESIZE:
            type = promotionPieces[int(newY // SQUARESIZE) - 2].type
            board.board[newY][newX].type = type
            board.board[newY][newX].reset()
            board.Promotionable.remove(piece)
            board.SavedMoves[-1] = board.SavedMoves[-1][:-1] + '=' + board.board[newY][newX].code[1] + ' '
            kings = board.GetKingsPosition()
            for king in kings:
              if inCheckmate(king):
                winner = colours[1-colours.index(king.colour)]
                play = False
            if play and Stalemate(Players[(i+1)%2]):
              play = False
              winner = 'Stalemate'
            PromotionWait = False
            i = (i+1) % 2
            print()
            print(Players[i].colour+"'s turn")
            print(board)

  else:
    player = Players[i]
    DrawScreen(None)
    Players[i].playTime += time.time() - contime
    contime = time.time()
    currentX,currentY,newX,newY,promotionPiece = GetMove(Players[i].colour)
    piece = board.board[currentY][currentX]
    if LegalMove(currentX,currentY,newX,newY,colours[i]):
      for passantPiece in board.EnPassantable:
        if passantPiece.colour == colours[(i+1)%2]:
          #removes all passantable pieces from other colour
          board.EnPassantable.remove(passantPiece)
      if piece in board.Promotionable:
        PromotionWait = piece
      else:
        PromotionWait = False

      kings = board.GetKingsPosition()
      for king in kings:
        if inCheckmate(king):
          winner = colours[1-colours.index(king.colour)]
          play = False
      
      if play and Stalemate(Players[(i+1)%2]):
        play = False
        winner = 'Stalemate'
      i = (i + 1) % 2
      print(f"You moved {piece} to ({currentX+1},{currentY+1})")
      print()
      print(Players[i].colour+"'s turn")
      print(board)
    else:
      print("illegal move")
    if piece in board.Promotionable:
      if promotionPiece == None and player.ai:
        promotionPiece = interface.aiPromotion()
      if promotionPiece != None:
        for p in piecesCodes:
          if p[0] == promotionPiece:
            code = p[1]
        board.board[newY][newX].type = code
        board.board[newY][newX].reset()
        PromotionWait = False
        board.SavedMoves[-1] = board.SavedMoves[-1][:-1] + '=' + promotionPiece + ' '
        board.Promotionable.remove(piece)
        for king in kings:
          if inCheckmate(king):
            winner = colours[1-colours.index(king.colour)]
            play = False
        if play and Stalemate(Players[(i+1)%2]):
          play = False
          winner = 'Stalemate'
for player in Players:
  player.check = False
DrawScreen(None)
text = font.render(winner + " Wins!", True, WHITE)
screen.blit(text, (0, SIZE + SQUARESIZE))
pygame.display.update()
print("End of Game")
if len(Moves) > 0:
  print("moves left")
SaveGame()
pygame.time.wait(20000)
pygame.quit()
    