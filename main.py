import pygame, sys, time
from pygame.locals import QUIT
import AIinterface as interface

#Test Stalemate
#Start on AI properly
#link to GitHub and save as a checkpoint

#iphone use 328 size
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

playTxtMoves = True

class Piece:
  def __init__(self,type,colour):
    self.type = type
    self.colour = colour
    #Gets code in format colourType. Useful for references
    for piece in piecesCodes:
      if piece[1] == self.type:
        self.code = self.colour[0].lower() + piece[0]
    #imports image from files
    img = pygame.image.load(self.code + ".png").convert_alpha(screen)
    self.img = pygame.transform.scale(img, (SQUARESIZE,SQUARESIZE))
    if self.type == 'Pawn':
      self.EnPassant = False #if piece has been taken by enpassant so it can be deleted later
    if self.type == 'King':
      self.castleing = None #stores which way to castle. If not then none
   
  def __str__(self):
    return f"{self.code} {self.GetPosition()}"

  def GetPosition(self):
    for i in range(8):
      for j in range(8):
        if board.board[i][j] == self:
          return (j,i) #in form x,y

class Board:
  def __init__(self):
    #Creates board
    board = []
    for i in range(8):
      board.append([None]*8)
  
    #Creates and places pieces
    for colour in range(2):
      row = colour
      if colour == 1:
        row = 7
  
      board[row][0] = Piece(piecesCodes[1][1],colours[colour])
      board[row][7] = Piece(piecesCodes[1][1],colours[colour])
      board[row][1] = Piece(piecesCodes[4][1],colours[colour])
      board[row][6] = Piece(piecesCodes[4][1],colours[colour])
      board[row][2] = Piece(piecesCodes[2][1],colours[colour])
      board[row][5] = Piece(piecesCodes[2][1],colours[colour])
      board[row][3] = Piece(piecesCodes[3][1],colours[colour])
      board[row][4] = Piece(piecesCodes[5][1],colours[colour])
  
      #Places pawns
      for i in range(8):
        if colour == 0:
          board[1][i] = Piece(piecesCodes[0][1],colours[colour])
        else:
          board[6][i] = Piece(piecesCodes[0][1],colours[colour])

    self.board = board
    self.Promotionable = []
    self.EnPassantable = []
    self.MovedPieces = []




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
              screen.blit(piece.img, (SQUARESIZE*j, SQUARESIZE*i))
          else:
            screen.blit(piece.img, (SQUARESIZE*j, SQUARESIZE*i))

    #draws selected piece
    if selected != None:
      x,y = pygame.mouse.get_pos()
      x -= SQUARESIZE / 2
      y -= SQUARESIZE / 2
      pos = x,y
      screen.blit(self.board[currentY][currentX].img, pos)

  def GetKingsPosition(self):
    loc = []
    for i in range(8):
      for j in range(8):
        if self.board[i][j] != None and self.board[i][j].type == 'King':
          loc.append(self.board[i][j])
        if len(loc) == 2:
          return loc
    print("only one king")
    print(loc)

class Player:
  def __init__(self,colour,cursor=pygame.cursors.diamond,ai=False):
    self.colour = colour
    self.ai = ai
    self.playTime = 0
    self.cursor = cursor
    self.check = False

  def __str__(self):
    return self.colour

  def getPieces(self):
    pieces = []
    for i in range(8):
      for j in range(8):
        piece = board.board[i][j]
        if piece != None and piece.colour == self.colour:
          pieces.append(piece)
    return pieces

  def getPossibleMoves(self):
    pieces = self.getPieces()
    possibleMoves = []
    for piece in pieces:
      x, y = piece.GetPosition()
      for i in range(8):
        for j in range(8):
          if LegalMove(x,y,i,j,self.colour,False):
            possibleMoves.append(formatMove(x,y,i,j,Save=False))
    print(possibleMoves)
    return possibleMoves
    

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
    screen.blit(promotionPieces[i].img, (SIZE, SQUARESIZE * (i+2)))
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

  #temp so shows errors
  function = globals()["Valid"+piece.type+"Move"]
  if function(currentX, currentY, newX, newY, doMove):
    return True
  return False
  
  try:
    function = globals()["Valid"+piece.type+"Move"]
    if function(currentX, currentY, newX, newY, doMove):
      return True
    return False
  except Exception as e: 
    print(e)

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
      board.board[newY + 1][newX].EnPassant = True
      EnPassant = board.board[newY + 1][newX]
    if newY == currentY - 1 and (newX == currentX + 1 or newX == currentX - 1) and (attack or EnPassant):
      #if attacking or enpassanting then can go diagonally
      if EnPassant and not doMove:
        EnPassant.EnPassant = False #so pawn wont get taken
      return True

    if not begin:
      if newY >= currentY - 1 and newY <= currentY and newX == currentX and not attack:
        #Move forward 1
        if EnPassant and not doMove:
          EnPassant.EnPassant = False
        return True
      if EnPassant and not doMove:
        EnPassant.EnPassant = False
      return False

    if newY >= currentY - 2 and newY <= currentY and newX == currentX and not attack:
      #Move forward 1 or 2
      if board.board[currentY - 1][newX] != None:
        #Piece in way
        if EnPassant and not doMove:
          EnPassant.EnPassant = False
        return False
      if newY == currentY - 2:
        #if forward 2
        board.EnPassantable.append(piece)
      if EnPassant and not doMove:
        EnPassant.EnPassant = False
      return True
    if EnPassant and not doMove:
      EnPassant.EnPassant = False
    return False

  if piece.colour == 'Black':
    if board.board[newY - 1][newX] in board.EnPassantable and board.board[newY - 1][newX].code == 'wP' and board.board[newY][newX] == None:
      board.board[newY - 1][newX].EnPassant = True
      EnPassant = board.board[newY - 1][newX]
    if newY == currentY + 1 and (newX == currentX + 1 or newX == currentX - 1) and (attack or EnPassant):
      #if attacking or enpassanting then can go diagonally
      if EnPassant and not doMove:
        EnPassant.EnPassant = False
      return True

    if not begin:
      if newY <= currentY + 1 and newY >= currentY and newX == currentX and not attack:
        #Move forward 1
        if EnPassant and not doMove:
          EnPassant.EnPassant = False
        return True
      if EnPassant and not doMove:
        EnPassant.EnPassant = False
      return False

    if newY <= currentY + 2 and newY >= currentY and newX == currentX and not attack:
      #Move forward 1 or 2
      if board.board[currentY + 1][newX] != None:
        #Piece in way
        if EnPassant and not doMove:
          EnPassant.EnPassant = False
        return False
      if newY == currentY + 2:
        #if forward 2
        board.EnPassantable.append(piece)
      if EnPassant and not doMove:
        EnPassant.EnPassant = False
      return True
    if EnPassant and not doMove:
      EnPassant.EnPassant = False
    return False
  print("Valid Pawn Error")
  if EnPassant and not doMove:
    EnPassant.EnPassant = False
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
  #Check spaces arround king
  for i in range(-1,2):
    for j in range(-1,2):
      if y+i >= 0 and y+i < 8 and x+j >= 0 and x+j < 8 and not (j == 0 and i == 0):
        place = board.board[y+i][x+j]
        if place != None and place.colour != king.colour and place.type == 'King':
          return True
  #Check for pawns
  if king.colour == 'Black':
    for i in range(-1,2,2):
      if x+i >= 0 and x+i < 8 and y+1 < 8:
        place = board.board[y+1][x+i]
        if place != None and place.code == 'wP':
          return True
  elif king.colour == 'White':
    for i in range(-1,2,2):
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
  #Check for bishop and queen in ++ direction
  for i in range(1,8):
    if x+i < 8 and y+i < 8:
      place = board.board[y+i][x+i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x+i,y+i,x,y):
          return True
  # -- direction
  for i in range(1,8):
    if x-i >= 0 and y-i >= 0:
      place = board.board[y-i][x-i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x-i,y-i,x,y):
          return True
  # +- direction
  for i in range(1,8):
    if x-i >= 0 and y+i < 8:
      place = board.board[y+i][x-i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x-i,y+i,x,y):
          return True
  # -+ direction
  for i in range(1,8):
    if x+i < 8 and y-i >= 0:
      place = board.board[y-i][x+i]
      if place != None and place.colour != king.colour and (place.type == 'Queen' or place.type == 'Bishop'):
        if ValidBishopMove(x+i,y-i,x,y):
          return True
  #Checks for kings
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
  for piece in pieces:
    x, y = piece.GetPosition()
    for i in range(8):
      for j in range(8):
        if LegalMove(x,y,i,j,player.colour,False):
          return False
  print("\nStalemate\n\n")
  return True

def DoMove(currentX,currentY,newX,newY,piece):
  if piece not in board.MovedPieces:
    board.MovedPieces.append(piece)
  for i in range(8):
    for j in range(8):
      pos = board.board[i][j]
      if pos != None and pos.type == 'Pawn' and pos.EnPassant:
        board.board[i][j] = None
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
    SavedMoves.append(' 1. ')
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
  print(f"Move: {move}")
  SavedMoves.append(move)
  #print(SavedMoves)
  
def SaveGame():
  with open('SaveMoves.txt', 'w') as f:
    SavedMoves[0] = '1. '
    for move in SavedMoves:
      f.write(move)

def GetMove(colour):
  if Moves == []:
    print("Finished moves")
  pos = Moves[0]
  del Moves[0]
  #time.sleep(0.1)
  #input()
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
            if type(choice) == str:
              if posX == ord(choice)-97:
                startingPos = posX,posY
              elif x == ord(choice)-97:
                startingPos = x,y
              else:
                print("invalid choice str")
            elif type(choice) == int:
              if posY == 8-int(choice):
                startingPos = posX,posY
              elif y == 8-int(choice):
                startingPos = x,y
              else:
                print("invalid choice int")
            else:
              print(startingPos, "can go or", x,y, "can go. no choice")
  if startingPos == None:
    print("Pos None")
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
  


piecesCodes = [["P", "Pawn"], ["R", "Rook"], ["B", "Bishop"], ["Q", "Queen"], ["N", "Knight"], ["K", "King"]]
colours = ["Black", "White"]
promotionPieces = []
for p in range(1,5):
  promotionPieces.append(Piece(piecesCodes[p][1],"White"))
Players = []
for i in range(2):
  Players.append(Player(colours[i]))
Players[1].ai = True
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
SavedMoves = []

print(board)
DrawScreen(selected)
print(Players[i].colour+"'s turn")
print(board)
while play:
  if Moves == [] and Players[i].ai:
    #AI move selection
    initBoard = board
    Moves.append(interface.randomMove(Players[i].getPossibleMoves()))
    board = initBoard
  if Moves == []:
    DrawScreen(selected)
    Players[i].playTime += time.time() - contime
    contime = time.time()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        play = False
        SaveGame()
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
            newPiece = promotionPieces[int(newY // SQUARESIZE) - 2]
            board.board[currentY][currentX] = board.board[newY][newX] = Piece(newPiece.type,colours[i])
            selected = newPiece
            board.Promotionable.remove(piece)
            SavedMoves[-1] = SavedMoves[-1][:-1] + '=' + newPiece.code[1] + ' '
            kings = board.GetKingsPosition()
            for king in kings:
              if inCheckmate(king):
                winner = colours[1-colours.index(king.colour)]
                play = False
            if Stalemate(Players[(i+1)%2]):
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
              if Stalemate(Players[(i+1)%2]):
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
            newPiece = promotionPieces[int(y // SQUARESIZE) - 2]
            board.board[newY][newX] = Piece(newPiece.type,colours[i])
            board.Promotionable.remove(piece)
            SavedMoves[-1] = SavedMoves[-1][:-1] + '=' + newPiece.code[1] + ' '
            kings = board.GetKingsPosition()
            for king in kings:
              if inCheckmate(king):
                winner = colours[1-colours.index(king.colour)]
                play = False
            if Stalemate(Players[(i+1)%2]):
              play = False
              winner = 'Stalemate'
            PromotionWait = False
            i = (i+1) % 2
            print()
            print(Players[i].colour+"'s turn")
            print(board)

  elif len(Moves) > 0:
    player = Players[i]
    DrawScreen(None)
    Players[i].playTime += time.time() - contime
    contime = time.time()
    grid = board
    currentX,currentY,newX,newY,promotionPiece = GetMove(Players[i].colour)
    board = grid
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
      if Stalemate(Players[(i+1)%2]):
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
        board.board[newY][newX] = Piece(code,player.colour)
        PromotionWait = False
        SavedMoves[-1] = SavedMoves[-1][:-1] + '=' + promotionPiece + ' '
        board.Promotionable.remove(piece)
        for king in kings:
          if inCheckmate(king):
            winner = colours[1-colours.index(king.colour)]
            play = False
        if Stalemate(Players[(i+1)%2]):
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
time.sleep(1000)
time.sleep(20)
pygame.quit()
    