"""State Module"""
from state_action_enums import Outcomes

NONE=(0,0,0,0,0,0,0,0,0)

def nxt(b):
    i=b.index(1)
    if i==8:
        nxt=0
    else:
        nxt=i+1
    batter=list(NONE)
    batter[nxt]=1
    return(tuple(batter))
    #return b

class State:
    """State is the parent class of all state distributions

    Attributes
    ----------
    outcomes : Outcomes
        all the possible outcomes for a state (e.g. foul, out, hit, strike, ball)

    Methods
    -------
    get_successors():
        returns all possible successor states based on all possible outcomes
    """

    def __init__(self, outcomes: Outcomes) -> None:
        """Instatiates State object"""
        self.outcomes = outcomes

    def get_successors(self) -> dict:
        """Returns a dictionary of key, outcome and value, resulting state

        Returns
        -------
        dict
            a dict of outcome and resulting state dict[outcome] = State
        """

    def get_state(self, balls: int, strikes: int) -> str:
        """Returns the name of the state as a string

        Returns
        -------
        str
            name of the state
        """


class Count(State):
    """Class used to represent CountState

    Attributes
    ----------
    ball_count : int
        number of balls in the count
    strike_count : int
        number of strikes in the count

    Methods
    -------
    get_successors()
        returns all possible successor states given outcomes
    """

    def __init__(self, outcomes: Outcomes, num_balls: int, num_strikes: int) -> None:
        """Instantiates CountState object

        Parameters
        ----------
        ball_count : int
            number of balls in the count in range (0,3)
        strike_count : int
            number of strikes in the count in range (0,2)
        """
        super().__init__(outcomes)
        self.num_balls = num_balls
        self.num_strikes = num_strikes
        self.state_name = str(num_balls) + str(num_strikes)

    def get_successor(self, res: str) -> dict:
        """Returns a dictionary of possible successor states over outcomes (excluding out)

        Returns
        -------
        dict
            a dict of outcome and resulting state dict[outcome] = str(Count)
        """

        # return terminal states
        if res in [self.outcomes.SINGLE.value, self.outcomes.DOUBLE.value,self.outcomes.TRIPLE.value,self.outcomes.HOMERUN.value,self.outcomes.STRIKEOUT.value,self.outcomes.GROUNDOUT.value]:
            # print(res)
            return res

        # count is full 3-2, ball -> hit, strike -> out, foul -> itself
        if self.num_balls == 3 and self.num_strikes == 2:
            if res == self.outcomes.STRIKE.value:
                return self.outcomes.STRIKEOUT.value
            if res == self.outcomes.BALL.value:
                return self.outcomes.SINGLE.value
            return self.state_name

        # count is x-2, strike -> out, foul -> itself
        if self.num_balls < 3 and self.num_strikes == 2:
            if res == self.outcomes.STRIKE.value:
                return self.outcomes.STRIKEOUT.value
            if res == self.outcomes.BALL.value:
                return self.get_state(self.num_balls+1, self.num_strikes)
            return self.state_name

        # count is 3-x, ball -> hit
        if self.num_balls == 3 and self.num_strikes < 2:
            if res == self.outcomes.STRIKE.value:
                return self.get_state(self.num_balls, self.num_strikes+1)
            if res == self.outcomes.BALL.value:
                return self.outcomes.SINGLE.value
            return self.get_state(self.num_balls, self.num_strikes+1)

        # count is not 3-x or x-2
        if res == self.outcomes.STRIKE.value:
            return self.get_state(self.num_balls, self.num_strikes+1)
        if res == self.outcomes.BALL.value:
            return self.get_state(self.num_balls+1, self.num_strikes)
        return self.get_state(self.num_balls, self.num_strikes+1)

    @classmethod
    def get_state(cls, balls: int, strikes: int) -> str:
        """Returns the name of the state as a string

        Returns
        -------
        str
            name of the state
        """
        return str(balls) + str(strikes)

    def __repr__(self):
        """Displays the inputs used to instantiate the object"""
        return (
            f"Count({self.outcomes}, {self.num_balls}, {self.num_strikes})"
        )

    def __str__(self):
        """Prints information about the object"""
        return (
            f"outcomes: {self.outcomes},\
            num_balls: {self.num_balls},\
            num_strikes: {self.num_strikes}"
        )


class Inning:

    def __init__(self,atbat,base,stat,N):
        """Instantiates CountState object

        Parameters
        ----------
        count : dict
            Recorded number of balls and strikes
        atbat : tuple
            Current batter/player at bat
        base: dict
            Binary indication of whether a player is on a given base
        stat: dict
            Recording of current number of runs and outs in the Inning
            
        Methods
        -------
        get_successor(res)
            returns Inning successor state given an outcome
        
        reward()
            returns int reward value of the game state
            
        count()
            returns str of ball-strike count of the current game state
        """
        self.atbat=atbat
        self.base=base
        self.stat=stat
        self.N=N
        self.state_name=str((self.atbat,self.base,self.stat))
        
    def get_successor(self,action):
        runs=0
        atbat=self.atbat[:]
        base=self.base.copy()
        stat=self.stat.copy()
        
        if atbat==NONE:
            #terminal state, returns itself as successor
            return self
        
        elif action == "out":
            #Update stats
            stat["strikes"]=0
            stat["balls"]=0
            stat["outs"]+=1
            
            #End game immediately on third strike
            if stat["outs"]>=3:
                return Inning(NONE,{1:0,2:0,3:0},stat,self.N)
            else:
                #Player on base 3 scores
                if base[3]==1:
                    runs+=1
                stat["runs"]+=runs
                
                #Check if terminal score is reached
                if stat["runs"]>=self.N:
                    stat["runs"]=self.N
                    stat["outs"]=3
                    return Inning(NONE,{1:0,2:0,3:0},stat,self.N)
                
                #Move players up 1 base
                base[3]=base[2]
                base[2]=base[1]
                base[1]=0
                return Inning(nxt(atbat),base,stat,self.N)
        
        elif action=="single":
            #Update stats
            stat["strikes"]=0
            stat["balls"]=0
            runs+=base[2]
            runs+=base[3]
            stat["runs"]+=runs
            
            #Stops game at terminal score
            if stat["runs"]>=self.N:
                stat["runs"]=self.N
                stat["outs"]=3
                return Inning(NONE,{1:0,2:0,3:0},stat,self.N)
            
            #Update bases and return successor
            base[3]=base[1]
            base[2]=0
            base[1]=1
            return Inning(nxt(atbat),base,stat,self.N)
        
        elif action in ["double","triple","home run"]:
            #Update count
            stat["strikes"]=0
            stat["balls"]=0
            
            #Score players on-base
            for b in base:
                runs+=base[b]
            stat["runs"]+=runs
            
            #Stops game at terminal score
            if stat["runs"]>=self.N:
                stat["runs"]=self.N
                stat["outs"]=3
                return Inning(NONE,{1:0,2:0,3:0},stat,self.N)
            
            if action=="double":
                return Inning(nxt(atbat),{1:0,2:1,3:0},stat,self.N)
            
            elif action=="triple":
                return Inning(nxt(atbat),{1:0,2:0,3:1},stat,self.N)
            
            else:
                #Score batter
                stat["runs"]+=1
                
                #Second check for terminal score
                if stat["runs"]>=self.N:
                    stat["runs"]=self.N
                    stat["outs"]=3
                    return Inning(NONE,{1:0,2:0,3:0},stat,self.N)
                
                return Inning(nxt(atbat),{1:0,2:0,3:0},stat,self.N)
        
        elif action == "strike":
            if stat["strikes"]==2:
                #Update stats and reset count
                stat["strikes"]=0
                stat["balls"]=0
                stat["outs"]+=1
                
                #Continue game with less than 3 outs, terminate otherwise
                if stat["outs"]<=2:
                    return Inning(nxt(atbat),base,stat,self.N)
                return Inning(NONE,{1:0,2:0,3:0},stat,self.N)
            
            #If less than 2 strikes, update count
            stat["strikes"]+=1
            return Inning(atbat,base,stat,self.N)
        
        elif action=="ball":
            if stat["balls"]==3:
                #Reset count
                stat["strikes"]=0
                stat["balls"]=0
                
                #Load bases, update score if all bases loaded
                if base[1]==0:
                    base[1]=1
                elif base[2]==0:
                    base[2]=1
                elif base[3]==0:
                    base[3]=1
                else:
                    runs+=1
                stat["runs"]+=runs
                
                #Stop game at terminal score, send next batter otherwise
                if stat["runs"]>=self.N:
                    stat["runs"]=self.N
                    stat["outs"]=3
                    return Inning(NONE,{1:0,2:0,3:0},stat,self.N)
                return Inning(nxt(atbat),base,stat,self.N)
            
            #Update "ball" count if less than 3 "balls" recorded
            stat["balls"]+=1
            return Inning(atbat,base,stat,self.N)
        
        elif action=="foul":
            #Adds to strike count when current at-bat count has less than 2 strikes
            if stat["strikes"]<2:
                stat["strikes"]+=1
            return Inning(atbat,base,stat,self.N)
    
    def reward(self):
        if self.stat["outs"]==3:
            return self.stat["runs"]
        return 0
        
    def Count(self):
        return str(self.stat["balls"])+str(self.stat["strikes"])
        
    def __eq__(self,o):
        if self.atbat==o.atbat and self.base==o.base and self.stat==o.stat:
            return True
        return False
    
    def __hash__(self):
        return tuple((self.atbat,tuple(self.base.items()),tuple(self.stat.items()))).__hash__()
    
    def __repr__(self):
        return str((self.atbat,self.base,self.stat,self.prev))
    
    def __str__(self):
        return str((self.atbat,self.base,self.stat,self.prev))
