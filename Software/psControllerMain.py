import PsController.PsController
import argparse

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--debug', help='Run in debug mode', action='store_true')
    args = parser.parse_args()
    isDebugMode = args.debug
    PsController.PsController.run(isDebugMode)

if __name__ == "__main__":
    run()
