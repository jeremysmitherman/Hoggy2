import sys
sys.path.append("..")
import Hoggy2
import Hoggy2.utils
from utils.HoggyLogger import HoggyLogger

log = HoggyLogger(__name__, Hoggy2.config.get('hoggy', 'logfile'))

def main():
    Hoggy2.hoggy_web.debug = True
    Hoggy2.hoggy_web.run(host="0.0.0.0", port=8090)

if __name__ == "__main__":
    main()
