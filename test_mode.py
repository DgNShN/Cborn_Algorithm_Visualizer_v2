SORTING_TEST_DATA = [5, 3, 8, 1, 2, 7, 4, 6]
SEARCH_TEST_DATA = [2, 5, 8, 12, 16, 23, 38, 45, 57, 71]
DEFAULT_SEARCH_TARGET_VALUE = 23


def get_test_data(algorithm_type, algorithm_name):
    if algorithm_type == "searching":
        return SEARCH_TEST_DATA[:]
    return SORTING_TEST_DATA[:]


def get_default_target():
    return DEFAULT_SEARCH_TARGET_VALUE


def validate_algorithm_result(algorithm_name, final_state, original_data, target=None):
    if not final_state:
        return False, "No final state produced."

    final_data = final_state.get("data", [])
    found_indices = final_state.get("found_indices", [])

    sorting_algorithms = {
        "Bubble Sort",
        "Selection Sort",
        "Insertion Sort",
        "Merge Sort",
        "Quick Sort",
    }

    searching_algorithms = {
        "Linear Search",
        "Binary Search",
    }

    if algorithm_name in sorting_algorithms:
        expected = sorted(original_data)
        if final_data == expected:
            return True, f"Validation passed. Final array is correctly sorted: {final_data}"
        return False, f"Validation failed. Expected {expected}, got {final_data}"

    if algorithm_name in searching_algorithms:
        if target is None:
            return False, "Validation failed. Search target is missing."

        if algorithm_name == "Binary Search":
            expected_data = sorted(original_data)
            if final_data != expected_data:
                return False, f"Validation failed. Binary Search data should be sorted: expected {expected_data}, got {final_data}"

            if target in expected_data:
                expected_index = expected_data.index(target)
                if found_indices and found_indices[0] == expected_index:
                    return True, f"Validation passed. Target {target} found at correct index {expected_index}."
                return False, f"Validation failed. Expected target {target} at index {expected_index}, got {found_indices}"
            else:
                if not found_indices:
                    return True, f"Validation passed. Target {target} correctly reported as not found."
                return False, f"Validation failed. Target {target} should not be found, but got {found_indices}"

        if algorithm_name == "Linear Search":
            if target in original_data:
                expected_index = original_data.index(target)
                if found_indices and found_indices[0] == expected_index:
                    return True, f"Validation passed. Target {target} found at correct index {expected_index}."
                return False, f"Validation failed. Expected target {target} at index {expected_index}, got {found_indices}"
            else:
                if not found_indices:
                    return True, f"Validation passed. Target {target} correctly reported as not found."
                return False, f"Validation failed. Target {target} should not be found, but got {found_indices}"

    return False, f"Unknown algorithm type for validation: {algorithm_name}"


# ==================== BROKEN TEST FILES ====================

BROKEN_TEST_FILES = {
    "broken_syntax.py": '''
def run(data):
    arr = data[:]
    if len(arr) > 0  # HATA: missing colon
        arr[0] = 5
    return [{"data": arr[:], "message": "Done"}]
''',

    "broken_import.py": '''
import os  # HATA: forbidden import!

def run(data):
    os.system("echo test")
    return [{"data": data[:], "message": "Done"}]
''',

    "broken_undefined.py": '''
def run(data):
    arr = data[:]
    x = undefined_variable + 1  # HATA: undefined variable
    return [{"data": arr[:], "message": "Done"}]
''',

    "broken_infinite.py": '''
def run(data):
    arr = data[:]
    i = 0
    while True:  # HATA: infinite loop!
        i += 1
    return [{"data": arr[:], "message": "Done"}]
''',
}


def get_broken_test_file(filename):
    """Return broken test file content"""
    return BROKEN_TEST_FILES.get(filename, None)


def list_broken_test_files():
    """List all available broken test files"""
    return list(BROKEN_TEST_FILES.keys())