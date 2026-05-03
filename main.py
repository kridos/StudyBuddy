import warnings

warnings.filterwarnings("ignore", message=".*SymbolDatabase.GetPrototype\(\) is deprecated.*")

from studybuddy.ui import run


if __name__ == "__main__":
    run()
