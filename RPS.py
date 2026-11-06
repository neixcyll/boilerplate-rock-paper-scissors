# Player for freeCodeCamp Rock Paper Scissors.
# Ensemble of predictors guesses the opponent's next
# move, then we play the move that beats it. Each
# predictor is scored on past predictions in the
# current match; the best-scoring predictor
# (Laplace-smoothed) is followed. State resets
# whenever prev_play == "" (first move of a match).
from collections import Counter
BEATS = {"R": "P", "P": "S", "S": "R"}
_state = {"opp": [], "mine": [], "scores": {}, "last": {}}


def _most_frequent(seq):
    if not seq:
        return None
    counts = Counter(seq)
    best = None
    best_count = -1
    for move in seq:
        if counts[move] > best_count:
            best = move
            best_count = counts[move]
    return best


def _markov_next(history, context, target):
    if not context or len(history) < len(context) + 1:
        return None
    k = len(context)
    counts = Counter()
    for i in range(len(history) - k):
        if tuple(history[i:i + k]) == tuple(context):
            counts[target[i + k]] += 1
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def _predictions(opp, mine):
    preds = {}
    if len(opp) >= 5:
        preds["quincy5"] = opp[-5]
    for k in (1, 2, 3, 4, 5):
        if len(opp) >= k:
            p = _markov_next(opp, opp[-k:], opp)
            if p:
                preds["opp_markov%d" % k] = p
    for k in (1, 2, 3):
        if len(mine) >= k:
            p = _markov_next(mine, mine[-k:], opp)
            if p:
                preds["my_markov%d" % k] = p
    if len(mine) >= 2 and len(opp) >= 2:
        pairs = list(zip(mine, opp))
        p = _markov_next(pairs, pairs[-2:], opp)
        if p:
            preds["joint2"] = p
    if mine:
        preds["kris"] = BEATS[mine[-1]]
        freq = _most_frequent(mine[-10:])
        if freq:
            preds["mrugesh"] = BEATS[freq]
        nxt = _markov_next(mine, mine[-1:], mine)
        if nxt:
            preds["abbey"] = BEATS[nxt]
    if opp:
        preds["opp_freq"] = _most_frequent(opp[-20:])
        preds["opp_last"] = opp[-1]
    return preds


def player(prev_play, opponent_history=[]):
    if prev_play == "":
        _state["opp"] = []
        _state["mine"] = []
        _state["scores"] = {}
        _state["last"] = {}
        guess = "R"
        _state["mine"].append(guess)
        return guess
    opp = _state["opp"]
    mine = _state["mine"]
    scores = _state["scores"]
    for name, pred in _state["last"].items():
        correct, total = scores.get(name, [0, 0])
        scores[name] = [correct + (1 if pred == prev_play else 0), total + 1]
    opp.append(prev_play)
    preds = _predictions(opp, mine)
    priority = ["quincy5", "opp_markov5", "opp_markov4"]
    priority += ["joint2", "my_markov3", "my_markov2"]
    priority += ["opp_markov3", "abbey", "mrugesh"]
    priority += ["kris", "opp_markov2", "my_markov1"]
    priority += ["opp_markov1", "opp_freq", "opp_last"]
    best_name = None
    best_score = -1.0
    for name in priority:
        if name not in preds:
            continue
        correct, total = scores.get(name, [0, 0])
        if total < 2:
            continue
        smoothed = (correct + 1) / (total + 3)
        if smoothed > best_score:
            best_score = smoothed
            best_name = name
    if best_name is None:
        predicted = _most_frequent(opp)
    else:
        predicted = preds[best_name]
    guess = BEATS[predicted] if predicted in BEATS else "R"
    _state["last"] = preds
    mine.append(guess)
    return guess
