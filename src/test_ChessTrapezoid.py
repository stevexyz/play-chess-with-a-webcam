#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Environment4Test import Environment4Test
from Video import Video
from ChessTrapezoid import ChessTrapezoid, FieldState, Color
from timeit import default_timer as timer
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import pytest
import chess

testEnv = Environment4Test()
speedup=5 # times 
waitAtEnd=0 # msecs
debug=False
debugChangeHistory=False
debugPlotHistory=False
displayImage=False
displayDebug=False

def test_RankAndFile():
    csquare=ChessTrapezoid((0,0),(100,0),(100,100),(0,100))
    for square in chess.SQUARES:
        tsquare=csquare.tsquares[square]
        assert tsquare.an==chess.FILE_NAMES[tsquare.col]+chess.RANK_NAMES[7-tsquare.row]
    
def test_Rotation():
    csquare=ChessTrapezoid((0,0),(100,0),(100,100),(0,100))
    rotations=[0,90,180,270]
    indices=[(0,0),(7,0),(7,7),(0,7)]
    expected=[(0,0),(7,0),(7,7),(0,7),
              (7,0),(7,7),(0,7),(0,0),
              (7,7),(0,7),(0,0),(7,0),
              (0,7),(0,0),(7,0),(7,7)]
    index=0
    for rotation in rotations:
        csquare.rotation=rotation
        anstr=""
        for row in range(ChessTrapezoid.rows):
            for col in range(ChessTrapezoid.cols):
                tsquare=csquare.tSquareAt(row, col)
                anstr=anstr+tsquare.an
            anstr=anstr+'\n'
        print (anstr)       
        for rowcol in indices:
            row,col=rowcol
            rotated=csquare.rotateIndices(row,col,rotation)
            print (rotation,rowcol,rotated,expected[index])
            assert rotated==expected[index]
            index=index+1
           
def test_Transform():
    trapez=ChessTrapezoid((20,40),(44,38),(60,8),(10,10))
    #if debug:
    #    plt.figure()
    #    plt.plot(trapez.pts_normedSquare[[0,1,2,3,0], 0],trapez.pts_normedSquare[[0,1,2,3,0], 1], '-')
    squarePatches = []
    tSquarePatches = []    
    # https://stackoverflow.com/questions/26935701/ploting-filled-polygons-in-python
    for square in chess.SQUARES:
        tsquare=trapez.tsquares[square]
        color=[1,1,1,1] if tsquare.fieldColor else [0.1,0.1,0.1,1]
        polygon=Polygon(tsquare.rpolygon,color=color)
        tpolygon=Polygon(tsquare.polygon,color=color)
        squarePatches.append(polygon)
        tSquarePatches.append(tpolygon)
    # https://stackoverflow.com/questions/44725201/set-polygon-colors-matplotlib    
    squareP = PatchCollection(squarePatches,match_original=True) 
    tSquareP = PatchCollection(tSquarePatches,match_original=True)    

    if debug:        
        fig, ax = plt.subplots(2)
        ax1=ax[0]
        ax1.set_title("relative normed square")
        ax1.add_collection(squareP)
        ax1.set_ylim(ax1.get_ylim()[::-1])
        ax2=ax[1]      

        ax2.set_title("trapezoidal warp")
        ax2.add_collection(tSquareP)
        ax2.autoscale()
        plt.show()               

def test_RelativeToTrapezXY():
    trapez=ChessTrapezoid((20,40),(40,40),(60,10),(10,10))
    rxrys=[(0,0),(1,0),(1,1),(0,1),(0,0.5),(0.5,0.5),(1,0.5)]
    expected=[(20,40),(40,40),(60,10),(10,10),(17.1,31.4),(31.4,31.4),(45.7,31.4)]
    for index,rxry in enumerate(rxrys):
        rx,ry=rxry
        x,y=trapez.relativeToTrapezXY(rx,ry)
        ex,ey=expected[index]
        print ("%d r:(%.1f,%.1f) e:(%.1f,%.1f) == (%.1f,%.1f)?" % (index,rx,ry,ex,ey,x,y))   
        assert x ==pytest.approx(ex,0.1) 
        assert y ==pytest.approx(ey,0.1)
        
def test_SortedTSquares(): 
    trapezoid=ChessTrapezoid((140,5),(506,10),(507,377),(137,374))
    trapezoid.updatePieces(chess.STARTING_FEN)    
    sortedTSquares=trapezoid.byFieldState()
    expected=[16,8,8,16,8,8]
    for fieldState,tsquareList in sortedTSquares.items():
        l=len(tsquareList)
        if debug:
            print(fieldState.title(),l)
        assert expected[fieldState]==l

def test_Stats():    
    h=2
    w=2
    channels=3

    image=np.zeros((h,w,channels), np.uint8)
    image[0,0]=(100,50,200)
    image[0,1]=(120,60,220)
    avgcolor=Color(image)
    gmean,bmean,rmean=avgcolor.color
    gstds,bstds,rstds=avgcolor.stds
    if debug:
        print ("means %.2f %.2f %.2f " % (gmean,bmean,rmean))
        print ("stds  %.2f %.2f %.2f " % (gstds,bstds,rstds))
    assert avgcolor.color==(110.00,55.00,210.00 )
    assert avgcolor.stds==(5.00,10.00,10.00)      

def test_ChessTrapezoid():
    video=Video()
    testPath=testEnv.testMedia + 'scholarsmate.avi'
    frames=334
    trapezoid=ChessTrapezoid((140,5),(506,10),(507,377),(137,374),rotation=270,idealSize=800) 
    #testPath="/Users/wf/source/python/play-chess-with-a-webcam/media/chessVideo2019-10-17_185821.avi"
    #trapezoid=ChessTrapezoid((210, 0), (603, 6), (581, 391), (208, 378),rotation=270,idealSize=800)
    #frames=2000
    video.open(testPath)
    start=timer()  
    colorHistory={}
    changeHistory={}
    for frame in range(frames):
        ret, bgr, quitWanted = video.readFrame(show=False)
        assert ret
        assert bgr is not None     
        h,w = bgr.shape[:2]
        if frame==0:
            #trapezoid.prepareMask(bgr)
            #trapezoid.maskPolygon(trapezoid.polygon)  
            trapezoid.updatePieces(chess.STARTING_BOARD_FEN)
        startc=timer()  
        warped=trapezoid.warpedBoardImage(bgr)
        warpedHeight, warpedWidth = warped.shape[:2]
        trapezoid.analyzeColors(warped)
        idealImage=trapezoid.idealColoredBoard(warpedWidth,warpedHeight)
        diffImage=trapezoid.diffBoardImage(warped,idealImage)
        changeHistory[frame]=trapezoid.detectChanges(diffImage)
        # diffSum=trapezoid.diffSum(warped,idealImage)
        endc=timer()
        print('image analysis for %dx%d frame %d took %.3f s' % (w,h,frame,endc-startc))    
        colorHistory[frame]=trapezoid.averageColors.copy()
        
        #mask=trapezoid.getEmptyImage(bgr)
        #trapezoid.drawFieldStates(mask,[FieldState.BLACK_EMPTY,FieldState.WHITE_EMPTY])
        #masked=trapezoid.maskImage(bgr,mask)
        #warped=trapezoid.warpedBoard(masked)
        if frame % speedup==0:
            keyWait=5
            #trapezoid.drawDebug(warped)
            if displayImage:
                video.showImage(warped, "warped", keyWait=keyWait)
            if displayDebug:
                #trapezoid.drawDebug(idealImage)
                video.showImage(idealImage,"ideal")
                trapezoid.drawDebug(diffImage)
                video.showImage(diffImage,"diff")
           
    end=timer()
    print('read %3d frames in %.3f s at %.0f fps' % (frames,end-start,(frames/(end-start))))
    if debugChangeHistory:
        ans=[]
        #ans=["e2","e4","e7","e5","d1","h5","b8","c6","f1","c4","c8","f6","f7","a1","h8"]
        for square in chess.SQUARES:
            tsquare=trapezoid.tsquares[square]
            ans.append(tsquare.an)
        plotChangeHistory(changeHistory,ans)
    if debugPlotHistory:
        plotColorHistory(colorHistory)
    if waitAtEnd>0:
        video.showImage(warped, "warped", keyWait=waitAtEnd)
        
def plotChangeHistory(changeHistory,ans):
    l=len(changeHistory)
    anIndex=0
    for an in ans:
        x=np.empty(l)
        y=np.empty(l)
        for frame,changes in changeHistory.items():
            x[frame]=frame
            y[frame]=changes[an]
        plt.plot(x,y,label=an)   
        anIndex+=1       
    plt.title("difference from ideal per square over time")      
    plt.legend()      
    plt.show()    
            
        
def plotColorHistory(colorHistory):
    l=len(colorHistory)
    print ("color  history for %d frames" % (l))    
    #fig,ax=plt.subplots(len(FieldState))
    markers=['s','o','v','^','<','>']
    dist=10
    for fieldState in FieldState:
        size=l//dist
        x=np.empty(size)
        r=np.empty(size)
        g=np.empty(size)
        b=np.empty(size)
        for frame,avgColors in colorHistory.items():
            avgColor=avgColors[fieldState]
            if frame%dist==0:
                index=frame//dist
                if index<size:
                    x[index]=frame
                    b[index],g[index],r[index]=avgColor.color
        #ax[fieldState].set_title(fieldState.title())    
        plt.plot(x,r,c='r',marker=markers[fieldState])
        plt.plot(x,g,c='g',marker=markers[fieldState])
        plt.plot(x,b,c='b',marker=markers[fieldState],label=fieldState.title())
        #ax[fieldState].autoscale()
    plt.legend()    
    plt.show()
    
test_RankAndFile()    
test_Rotation()     
test_Transform() 
test_RelativeToTrapezXY()  
test_SortedTSquares()
test_Stats() 
test_ChessTrapezoid()