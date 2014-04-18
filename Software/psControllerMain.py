import PsController.PsController
import argparse


def run():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--debug', help='Run in debug mode', action='store_true')
        parser.add_argument('-p', '--port', help='Force a connection to certain usb port')
        args = parser.parse_args()
        isDebugMode = args.debug
        forcedUsbPort = args.port
        PsController.PsController.run(isDebugMode, forcedUsbPort)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()
