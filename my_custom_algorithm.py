CUSTOM_META = {
    "overview": "Simple custom swap demo.",
    "why": "Shows that custom states can be replayed safely.",
    "best": "O(n)",
    "average": "O(n²)",
    "worst": "O(n²)",
    "space": "O(1)",
}

def run(data):
    states = []

    arr = data[:]

    states.append({
        "data": arr[:],
        "message": "Initial state",
        "active": [0, 1],
        "variables": {"i": 0, "j": 1},
        "stats": {"steps": 1, "comparisons": 0, "swaps": 0},
    })

    if len(arr) >= 2 and arr[0] > arr[1]:
        arr[0], arr[1] = arr[1], arr[0]
        states.append({
            "data": arr[:],
            "message": "Swapped first two values",
            "swap": [0, 1],
            "variables": {"i": 0, "j": 1},
            "stats": {"steps": 2, "comparisons": 1, "swaps": 1},
        })

    states.append({
        "data": arr[:],
        "message": "Custom run finished",
        "sorted_indices": list(range(len(arr))),
        "stats": {"steps": 3, "comparisons": 1, "swaps": 1},
    })

    return states