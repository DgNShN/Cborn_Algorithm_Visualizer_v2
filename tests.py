from algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    linear_search,
    binary_search,
)


def run_algorithm(algorithm, data, target=None):
    last_state = None
    if target is None:
        for step in algorithm(data):
            last_state = step
    else:
        for step in algorithm(data, target):
            last_state = step
    return last_state


def main():
    sample = [5, 3, 8, 1, 2, 7]

    print("Original:", sample)
    print("Bubble:", run_algorithm(bubble_sort, sample)["data"])
    print("Selection:", run_algorithm(selection_sort, sample)["data"])
    print("Insertion:", run_algorithm(insertion_sort, sample)["data"])
    print("Merge:", run_algorithm(merge_sort, sample)["data"])
    print("Quick:", run_algorithm(quick_sort, sample)["data"])

    print("Linear Search:", run_algorithm(linear_search, sample, 8)["message"])
    print("Binary Search:", run_algorithm(binary_search, sample, 8)["message"])


if __name__ == "__main__":
    main()