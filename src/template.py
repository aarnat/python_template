import argparse
import logging
import signal
from pathlib import Path
from datetime import datetime


class tempy:
    # Variables #
    verbose = 0
    infile  = ""
    outfile = ""
    mode    = "print"
    writemode = "wb"
    reader  = None
    writer  = None

    # Methods #
    def __init__(self, infile_arg, outfile_arg, mode_arg,
                 append_arg, verbose_arg):
        # 1. Set Variables from the argument #
        self.verbose = verbose_arg
        self.mode    = mode_arg.lower()
        self.append  = append_arg

        # 2. Logger #
        self.setup_logger()
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level())

        # 3. File Path related #
        self.set_infile(infile_arg)
        self.set_outfile(outfile_arg)

        # 4. Critical Error Checking #
        if (self.infile == self.outfile):
            raise FileExistsError("Input file and Output file are the same.")

        if (not(self.append) and self.outfile.exists()):
            self.confirm("Overwrite?")

        # 5. Create reader and writer #
        # -reader #
        try:
            self.reader = open(self.out_file)
        except Exception as e:
            logger.error("Reader Creation Failed: {}".format(e))
            exit()

        # -writer #
        if (self.mode == "write"):
            if (self.append):
                self.write_mode = "ab"
            try:
                self.writer = open(self.outfile, self.write_mode)
            except Exception as e:
                logger.error("Writer Creation Failed: {}".format(e))
        return


    def shutdown(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level())

        if (self.reader is not None):
            try:
                self.reader.close()
            except Exception as e:
                logger.error("Closing reader failed: {}".format(e))

        if (self.writer is not None):
            try:
                self.writer.close()
            except Exception as e:
                logger.error("Closing writer failed: {}".format(e))

        exit()
        return


    def setup_logger(self):
        # Time related stuff for naming uses #
        now = datetime.now()
        date = now.strftime("%m%d")
        dateTime = now.strftime("%m%d%H%M%S")

        # Create filename/filepath #
        script = Path(__file__).parents[1]
        logpath = script.joinpath("log", date)
        Path.mkdir(logpath, parents=True, exist_ok=True)
        logFile = logpath.joinpath("{}.log".format(dateTime))

        # Create the log file Formatter & Handler #
        rootLogger = logging.getLogger()
        fileHandler = logging.FileHandler(logFile)
        fmtStr = "%(asctime)s [%(levelname)-5.5s]  %(message)s"
        logFormatter = logging.Formatter(fmtStr)
        fileHandler.setFormatter(logFormatter)

        # Create the console Formatter & Handler #
        consoleHandler = logging.StreamHandler()
        consoleFormatter = logging.Formatter("%(message)s")
        consoleHandler.setFormatter(consoleFormatter)

        # Add the log file logger and console logger to the root logger #
        rootLogger.addHandler(fileHandler)
        rootLogger.addHandler(consoleHandler)

        return


    def log_level(self):
        level = logging.INFO
        if (self.verbose > 0):
            level = logging.DEBUG
        return level


    def set_infile(self, infile_arg):
        pathInFile = Path(infile_arg)
        if (pathInFile.is_file()):
            self.infile = pathInFile.resolve()
        else:
            raise FileNotFoundError

        return

    def set_outfile(self):
        # TODO
        return


    def confirm(self, confirm_str, count_limit=3):
        count = 0
        ask = True

        while ask:
            raw = input("{} (y/n): ".format(confirm_str)).lower()
            if raw in ["no", "n", "q"]:
                exit()
            if raw in ["yes", "y"]:
                ask = False
            count = count + 1
            if (count >= count_limit):
                exit()

        return


# Global Scope #

def graceful_shutdown(signum):
    return

if __name__ == "__main__":
    # TODO: Make windows and Linux Checker for signals
    signal.signal(signal.SIGHUP, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    # signal.signal(signal.SIGKILL, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    ap = argparse.ArgumentParser(description="tempy.py", epilog="")
    ap.add_argument("mode", choice=["print"],
                    help="Mode to run tool in")
    ap.add_argument("infile", type=str, help="File to read")
    ap.add_argument("-o", "--outfile", type=str, default="",
                    help="File to write to")
    ap.add_argument("-v", "--verbose", type=int, defauilt=0, action="count",
                    help="Verbosity level, more v's = more debug")
    ap.add_argument("-a", "--append", action="store_true",
                    help="Use the writer in appended mode")

    args = ap.parse_args()

    tp = tempy(args.infile, args.outfile, args.mode,
               args.append, args.verbose)

    tp.shutdown()
