
def first_upper(s):
    if len(s) > 2:
        return s[:2].upper() + s[2:]
    return s

def get_cells(code, include_import_prefix):
    lines = [line for line in code.split('\n') if len(line) > 0]
    if include_import_prefix:
        lines = ['# Cell 1 - import libraries'] + lines
    else:
        first_line = '# ' + lines[0].strip() if not lines[0].strip().startswith('#') else lines[0].strip()
        lines = [first_line] + lines[1:]
    cells = []
    cur_cell = []
    for line in lines:
        if line.startswith('# Cell'):
            if len(cur_cell):
                cells.append('\n'.join(cur_cell))
            cur_cell = []

            cur_cell.append('#' + first_upper(''.join(line.split('-')[1:])))
        else:
            cur_cell.append(line)
    if len(cur_cell):
        cells.append('\n'.join(cur_cell))
    return [c for c in cells if len(c)]