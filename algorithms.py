ALGORITHM_INFO = {
    "Bubble Sort": {
        "type": "sorting",
        "best": "O(n)",
        "average": "O(n²)",
        "worst": "O(n²)",
        "space": "O(1)",
        "code": """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break"""
    },
    "Selection Sort": {
        "type": "sorting",
        "best": "O(n²)",
        "average": "O(n²)",
        "worst": "O(n²)",
        "space": "O(1)",
        "code": """def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]"""
    },
    "Insertion Sort": {
        "type": "sorting",
        "best": "O(n)",
        "average": "O(n²)",
        "worst": "O(n²)",
        "space": "O(1)",
        "code": """def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key"""
    },
    "Merge Sort": {
        "type": "sorting",
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "space": "O(n)",
        "code": """def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)"""
    },
    "Quick Sort": {
        "type": "sorting",
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n²)",
        "space": "O(log n)",
        "code": """def quick_sort(arr, low, high):
    if low < high:
        pivot_index = partition(arr, low, high)
        quick_sort(arr, low, pivot_index - 1)
        quick_sort(arr, pivot_index + 1, high)"""
    },
    "Linear Search": {
        "type": "searching",
        "best": "O(1)",
        "average": "O(n)",
        "worst": "O(n)",
        "space": "O(1)",
        "code": """def linear_search(arr, target):
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1"""
    },
    "Binary Search": {
        "type": "searching",
        "best": "O(1)",
        "average": "O(log n)",
        "worst": "O(log n)",
        "space": "O(1)",
        "code": """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""
    },
}


def build_state(
    data,
    message="",
    active=None,
    swap=None,
    sorted_indices=None,
    found_indices=None,
    variables=None,
    stats=None,
):
    return {
        "data": data[:],
        "message": message,
        "active": active[:] if active else [],
        "swap": swap[:] if swap else [],
        "sorted_indices": sorted_indices[:] if sorted_indices else [],
        "found_indices": found_indices[:] if found_indices else [],
        "variables": variables.copy() if variables else {},
        "stats": stats.copy() if stats else {"steps": 0, "comparisons": 0, "swaps": 0},
    }


def bubble_sort(data):
    arr = data[:]
    n = len(arr)
    steps = comparisons = swaps = 0

    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            comparisons += 1
            steps += 1
            yield build_state(
                arr,
                message=f"Comparing index {j} and {j + 1}",
                active=[j, j + 1],
                sorted_indices=list(range(n - i, n)),
                variables={"i": i, "j": j},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
                steps += 1
                yield build_state(
                    arr,
                    message=f"Swapped {arr[j]} and {arr[j + 1]}",
                    active=[j, j + 1],
                    swap=[j, j + 1],
                    sorted_indices=list(range(n - i, n)),
                    variables={"i": i, "j": j},
                    stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
                )

        steps += 1
        yield build_state(
            arr,
            message=f"Index {n - i - 1} fixed",
            sorted_indices=list(range(n - i - 1, n)),
            variables={"i": i},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

        if not swapped:
            steps += 1
            yield build_state(
                arr,
                message="Array already sorted",
                sorted_indices=list(range(n)),
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )
            return

    steps += 1
    yield build_state(
        arr,
        message="Bubble Sort completed",
        sorted_indices=list(range(n)),
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )


def selection_sort(data):
    arr = data[:]
    n = len(arr)
    steps = comparisons = swaps = 0

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            steps += 1
            yield build_state(
                arr,
                message=f"Checking index {j} against current min {min_idx}",
                active=[min_idx, j],
                sorted_indices=list(range(i)),
                variables={"i": i, "j": j, "min_idx": min_idx},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

            if arr[j] < arr[min_idx]:
                min_idx = j
                steps += 1
                yield build_state(
                    arr,
                    message=f"New minimum found at index {min_idx}",
                    active=[i, min_idx],
                    sorted_indices=list(range(i)),
                    variables={"i": i, "j": j, "min_idx": min_idx},
                    stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
                )

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
            steps += 1
            yield build_state(
                arr,
                message=f"Swapped index {i} and {min_idx}",
                active=[i, min_idx],
                swap=[i, min_idx],
                sorted_indices=list(range(i)),
                variables={"i": i, "min_idx": min_idx},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

        steps += 1
        yield build_state(
            arr,
            message=f"Index {i} fixed",
            sorted_indices=list(range(i + 1)),
            variables={"i": i},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

    steps += 1
    yield build_state(
        arr,
        message="Selection Sort completed",
        sorted_indices=list(range(n)),
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )


def insertion_sort(data):
    arr = data[:]
    n = len(arr)
    steps = comparisons = swaps = 0

    if n == 0:
        yield build_state(arr, message="Empty array")
        return

    steps += 1
    yield build_state(
        arr,
        message="First element is considered sorted",
        sorted_indices=[0],
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )

    for i in range(1, n):
        key = arr[i]
        j = i - 1

        steps += 1
        yield build_state(
            arr,
            message=f"Trying to insert value {key}",
            active=[i],
            sorted_indices=list(range(i)),
            variables={"i": i, "j": j, "key": key},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

        while j >= 0:
            comparisons += 1
            steps += 1
            yield build_state(
                arr,
                message=f"Comparing {arr[j]} and key {key}",
                active=[j, j + 1],
                sorted_indices=list(range(i)),
                variables={"i": i, "j": j, "key": key},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

            if arr[j] > key:
                arr[j + 1] = arr[j]
                swaps += 1
                steps += 1
                yield build_state(
                    arr,
                    message=f"Shifting value from index {j} to {j + 1}",
                    active=[j, j + 1],
                    swap=[j, j + 1],
                    sorted_indices=list(range(i)),
                    variables={"i": i, "j": j, "key": key},
                    stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
                )
                j -= 1
            else:
                break

        arr[j + 1] = key
        steps += 1
        yield build_state(
            arr,
            message=f"Inserted key at index {j + 1}",
            active=[j + 1],
            sorted_indices=list(range(i + 1)),
            variables={"i": i, "j": j, "key": key},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

    steps += 1
    yield build_state(
        arr,
        message="Insertion Sort completed",
        sorted_indices=list(range(n)),
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )


def merge_sort(data):
    arr = data[:]
    steps = comparisons = swaps = 0

    def merge_sort_recursive(left, right):
        nonlocal steps, comparisons, swaps, arr

        if left >= right:
            return

        mid = (left + right) // 2
        steps += 1
        yield build_state(
            arr,
            message=f"Splitting range {left}-{right} at mid {mid}",
            active=[left, mid, right],
            variables={"left": left, "mid": mid, "right": right},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

        yield from merge_sort_recursive(left, mid)
        yield from merge_sort_recursive(mid + 1, right)

        temp = []
        i, j = left, mid + 1

        while i <= mid and j <= right:
            comparisons += 1
            steps += 1
            yield build_state(
                arr,
                message=f"Comparing left[{i}] and right[{j}]",
                active=[i, j],
                variables={"left": left, "mid": mid, "right": right, "i": i, "j": j},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

            if arr[i] <= arr[j]:
                temp.append(arr[i])
                i += 1
            else:
                temp.append(arr[j])
                j += 1

        while i <= mid:
            temp.append(arr[i])
            i += 1

        while j <= right:
            temp.append(arr[j])
            j += 1

        for idx, value in enumerate(temp):
            arr[left + idx] = value
            swaps += 1
            steps += 1
            yield build_state(
                arr,
                message=f"Writing merged value at index {left + idx}",
                swap=[left + idx],
                active=[left + idx],
                variables={"left": left, "mid": mid, "right": right},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

        steps += 1
        yield build_state(
            arr,
            message=f"Merged range {left}-{right}",
            sorted_indices=list(range(left, right + 1)),
            variables={"left": left, "mid": mid, "right": right},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

    if len(arr) == 0:
        yield build_state(arr, message="Empty array")
        return

    yield from merge_sort_recursive(0, len(arr) - 1)

    steps += 1
    yield build_state(
        arr,
        message="Merge Sort completed",
        sorted_indices=list(range(len(arr))),
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )


def quick_sort(data):
    arr = data[:]
    steps = comparisons = swaps = 0

    def quick_sort_recursive(low, high):
        nonlocal steps, comparisons, swaps, arr

        if low >= high:
            if 0 <= low < len(arr):
                steps += 1
                yield build_state(
                    arr,
                    message=f"Single element at index {low} is placed",
                    sorted_indices=[low],
                    variables={"low": low, "high": high},
                    stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
                )
            return

        pivot = arr[high]
        i = low - 1

        steps += 1
        yield build_state(
            arr,
            message=f"Pivot selected: index {high}, value {pivot}",
            active=[high],
            variables={"low": low, "high": high, "pivot": pivot, "pivot_index": high},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

        for j in range(low, high):
            comparisons += 1
            steps += 1
            yield build_state(
                arr,
                message=f"Comparing arr[{j}] with pivot {pivot}",
                active=[j, high],
                variables={"low": low, "high": high, "j": j, "i": i, "pivot": pivot, "pivot_index": high},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

            if arr[j] <= pivot:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps += 1
                    steps += 1
                    yield build_state(
                        arr,
                        message=f"Swapped index {i} and {j}",
                        active=[i, j],
                        swap=[i, j],
                        variables={"low": low, "high": high, "j": j, "i": i, "pivot": pivot, "pivot_index": high},
                        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
                    )

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        swaps += 1
        pivot_index = i + 1
        steps += 1
        yield build_state(
            arr,
            message=f"Placed pivot at index {pivot_index}",
            active=[pivot_index],
            swap=[pivot_index, high],
            sorted_indices=[pivot_index],
            variables={"low": low, "high": high, "pivot": pivot, "pivot_index": pivot_index},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

        yield from quick_sort_recursive(low, pivot_index - 1)
        yield from quick_sort_recursive(pivot_index + 1, high)

    if len(arr) == 0:
        yield build_state(arr, message="Empty array")
        return

    yield from quick_sort_recursive(0, len(arr) - 1)

    steps += 1
    yield build_state(
        arr,
        message="Quick Sort completed",
        sorted_indices=list(range(len(arr))),
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )


def linear_search(data, target):
    arr = data[:]
    steps = comparisons = swaps = 0

    for i, value in enumerate(arr):
        comparisons += 1
        steps += 1
        yield build_state(
            arr,
            message=f"Checking index {i} for target {target}",
            active=[i],
            variables={"i": i, "target": target, "value": value},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

        if value == target:
            steps += 1
            yield build_state(
                arr,
                message=f"Target {target} found at index {i}",
                active=[i],
                found_indices=[i],
                variables={"i": i, "target": target, "value": value},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )
            return

    steps += 1
    yield build_state(
        arr,
        message=f"Target {target} not found",
        variables={"target": target},
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )


def binary_search(data, target):
    arr = sorted(data[:])
    steps = comparisons = swaps = 0
    left, right = 0, len(arr) - 1

    steps += 1
    yield build_state(
        arr,
        message="Binary Search requires sorted data. Data sorted automatically.",
        variables={"left": left, "right": right, "target": target},
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )

    while left <= right:
        mid = (left + right) // 2
        comparisons += 1
        steps += 1
        yield build_state(
            arr,
            message=f"Checking middle index {mid}",
            active=[left, mid, right] if left != right else [mid],
            variables={"left": left, "mid": mid, "right": right, "target": target, "value": arr[mid]},
            stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
        )

        if arr[mid] == target:
            steps += 1
            yield build_state(
                arr,
                message=f"Target {target} found at index {mid}",
                active=[mid],
                found_indices=[mid],
                variables={"left": left, "mid": mid, "right": right, "target": target, "value": arr[mid]},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )
            return
        elif arr[mid] < target:
            left = mid + 1
            steps += 1
            yield build_state(
                arr,
                message=f"Target is greater than {arr[mid]}, moving right",
                active=[mid],
                variables={"left": left, "mid": mid, "right": right, "target": target},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )
        else:
            right = mid - 1
            steps += 1
            yield build_state(
                arr,
                message=f"Target is smaller than {arr[mid]}, moving left",
                active=[mid],
                variables={"left": left, "mid": mid, "right": right, "target": target},
                stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
            )

    steps += 1
    yield build_state(
        arr,
        message=f"Target {target} not found",
        variables={"left": left, "right": right, "target": target},
        stats={"steps": steps, "comparisons": comparisons, "swaps": swaps},
    )


ALGORITHMS = {
    "Bubble Sort": bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Linear Search": linear_search,
    "Binary Search": binary_search,
}