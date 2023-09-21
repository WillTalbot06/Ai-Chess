import pygame
from config import *
from Function import *
#Used to set up classes


pygame.init()
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

screen = pygame.display.set_mode(WINDOWSIZE)
font = pygame.font.Font(None, int(SQUARESIZE))

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
    if isinstance(piece,Piece):
      return self.id == piece.id
    return False

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
    for i in range(8):
      for j in range(8):
        if self.board[i][j] != None and self.board[i][j].type == 'King':
          loc.append(self.board[i][j])
        if len(loc) == 2:
          return loc
    print("only one king")
    print(loc[0].id)
    print(board)