import argparse
import brainer

parser = argparse.ArgumentParser(
    prog="Brainer Debugger",
    description="A simple Brainfuck interpreter and debugger"
)
parser.add_argument('-u','--user_input')
parser.add_argument('-b','--boring',action='store_false')
parser.add_argument('filenames',nargs='*')
args = parser.parse_args()

interactive = args.boring
input_file = (args.filenames or None,)[0] # TODO: allow for multiple files
user_input = list(args.user_input) if args.user_input else []
output = ''

def get_input(screen=None):
    global user_input
    if len(user_input) == 0:
        if screen:
            while True:
                screen.clear_buffer(Screen.COLOUR_DEFAULT, 0, Screen.COLOUR_DEFAULT, 0, 7, screen.width, screen.height)
                screen.print_at('Input: '+''.join(user_input), 0, 7, Screen.COLOUR_MAGENTA, 0, Screen.COLOUR_DEFAULT)
                screen.refresh()
                screen.wait_for_input(10)
                event = screen.get_event()
                if not type(event) == KeyboardEvent: continue
                elif event.key_code == 10 and len(user_input)>0: break
                elif event.key_code == Screen.KEY_BACK:
                    if len(user_input) > 0: user_input.pop()
                    continue
                elif not 32 <= event.key_code < 127: continue
                user_input.append(chr(event.key_code))
        else:
            user_input += list(input('Input: '))
        user_input.append(chr(0))
    return ord(user_input.pop(0))

def get_output(x):
    global output
    x = chr(x)
    output += x
    print(x,end='')

def debug_screen(program, screen, pause=False):
    screen.clear_buffer(Screen.COLOUR_DEFAULT, 0, Screen.COLOUR_DEFAULT)

    screen.print_at('Program:', 0, 0, Screen.COLOUR_DEFAULT, 0, Screen.COLOUR_DEFAULT)
    w = screen.width//6
    s = max(0,program.pc-w)
    for i in range(s,min(program.length, program.pc+w)):
        screen.print_at(program.instructions[i], (i-s)*2, 1, Screen.COLOUR_YELLOW if i == program.pc else Screen.COLOUR_DEFAULT, 1, Screen.COLOUR_DEFAULT)

    screen.print_at('Tape:', 0, 3, Screen.COLOUR_DEFAULT, 0, Screen.COLOUR_DEFAULT)
    for i in range(len(program.tape)):
        screen.print_at(f'[{program.tape[i]: >3}]', i*5, 4, Screen.COLOUR_CYAN if i == program.dp else Screen.COLOUR_DEFAULT, 1, Screen.COLOUR_DEFAULT)
        screen.print_at(f'({(chr(program.tape[i]) if 32 <= program.tape[i] < 127 else ' '): >3})', i*5, 5, Screen.COLOUR_CYAN if i == program.dp else Screen.COLOUR_DEFAULT, 1, Screen.COLOUR_DEFAULT)

    if output:
        screen.print_at('Output: ' + output, 0, 6, Screen.COLOUR_GREEN, 0, Screen.COLOUR_DEFAULT)

    screen.refresh()

    while pause:
        screen.wait_for_input(10)
        event = screen.get_event()
        if not type(event) == KeyboardEvent: continue
        if event.key_code == 10: break

def main(screen=None):
    if screen: screen.clear()

    raw_program = ''
    if input_file:
        with open(input_file[0]) as file:
            raw_program = file.read()
    else:
        raw_program = input('BF: ')
    program = brainer.Program(raw_program, lambda:get_input(screen), lambda x:get_output(x))

    try:
        while not program.at_end:
            if screen: debug_screen(program, screen, True)
            program.step()
        if screen: debug_screen(program, screen, True)
    except KeyboardInterrupt:
        print('\nExiting...')


if interactive:
    from asciimatics.screen import Screen
    from asciimatics.event import KeyboardEvent
    Screen.wrapper(main)
else:
    main()