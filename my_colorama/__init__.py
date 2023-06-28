from colorama import init, Fore, Back, Style

init()  # initialize the colorama package

# print message in a specified color
def msg(color, message):
  import inspect
  print("%s%s%s" % (color, message, Style.RESET_ALL ))
  # print("%s.%s > %s %s %s" % (__name__, inspect.currentframe().f_back.f_code.co_name, color, message, Style.RESET_ALL ))

# print message in RED
def red(message):
  msg(Fore.RED, message)

# print message in BLUE
def blue(message):
  msg(Fore.BLUE, message)

# print message in YELLOW
def yellow(message):
  msg(Fore.YELLOW, message)

# print message in CYAN
def cyan(message):
  msg(Fore.CYAN, message)

# switch to LIGHTCYAN_EX background, or RESET
def code(toggle):
  if toggle:
    print(Back.LIGHTCYAN_EX)
  else:
    print(Back.RESET)