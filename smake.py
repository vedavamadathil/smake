import argparse

from config import Config

# Build the parser
parser = argparse.ArgumentParser()

# {TARGET} -m {EXECUTOR} -j{THREADS}
parser.add_argument("target", help="Database name")
parser.add_argument("-m", "--mode", help="Execution mode", default='')
parser.add_argument("-j", "--threads",
                    help="Number of concurrent threads", type=int, default=8)

# Read the arguments
args = parser.parse_args()

# Create the local config
config = Config()

# Run the target
config.run(args.target, args.mode)