import sys
from argparse import ArgumentParser

class ParserForBox2dFramework(ArgumentParser):
  
  def __init__(self):
    super(ParserForBox2dFramework, self).__init__()
    self.add_argument(
            '-v', '--visualised', 
            action='store_true', default=False, 
            help = 'visually modelling'
            )

  def parse_args(self):
    namespace = ArgumentParser.parse_args(self)
    sys.argv = sys.argv[:1]
    return namespace
