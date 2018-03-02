from typing import Tuple
import constants
import random
import copy
from enum import Enum

class PropertyResponse(Enum):
    Purchase = 0
    Spend = 1
    Chance = 2
    GotoJail = 3
    SpecialBehaviour = 99

    class InvalidResponse(Exception):
        ...

class GoPastResponse(Enum):
    GetMoney = 0

class NotEnoughMoney(Exception):
    pass


class Player:
    def __init__(self, name, money, position=0):
        self.name = name
        self.money = money
        self.location = position
        self.properties = set()


    def move(self, amount, maxIndex):
        self.location += amount
        self.location = self.location % maxIndex

    def add_property(self, property):
        self.properties.add(property)

    def give_money(self, money, otherplayer):
        """
        :param money:  amouunt (int)
        :param otherplayer: otherplayer (Player)
        :return:
        """
        if money > self.money:
            raise NotEnoughMoney
        else:
            self.money -= money
            otherplayer.money += money
            return True

    def can_withdraw(self, amount):
        return False if self.money < amount else True



class Property:
    @staticmethod
    def SpecialPropOptions():
        """
        :return: set(Of PropertyResponse), possible things to do on this property, override on specialProperty
        """
        return set(PropertyResponse.SpecialBehaviour)

    def __init__(self, color, name, cost, startrent, description):
        """
        :param color: ColorSet (str)
        :param name:  Name     (str)
        :param cost:  Cost     (int)
        :param description: Short descrip (str)
        :return: Property
        """
        self.color = color
        self.name = name
        self.description = description
        self.cost = cost
        self.NoBuySell = False
        self.rent = startrent
        ##
        self.owner = None
        self.mortgage = False
        ##
    def landed_on_force(self, player, board):
        """
        if the player is forced to do something!
        :param player: player
        :param board:  board
        :return:       True/False if sucess ! to be overriden in subclasses
        """
        return False

    def get_actions_landed(self):
        """
        Get Possible reactions when landing on a property
        :return: set() of PropertyResponseEnums
        """
        ret = set()
        if not self.NoBuySell:
            if self.owner:
                # if morgaged
                if not self.mortgage:
                    ret.add(PropertyResponse.Spend)
            else:
                ret.add(PropertyResponse.Spend)
        return ret


    def respond_landed(self, player, board, response=None):
        """
        Takes the action, player and board and processes that response
        :param response: Action, PropertyResponse
        :return: None
        Will raise Exceptions if money is not enough, etc etc
        """
        if response is None:
            return
        if response == PropertyResponse.Spend:
            assert not self.NoBuySell
            player.give_money(self.rent, player)
        elif response == PropertyResponse.Buy:
            assert not self.NoBuySell
            self.owner.properties.remove(self)
            self.owner = player
            player.properties.add(self)


    def respond_passed_force(self, player, board):
        """
        called if a player goes thru a property but not land on
        :param player: Player
        :param board:  Board
        :return:  False/True
        """
        return False


    def same_set(self, other):
        if other.color == self.color:
            return True
        else:
            return False

    @staticmethod
    def set_complete(item, set_of_properties, property_to_color, color_to_property_set):
        """Returns True if set_of_properties contains all of item's color, from dictionaries given"""
        try:
            set_needed = color_to_property_set[property_to_color[item]]
            for i in set_needed:
                if i not in set_of_properties:
                    return False
            return True
        except KeyError:
            print("KEY", item, "NOT FOUND!")
            raise


class SpecialProperty(Property):
    def Chance_landed_force(self, player, board):
        constants.ChanceApply(random.choice(constants.K_CHANCE), player)
    def GotoJail_landed_force(self, player, board):
        player.location = board.JailLocation
        assert player.location != None
    def GetMoney_passed_force(self, player, board):
        player.money += constants.K_GO_MONEY

    def __init__(self, color, name, cost, startrent, description, override_land_on_force=None, override_passed_force=None,
                 noBuySell=True):
        """
        Property with special behaviour
        :param color: color (str)
        :param name:  name  (str)
        :param cost:  cost  (int)
        :param description:  description (str)
        :param specialBehaviour: function run when player steps on
        :param noBuySell:
        :param SpecialPropOptions: list of event handlers: []
        :return:
        """
        super(SpecialProperty, self).__init__(color, name, cost, startrent, description)
        self.NoBuySell = noBuySell
        if callable(override_land_on_force):
            self.override_land_on_force = [override_land_on_force]
        if callable(override_passed_force):
            self.override_passed_force = [override_passed_force]
        assert isinstance(override_passed_force, list) and isinstance(override_land_on_force, list)
        for i in override_land_on_force + override_passed_force:
            assert callable(i)


    def landed_on_force(self, player, board):
        super().landed_on_force(player,board)
        for i in self.override_land_on_force:
            i()

    def respond_passed_force(self, player, board):
        super().respond_passed_force(player, board)
        for i in self.override_passed_force:
            i()





class Board:
    def __init__(self, length, height):
        """
        Creates a board object
        length: Length of board (int)
        height: Height of board (int)
        no_players: Number of Players (int)
        na_players: Names of Players (tuple/list)
        startamount: Starting money (int)
        handicap: List showing handicap to give to players: (0,0,3) = +3 dollars for p3 (tuple)
        """
        self.length = length
        self.height = height
        self.display_board = []

        for i in range(height):
            if i == 0 or i == height-1:
                # first and last rows
                self.display_board.append(['*'] * length)
            else:
                self.display_board.append(['*'] + [' '] * (length - 2) + ['*'])
        self.totalcells = length * 2 + (height-2) * 2
        self.maxIndex = self.totalcells -  1
        self.board = [None] * (length * 2 + (height-2) * 2)
        self.playerlist = []
        self.property_to_player = {} # {property: player}
        self.property_to_color = {}  # {property: color}
        self.color_to_property = {}  # {color: (property1,...)}
        self.JailLocation = None
        self.assignColors()


    def __str__(self):
        return '\n'.join((''.join(x) for x in self.display_board))

    def add_player(self, name, startamount, handicap=0,startPos=0):
        startPos %= self.maxIndex
        self.playerlist.append(Player(name,startamount+handicap,startPos))

    @staticmethod
    def chancePercent(percent):
        assert percent < 100
        if random.randint(1,100) <= percent:
            return True
        return False

    def assignColors(self):
        current_slot = 0
        # for top segment, 1-(length-2), for a total of length of length-2
        colorList = copy.deepcopy(constants.K_COLORS)
        for iteration,bitlen in enumerate([self.length-2, self.height-2]*2):
            local_slot = 0

            # add one of the special pieces
            if iteration == 0:# top left corner
                self.board[current_slot] = SpecialProperty(None, "Go", None, None, "Go past go to get %d dollars" % constants.K_GO_MONEY,override_passed_force=SpecialProperty.GetMoney_passed_force, override_land_on_force=SpecialProperty.GetMoney_passed_force)
                current_slot += 1

            current_color = []
            while True:
                spacesLeft = bitlen - local_slot

                if not current_color:
                    # first get a random color
                    # if there is only 3 left
                    if spacesLeft == 3:
                        # get a non-utility
                        nonUtilsRemaining =  constants.K_COLORS.intersection(colorList)
                        assert len(nonUtilsRemaining) > 0
                        current_color = random.choice(list(nonUtilsRemaining))
                        colorList.
                        colorLen = 3
                    elif spacesLeft == 2:

                    elif spacesLeft == 1:

                    else:
                        current_color = random.choice(colorList)
                        if current_color[0]  in constants.K_UTILS:
                            colorList.remove(current_color)
                            colorLen = 1
                        # get length
                        else:
                            colorLen = 3 if self.chancePercent(75) else 2



























if __name__ == '__main__':
    x = Board(length=10, height=10)
    x.add_player('Jack', 1000)
