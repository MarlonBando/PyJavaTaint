class Tainted_var:


  __value: int|str|bool
  __tainted: bool


  def __init__(self, value, tainted=False):

    self.__value = value
    self.__tainted = tainted


  def __repr__(self):

    RED_COLOR = '\033[91m'
    GREEN_COLOR = '\033[92m'
    END = '\033[0m'

    if self.__tainted:
      return f"{RED_COLOR}{self.__value}{END}"
    else:
      return f"{GREEN_COLOR}{self.__value}{END}"
    
  def __add__(self, other: Tainted_var):

    if type(self.__value) == type(other.__value):
      new_value = self.__value + other.__value
      new_taint = self.__tainted or other.__tainted
      return Tainted_var(new_value, tainted=new_taint)
    else:
      raise TypeError('To add 2 tainted variables they must have the same type')