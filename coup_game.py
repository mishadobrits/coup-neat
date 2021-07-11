import itertools
import random
from typing import Any, List, Dict, Tuple, Union, Iterator, Literal
from typing import get_args


class Probability:
    def __init__(self, value: float):
        if value < 0:
            raise ValueError(f"Negative value={value} were given")
        if value > 1:
            raise ValueError(f"Probability value={value} > 1")
        self.v = value

    def __str__(self):
        return f"Probability({self.v})"

    def random(self):
        return random.random() < self.v


class LiteralStr:
    literal: List[str] = []

    def __init__(self, title: str):
        self.title = title

    def __eq__(self, other):
        return self.title == other.title

    def __lt__(self, other):
        return self.title < other.title

    def __hash__(self):
        return hash(type(self)) + hash(self.title)

    def __str__(self):
        return f"{type(self).__name__}({self.title})"

    def __repr__(self):
        return str(self)

    @classmethod
    def is_valid(cls, str):
        return str in get_args(cls.literal)

    @classmethod
    def from_input(cls):
        rt = ""
        while rt not in get_args(cls.literal):
            rt = input(f"Input {cls.__name__}: ").title()
        return cls(rt)


class WhoCanBlock(LiteralStr):
    literal = ["No_one", "Victim", "Every_one"]

    def __init__(self, title: literal):
        super(WhoCanBlock, self).__init__(title)

    def players_who_can_block(self,
                              players_number: int,
                              action,  # Action
                              ) -> List[int]:
        if self == NO_ONE or (self == VICTIM and not action.victim_index):
            return []
        elif self == VICTIM and action.victim_index:
            return [action.victim_index]
        elif self == EVERY_ONE:
            return [player for player in range(players_number) if player != action.sender_index]
            # return list(filter(lambda player: player != action.sender_index, players_number))


NO_ONE = WhoCanBlock("No_one")
VICTIM = WhoCanBlock("Victim")
EVERY_ONE = WhoCanBlock("Every_one")


class Card(LiteralStr):
    literal = Literal["Duke", "Assassin", "Captain", "Ambassador", "Contessa", "Any"]

    def __init__(self, title: literal):
        super(Card, self).__init__(title)
DUKE = Card("Duke")
ASSASSIN = Card("Assassin")
CAPTAIN = Card("Captain")
AMBASSADOR = Card("Ambassador")
CONTESSA = Card("Contessa")
FICTION_ANY_CARD = Card("Any")


class ActionBase(LiteralStr):
    literal = Literal["Income", "Foreign_Aid", "Coup", "Tax", "Assassinate", "Steal", "Exchange"]

    def __init__(self, title: literal):
        super(ActionBase, self).__init__(title)
INCOME = ActionBase("Income")
FOREIGN_AID = ActionBase("Foreign_Aid")
COUP = ActionBase("Coup")
TAX = ActionBase("Tax")
ASSASSINATE = ActionBase("Assassinate")
STEAL = ActionBase("Steal")
EXCHANGE = ActionBase("Exchange")


class Action:
    def __init__(self,
                 title: ActionBase.literal,
                 sender_index: int,
                 victim_index: Union[int, None] = None):
        self.title = title
        self.sender_index = sender_index
        self.victim_index = victim_index

    def base(self) -> ActionBase:
        return ActionBase(self.title)

    @staticmethod
    def from_input(sender_index: int):
        base = ActionBase.from_input()
        if HAS_VICTIM[base]:
            victim_index = int(input("Input victim_index (from alive players): "))
        else:
            victim_index = None
        return __class__(base.title, sender_index, victim_index)

    def __str__(self):
        s = f"{self.title}(sender={self.sender_index}%s)"
        if self.victim_index:
            return s % f", victim={self.victim_index}"
        return s % ""


CAN_BE_PLAYED_BY: Dict[ActionBase, Card] = {
    INCOME: FICTION_ANY_CARD,
    FOREIGN_AID: FICTION_ANY_CARD,
    COUP: FICTION_ANY_CARD,
    TAX: DUKE,
    ASSASSINATE: ASSASSIN,
    STEAL: CAPTAIN,
    EXCHANGE: AMBASSADOR,
}

CAN_BE_BLOCKED_BY: Dict[ActionBase, List[Card]] = {
    INCOME: [],
    FOREIGN_AID: [DUKE],
    COUP: [],
    TAX: [],
    ASSASSINATE: [CONTESSA],
    STEAL: [CAPTAIN, EXCHANGE],
    EXCHANGE: []
}

WHO_CAN_BLOCK: Dict[ActionBase, WhoCanBlock] = {
    INCOME: NO_ONE,
    FOREIGN_AID: EVERY_ONE,
    COUP: NO_ONE,
    TAX: NO_ONE,
    ASSASSINATE: VICTIM,
    STEAL: VICTIM,
    EXCHANGE: NO_ONE
}

HAS_VICTIM: Dict[ActionBase, bool] = {
    INCOME: False,
    FOREIGN_AID: False,
    COUP: True,
    TAX: False,
    ASSASSINATE: True,
    STEAL: True,
    EXCHANGE: False
}


class PlayedMove:
    def __init__(self, n: int, action: Action, is_blocked: Union[bool, None]):
        self.n = n
        self.action = action
        self.is_blocked = is_blocked

    def to_array(self):
        pass

    def __str__(self):
        return f"PlayedMove(action={self.action}, is_blocked={self.is_blocked})"


class MovesHistory:
    """like List[PlayedMove]"""
    def __init__(self):
        self.list_of_moves: List[PlayedMove] = []

    def append_move(self, move: PlayedMove) -> None:
        self.list_of_moves.append(move)

    def __str__(self):
        last_5_moves = self.list_of_moves[:-6:-1]
        return "MovesHistory(\n" + "    \n".join(list(map(str, last_5_moves))) + ")"

    def to_list(self) -> List[float]:
        pass


class PublicPartOfPlayerState:
    def __init__(self, cards_number: int, coins_number: int):
        self.cards_number = cards_number
        self.coins_number = coins_number

    def __str__(self):
        return f"PPoPS(cards={self.cards_number}, coins={self.coins_number})"

    def __repr__(self):
        return str(self)


class PlayerState:
    def __init__(self, cards: Tuple[Card], coins: int):
        self.cards: List[Card] = list(cards)
        self.coins = coins

    def add_coins(self, numb):
        self.coins += numb
        if self.coins < 0:
            raise ValueError("Player has negative number of coins")

    def add_cards(self, cards: List[Card]):
        self.cards += cards

    def pop_card(self, card: Card):
        self.cards.pop(self.cards.index(card))

    def to_list(self) -> List[float]:
        pass

    def public_part(self) -> PublicPartOfPlayerState:
        return PublicPartOfPlayerState(len(self.cards), self.coins)

    def __str__(self):
        return f"PlayerState({self.cards}, coins={self.coins})"


class PlayerObservation:
    def __init__(self,
                 state: PlayerState,
                 discharge: List[Card],
                 players_visible_states: List[PublicPartOfPlayerState],
                 history: MovesHistory):
        self.state = state
        self.discharge = discharge
        self.players_visible_states = players_visible_states
        self.history = history

        self.info_dict: Dict[str, Any] = {
            "state": state,
            "discharge": discharge,
            "players_visible_states": players_visible_states,
            "history": history
        }

    def to_array(self) -> List[float]:
        pass

    def __str__(self):
        rt = "PlayerObservation(\n"
        rt += "\n".join([f"    {key}: {value}" for key, value in self.info_dict.items()])
        rt += "\n)"
        return rt

    def __repr__(self):
        return str(self)


class Player:
    """Base class for players (InputPlayer and NeatPlayer) classes"""
    def __init__(self, number_of_players: int, player_index: int):
        self.n = number_of_players
        self.index = player_index

    def action(self, smth: PlayerObservation) -> Action:
        pass

    def wants_to_check(self, player_index: int, card: Card, obs: PlayerObservation) -> bool:
        pass

    def card_to_block(self, action: Action, smth: PlayerObservation) -> Union[bool, Card]:
        pass

    def what_card_to_lose(self, observation: PlayerObservation) -> Card:
        pass

    def __str__(self):
        return f"{type(self).__name__}(index = {self.index}, n = {self.n})"


class InputPlayer(Player):
    """All moves are input by user."""
    def _print_situation(self, arg: Any, question: str) -> None:
        print(f"I'm {self}. {question}. Observation is\n{arg}")

    def action(self, observation: PlayerObservation) -> Action:
        self._print_situation(observation, "What is my action?")
        return Action.from_input(self.index)

    def card_to_block(self, action: Action, observation: PlayerObservation) -> Union[bool, Card]:
        self._print_situation(f"({str(action)}, {str(observation)})", "")
        if input_yes_or_not("Do I want block?") == "not":
            return False
        return Card.from_input()  # "Input Card to blocj"

    def wants_to_check(self, player_index: int, card: Card, observation: PlayerObservation) -> bool:
        self._print_situation((player_index, card, observation), "Do I want check?")
        return input_yes_or_not("Do I want check?") == "yes"

    def what_card_to_lose(self, observation: PlayerObservation) -> Card:
        self._print_situation(observation, "What card to lose")
        return Card.from_input()


class CardDeck:
    def __init__(self):
        self.cards: List[Card] = [DUKE, CAPTAIN, CONTESSA, ASSASSIN, AMBASSADOR] * 3

    def pop(self) -> Card:
        return self.cards.pop()

    def pop2(self) -> Tuple[Card, Card]:
        random.shuffle(self.cards)
        return self.pop(), self.pop()

    def add_card(self, card: Card):
        self.cards.append(card)

    def reshuffle(self, card: Card) -> Card:
        self.add_card(card)
        return self.pop()

    def __str__(self):
        rt = {}


class CoupGame:
    def __init__(self, players: List[Player], moves_number: int = 200):
        self.players = players
        self.n = len(players)
        if self.n > 7:
            raise ValueError("Players number must be <= 7 %d were given" % self.n)
        self.moves_number = moves_number

        self.deck = CardDeck()
        self.discharge: List[Card] = list()
        self.moves_history = MovesHistory()

        self.player_index_iter = itertools.chain(*[range(self.n) for _ in range(moves_number)])
        self.place_in_game: List[int] = list(itertools.repeat(1, self.n))

        fake_state = PlayerState((FICTION_ANY_CARD,), 0)
        self.player_state: List[PlayerState] = [fake_state for p in players]
        self.set_start_state()

    def set_start_state(self) -> None:
        for player_index, player in enumerate(self.players):
            self.player_state[player_index] = PlayerState(self.deck.pop2(), 2)

    def play(self) -> List[int]:
        def everyone_checks_if_he_wants(self, player_index: int, card: Card) -> bool:
            """
            Returns action_succeed == nobody stopped:
                    True if nobody checks or given player has given card
            """
            if card == FICTION_ANY_CARD:
                return True
            player_state: PlayerState = self.player_state[player_index]
            action_succeed = True
            for other in other_players(self.n, player_index):
                if not self.is_alive(other):
                    continue
                his_observation = self.player_observation(other)
                if players[other].wants_to_check(player_index, card, his_observation):
                    if card in player_state.cards:
                        self.kill_player(other)
                        player_state.pop_card(card)
                        player_state.add_cards([self.deck.pop()])
                        action_succeed = True  # unnecessary but why not
                    else:
                        self.kill_player(player_index)
                        action_succeed = False
                    break
            return action_succeed

        players, n = self.players, self.n
        for player_index in self.player_index_iter:
            if not self.is_alive(player_index):
                continue
            if sum(int(self.is_alive(player)) for player in range(self.n)) <= 1:
                # Game has ended.
                break
            player = players[player_index]
            player_observation = self.player_observation(player_index)

            action = player.action(player_observation)
            self.preexecute_action(action)

            is_action_succeed = everyone_checks_if_he_wants(
                self, player_index, CAN_BE_PLAYED_BY[action.base()]
            )
            if not is_action_succeed:
                continue

            is_block_succeed = False
            for blockator in WHO_CAN_BLOCK[action.base()].players_who_can_block(n, action):
                if not self.is_alive(blockator):
                    continue
                his_observation = self.player_observation(blockator)
                block_card = players[blockator].card_to_block(action, his_observation)
                if not block_card:
                    continue
                is_block_succeed = everyone_checks_if_he_wants(
                    self, blockator, block_card
                )
                if is_block_succeed:
                    break

            # todo Add moves

            if not is_block_succeed:
                self.execute_action(action)

        return self.place_in_game

    def kill_player(self,
                    index: int,
                    put_card_to: Literal["discharge", "deck"] = "discharge") -> None:
        if not self.player_state[index]:
            return
        lost_card = self.players[index].what_card_to_lose(self.player_observation(index))
        self.player_state[index].pop_card(lost_card)

        if not self.player_state[index].cards:
            self.place_in_game[index] = self.n - sum(self.is_alive(pl) for pl in range(self.n))

        if put_card_to == "discharge":
            self.discharge.append(lost_card)
        elif put_card_to == "deck":
            self.deck.add_card(lost_card)
        else:
            Warning(f"put_card_to argument is {put_card_to}")

    def player_observation(self, player_index) -> PlayerObservation:
        return PlayerObservation(
            self.player_state[player_index],
            self.discharge,
            [player_state.public_part() for player_state in self.player_state],
            self.moves_history,
        )

    def is_alive(self, player_index: int) -> bool:
        return bool(self.player_state[player_index].cards)

    def preexecute_action(self, action: Action) -> None:
        if action == ASSASSINATE:
            self.player_state[action.sender_index].add_coins(-3)

    def execute_action(self, action: Action) -> None:
        root, sender, victim = action.base(), action.sender_index, action.victim_index
        add_coins = self.player_state[sender].add_coins
        if victim and not self.is_alive(victim):
            Warning(f"You tried to {root} player number {victim}, but he is already dead")
            return
        if root == INCOME:
            add_coins(1)
        elif root == FOREIGN_AID:
            add_coins(2)
        elif root == COUP:
            add_coins(-7)
            self.kill_player(victim)
        elif root == TAX:
            add_coins(3)
        elif root == ASSASSINATE:
            add_coins(-3)
            self.kill_player(victim)
        elif root == STEAL:
            stealed_couns = min(self.player_state[victim].coins, 2)
            add_coins(stealed_couns)
            self.player_state[victim].add_coins(-stealed_couns)
        elif root == EXCHANGE:
            self.player_state[sender].add_cards(self.deck.pop2())
            self.kill_player(sender, put_card_to="deck")
            self.kill_player(sender, put_card_to="deck")
        else:
            raise ValueError(f"Action {action} with root {root} is not processed")


def other_players(n: int, player_index: int) -> Iterator[int]:
    return map(lambda k: k % n, range(player_index + 1, player_index + n))


def input_yes_or_not(inp: str) -> Literal["yes", "not"]:
    s = ""
    while s not in ["yes", "not"]:
        s = input(f"{inp} Input 'yes' or 'not'").lower()

    if s == "yes":
        return "yes"
    return "not"


def my_str(l: Any, indent: int = 4, already_indent: int = 0) -> str:
    if type(l) in [list, tuple]:
        if not l:
            print(l)
        rt = f"[\n"
        already_indent += indent
        for elem in l[0:]:
            rt += " " * already_indent + my_str(elem, indent, already_indent) + ",\n"
        rt += " " * (already_indent - indent) + "]"
    else :
        rt = str(l)
    return rt