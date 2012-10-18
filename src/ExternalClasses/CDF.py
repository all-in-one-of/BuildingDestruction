# -*- coding: utf-8 -*-
import random
class CDF:
    @staticmethod
    def cdf(PList):
        """
        Cumulative distribution function

        In probability theory and statistics, the cumulative distribution function (CDF),
        or just distribution function, describes the probability that a real-valued random
        variable X with a given probability distribution will be found at a value less than or
        equal to x.

        Intuitively, the function tell you one ID(from all ID's) taking into account the provability
        to choose that ID.
        _________________________________

        Usage:
        PList in format [[Provability,ID],...]
        Call the function like: CDF.cdf(PList)
        _______________________________________________________________________

        Examples:
        If you put one ID with 100% of chance, the function will return that ID
        >>> CDF.cdf([[100,0]])
        0

        If you put one ID with 0% of chance, the function will return that ID
        >>> CDF.cdf([[0,0]])
        0

        In the next test, the probability are 50 in both ID, so, in the normal case, the summation
        of returns from the function are 50 about 100 in each case.
        >>> if(True):
        ...     acum0=0
        ...     acum1=0
        ...     for i in range(100000):
        ...         if(CDF.cdf([[50,0],[50,1]])==0): acum0+=1
        ...         else: acum1+=1
        ...     print int(round(float(acum0)/1000))
        ...     print int(round(float(acum1)/1000))
        50
        50
        
        In the next test, the probability are 10 in firts ID, 90 in second ID and 150 in third ID
        so, in the normal case, the summation of returns from the function are 10, 90 and 150 about 250
        in each case.
        >>> if(True):
        ...     acum0=0
        ...     acum1=0
        ...     acum2=0
        ...     for i in range(250000):
        ...         res=CDF.cdf([[10,0],[90,1],[150,2]])
        ...         if(res==0): acum0+=1
        ...         elif(res==1): acum1+=1
        ...         else:acum2+=1
        ...     print int(round(float(acum0)/1000))
        ...     print int(round(float(acum1)/1000))
        ...     print int(round(float(acum2)/1000))
        10
        90
        150
        """
        if PList != []:
            PList.sort(reverse=True)
            cumList = []
            aux = 0
            for pos in range(len(PList)):
                aux += PList[pos][0]
                cumList.append([aux, PList[pos][1]])
            rand = random.random() * cumList[(len(cumList) - 1)][0]
            pos2 = 0
            while(rand > cumList[pos2][0]):
                pos2 += 1
            return cumList[pos2][1]
        else:
            return None
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
