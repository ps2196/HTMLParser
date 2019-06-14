import scanner

scan = scanner.Scanner('tests/map_config.html')

sym = scan.next_symbol()
while  sym is not None and sym.text != '':
    print("Symbol: ", sym.type, " ->>> ", sym.text)
    sym = scan.next_symbol()




