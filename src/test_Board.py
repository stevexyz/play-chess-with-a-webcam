#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Board import Board
from Board import RejectedMove

# check the sequence of  moves end positon against the expected FEN notation string
def checkMovesEndPosition(moves,expectedFen):
    board = Board()
    for move in moves:
       try:
          san=board.performMove(move)
          print (san)
       except RejectedMove as e:
          print(e)
          pass
    checkEndPosition(board,expectedFen)

# check the expected end position
def checkEndPosition(board,expectedFen):
    print("---Final positions---")
    fen=board.fen()
    print (fen)
    unicode=board.unicode()
    print (unicode)
    pgn=board.pgn()
    print (pgn)
    assert expectedFen==fen

# test the board state using "easy" notation
def test_BoardEasy():
    moves=[
        ['D2','D4'],              #d4
        ['G8','F6'],              #Nf6
        ['C2','C4'],              #c4
        ['E7','E6'],              #e6
        ['C4','C5'],              #c5
        ['F8','D6'],              #Bd6
        ['D1','A4'],              #Qa4
        ['B7','B5'],              #b5
        ['B5','B6'],              #cxb6, En Passant
        ['E8','G8'],              #0-0
        ['B6','C7']               #bxc7, Hidden eat
    ]
    expectedFen="rnbq1rk1/p1Pp1ppp/3bpn2/2P5/Q2P4/8/PP2PPPP/RNB1KBNR"
    checkMovesEndPosition(moves,expectedFen)

# test using pgn notation
def test_BoardPgn():
    pgn="1. d4 Nf6 2. c4 e6 3. c5 Bd6 4. Qa4 b5 5. cxb6 O-O 6. bxc7"
    board=Board()
    board.setPgn(pgn)
    expectedFen="rnbq1rk1/p1Pp1ppp/3bpn2/8/Q2P4/8/PP2PPPP/RNB1KBNR"
    checkEndPosition(board,expectedFen)

test_BoardEasy()
test_BoardPgn()
