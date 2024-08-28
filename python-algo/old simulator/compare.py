import json

with open('sim_results.txt') as f:
    lines = [line.rstrip() for line in f]

with open('official_result.txt') as f:
    lines = [line.rstrip() for line in f]

# Sort units within each type
def sort_units(units):
    # Sort by X coordinate, then by Y coordinate, then by health
    return sorted(units, key=lambda unit: (unit[0], unit[1], unit[2]))

# Sort all unit lists in the game state
def sort_all_units(units):
    return [sort_units(unit_list) for unit_list in units]

# Compare two game states and ensure they are the same
def same_game_state(gs1: str, gs2: str) -> bool:
    gs1 = json.loads(gs1)
    gs2 = json.loads(gs2)

    # Compare p1Stats and p2Stats (assuming the first element is what needs to be checked)
    if gs1["p1Stats"][0] != gs2["p1Stats"][0] or gs1["p2Stats"][0] != gs2["p2Stats"][0]: 
        return False

    # Sort units before comparison
    gs1_sorted_units = sort_all_units(gs1["p1Units"])
    gs2_sorted_units = sort_all_units(gs2["p1Units"])

    # Compare p1Units
    for i in range(8):
        if gs1_sorted_units[i] != gs2_sorted_units[i]:
            return False

    # Repeat the process for p2Units
    gs1_sorted_units = sort_all_units(gs1["p2Units"])
    gs2_sorted_units = sort_all_units(gs2["p2Units"])

    for i in range(8):
        if gs1_sorted_units[i] != gs2_sorted_units[i]:
            return False

    return True
