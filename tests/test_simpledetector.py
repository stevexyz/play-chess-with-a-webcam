'''
Created on 2019-12-14

@author: wf
'''
from pcwawc.args import Args
from pcwawc.videoanalyze import VideoAnalyzer
from pcwawc.environment4test import Environment4Test
import getpass

testEnv=Environment4Test()

class MoveChecker():
    def __init__(self,analyzer):
        self.analyzer=analyzer
        self.moveCount=0
        
    def onMove(self,event):
        move=event.move
        self.moveCount+=1
        #if str(move) in ["f1c4","g8f6"]:
        #    self.analyzer.moveDetector.frameDebug=True
        #    # fake calibration to pre move transition (time to short in this video)
        #    ic=self.analyzer.moveDetector.imageChange
        #    #ic.transitionToPreMove()
        pass

def test_SimpleDetector():
    warpPointList=[ 
                   (),
                   ([0,610],[0,0],[610,0],[610, 610]),
                   ([143,9],[503,9],[505,375],[137,373]),
                   ([143,9],[503,9],[505,375],[137,373]),
                   ]
    rotation=[0,0,90]
    #index=-1
    #for testVideo in testEnv.getTestVideos():
    #    index+=1 
    #    if getpass.getuser()=="wf":
    #        if index==0:
    #            continue
    #        if index==2:
    #            break
    if getpass.getuser()!="travis":
        index=0
        testVideo="scholarsMate2019-12-18.avi"
        path=testEnv.testMedia+testVideo
        print (testVideo)
        cmdlineArgs=Args("test")
        cmdlineArgs.parse(["--input",path,"--detect","simple8x8"])
        analyzer=VideoAnalyzer(cmdlineArgs.args)
        moveChecker=MoveChecker(analyzer)
        analyzer.open()
        vision=analyzer.vision
        if index<len(warpPointList):
            warpPoints=warpPointList[index]
            if len(warpPoints)>0:
                vision.warp.pointList=warpPoints
                vision.warp.updatePoints() 
            else:
                vision.warp.warping=True
                cmdlineArgs.args.nowarp=True    
            vision.warp.rotation=rotation[index]
        else:
            analyzer.nextImageSet()
            analyzer.findChessBoard()
        analyzer.setUpDetector()
        analyzer.moveDetector.subscribe(moveChecker.onMove)
        #analyzer.moveDetector.debug=True
        #analyzer.moveDetector.frameDebug=True
        pgn=analyzer.analyze()
        print (pgn)

test_SimpleDetector()
    
