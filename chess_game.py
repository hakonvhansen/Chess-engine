import chess
import math

class Game:
    def initial_state(self) -> chess.Board:
        return chess.Board()

    def to_move(self, state: chess.Board) -> int:
        return 0 if state.turn == chess.WHITE else 1

    def actions(self, state: chess.Board) -> list[chess.Move]:
        return list(state.legal_moves)

    def result(self, state: chess.Board, action: chess.Move) -> chess.Board:
        next_state = state.copy()      # don't mutate the parent state
        next_state.push(action)
        return next_state

    def is_terminal(self, state: chess.Board) -> bool:
        return state.is_game_over()

    def utility(self, state: chess.Board, player: int) -> float:
        winner = state.outcome().winner       # True = white, False = black, None = draw
        if winner is None:
            return 0
        winner_index = 0 if winner == chess.WHITE else 1
        return 1000 if winner_index == player else -1000

    def evaluate(self, state: chess.Board, player: int) -> float:
        """Heuristic for non-terminal positions: material balance."""
        values = {chess.PAWN: 1, chess.KNIGHT: 3.3, chess.BISHOP: 3.5,
                  chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        score = 0
        for piece in state.piece_map().values():
            v = values[piece.piece_type]
            score += v if piece.color == chess.WHITE else -v
        return score if player == 0 else -score   

    
def alpha_beta_search(game, state, depth=3):
    global player
    player = game.to_move(state)
    value, move = MAX_VALUE_AB(game, state, -math.inf, math.inf, depth)
    return move

def MAX_VALUE_AB(game, state, alpha, beta, depth):
    if game.is_terminal(state):
        return game.utility(state, player), None
    if depth == 0:                                   # cutoff test
        return game.evaluate(state, player), None
    v, move = -math.inf, None
    for a in game.actions(state):
        v2, a2 = MIN_VALUE_AB(game, game.result(state, a), alpha, beta, depth - 1)
        if v2 > v:
            v, move = v2, a
            alpha = max(alpha, v)
        if v >= beta:
            return v, move
    return v, move

def MIN_VALUE_AB(game, state, alpha, beta, depth):
    if game.is_terminal(state):
        return game.utility(state, player), None
    if depth == 0:
        return game.evaluate(state, player), None
    v, move = math.inf, None
    for a in game.actions(state):
        v2, a2 = MAX_VALUE_AB(game, game.result(state, a), alpha, beta, depth - 1)
        if v2 < v:
            v, move = v2, a
            beta = min(beta, v)
        if v <= alpha:
            return v, move
    return v, move


def play_human_vs_engine(depth: int = 3):
    game = Game()
    state = game.initial_state()

    choice = input("Play as white or black? [w/b]: ").strip().lower()
    human = 0 if choice != 'b' else 1   # 0 = white, 1 = black

    print(state, '\n')
    while not game.is_terminal(state):
        if game.to_move(state) == human:
            # Human's turn
            text = input("Your move (e.g. e4, Nf3, e2e4, or 'quit'): ").strip()
            if text.lower() in ('quit', 'q', 'exit'):
                print("Game abandoned.")
                return
            try:
                try:
                    move = state.parse_san(text)    # e.g. Nf3, e4, O-O
                except ValueError:
                    move = state.parse_uci(text)    # e.g. g1f3
            except ValueError:
                print("Invalid or illegal move, try again.")
                print("Legal moves:", ', '.join(state.san(m) for m in game.actions(state)))
                continue
        else:
            # Engine's turn
            print("Engine is thinking...")
            move = alpha_beta_search(game, state, depth)
            print(f"Engine plays {state.san(move)}")   # must be called before the move is pushed

        state = game.result(state, move)
        print(state, '\n')

    outcome = state.outcome()
    if outcome.winner is None:
        print(f"Draw ({outcome.termination.name.lower()})")
    elif (0 if outcome.winner == chess.WHITE else 1) == human:
        print("You won!")
    else:
        print("The engine won.")


if __name__ == '__main__':
    play_human_vs_engine(depth=3)