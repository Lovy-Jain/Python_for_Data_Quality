import cProfile
import time


def slow_function():
    time.sleep(1)
    return "Slow operation completed"


def fast_function():
    return "Fast operation completed"


def main():
    # Some operations to profile
    for i in range(3):
        slow_function()
        fast_function()


if __name__ == '__main__':
    # Run profiler on the main function
    profiler = cProfile.Profile()
    profiler.enable()

    main()  # Execute the code to profile

    profiler.disable()
    profiler.print_stats(sort='cumulative')