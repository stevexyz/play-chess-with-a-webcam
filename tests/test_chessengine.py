'''
Created on 2019-12-26

@author: wf
'''
from pcwawc.chessengine import Engine
import pytest
import chess
import chess.pgn
from datetime import datetime
import os

debug=True

def fix_path():
    """ fixes PATH issues e.g. on MacOS macports environment - adopt to your needs as you see fit"""
    home=os.environ["HOME"]
    homebin=home+"/bin"
    # is a home/bin and/or /usr/games directory available?
    # priority is last in list as higher priority
    for path in [ "/usr/games", homebin ]:
        # if the path is available
        if os.path.isdir(path):
            if debug:
                print ("found %s - prepending it to PATH" % path)    
            os.environ["PATH"]="%s:%s" % (path,os.environ["PATH"])
        
def findEngines():
    fix_path()
    Engine.debug=debug
    engineConfigs=Engine.findEngines()
    return engineConfigs
        
# http://julien.marcel.free.fr/macchess/Chess_on_Mac/Engines.html
def test_engines():
    engineConfigs=findEngines()
    for key,engineConfig in engineConfigs.items():
        chessEngine=Engine(engineConfig)
        print (chessEngine)
        try:
            engine=chessEngine.open()
        except Exception as e:
            print ("opening %s failed with " % (engine.name,str(e)))
            #pytest.fail(str(e))
        
        
def test_play():
    engineConfigs=findEngines() 
    engineCmds=["gnuchess","stockfish"]
    for engineCmd in engineCmds:
        if engineCmd not in engineConfigs:
            raise Exception("%s engine not found" % engineCmd)
        chessEngine=Engine(engineConfigs[engineCmd])
        engine=chessEngine.open()
        if engine is None:
            raise Exception("Could not open %s engine" % engineCmd)
        board = chess.Board()
        game = chess.pgn.Game() 
        game.headers["Event"] = "test_chessengine %s" % (chessEngine.name)
        game.headers["Site"] = "http://wiki.bitplan.com/index.php/PlayChessWithAWebCam" 
        game.headers["White"] = "%s" % (chessEngine.name)
        game.headers["Black"] = "%s" % (chessEngine.name)
        game.headers["Date"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        moveIndex=0
        node=None
        while not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(time=0.1))
            move=str(result.move)
            board.push(result.move)
            print ("%d-%s: %s" % (moveIndex//2+1,"white" if moveIndex%2==0 else "black",move))
            print (board.unicode())
            if moveIndex == 0:
                node = game.add_variation(chess.Move.from_uci(move))
            else:
                node = node.add_variation(chess.Move.from_uci(move))
            moveIndex+=1
    
        engine.quit()    
        print (game)   
        # try pasting resulting pgn to
        # https://lichess.org/paste            

test_engines()
test_play()