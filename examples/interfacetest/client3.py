from domino3 import Domino

def DominoClient(cmd):
    if cmd == 'DrawDominoSet()':
        DrawDominoSet()
    elif cmd == 'Domino(3,5).getLeftDots()':
        domino = Domino(3,5)
        print(domino.getLeftDots())
    elif cmd == 'Domino(3,5).getRightDots()':
        domino = Domino(3,5)
        print(domino.getRightDots())

def DrawDominoSet():
    for left in range(0,7):
        dominoRow = []
        for right in range(left, 7):
            nextDomino = Domino(left, right)
            dominoRow.append(nextDomino)
        print(' '.join([str(domino) for domino in dominoRow]))

            
        