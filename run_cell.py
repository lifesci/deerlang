from collections import namedtuple
from direction_help import direction_offsets
from ir import meta, cell as cell_def, aliases, alias_selectors, selectors, rules
from time import sleep

DEFAULT_ROWS = 20
DEFAULT_COLS = 80

class InvalidAliasException(Exception):
  pass

class Simulation:
  def matchcount(self, dirs, selector, cell): 
    count = 0
    for deer in dirs:
      row_diff, col_diff = direction_offsets[deer]
      row = cell.row + row_diff
      col = cell.col + col_diff
      if 0 <= row < self.rows and 0 <= col < self.cols:
        comp_cell = self.grid[row][col]
        if selector(self.selectors, comp_cell, self.builtins):
          count += 1
    return count

  def build_grid(self):
    self.grid = []
    for i in range(self.rows):
      row = []
      self.grid.append(row)
      for j in range(self.cols):
        row.append(self.cell._replace(row=i, col=j))

  def build_next_grid(self):
    self.next_grid = []
    for i in range(self.rows):
      row = []
      self.next_grid.append(row)
      for j in range(self.cols):
        row.append(None)

  def build_builtins(self):
    self.builtins = {
      "matchcount": self.matchcount,
    }

  def __init__(self):
    self.rows = meta.get("Rows", DEFAULT_ROWS)
    self.cols = meta.get("Cols", DEFAULT_COLS)
    cell_def.update({"row": 0, "col": 0})
    cell_template = namedtuple("Cell", cell_def)
    self.cell = cell_template(**cell_def)
    self.selectors = selectors
    self.aliases = aliases
    self.alias_selectors = alias_selectors
    self.build_builtins()
    self.rules = rules
    self.build_grid()

  def get_meta(self):
    return {
      "rows": self.rows,
      "cols": self.cols,
    }

  def _match_alias(self, cell):
    for selector in self.alias_selectors:
      if selector.func(cell):
        return selector.name
    return None

  def get_frame(self):
    frame = []
    for row in self.grid:
      frame_row = []
      frame.append(frame_row)
      for cell in row:
        alias = self._match_alias(cell)
        frame_row.append(alias)
    return frame

  # TODO this is actually really tricky, maybe removing should only be allowed before starting the simulation
  def remove(self, row, col):
    new_cell = self.cell._replace(row=row, col=col)
    self.grid[row][col] = new_cell

  def update(self, row, col, alias):
    try:
      props = self.aliases[alias]
    except KeyError:
      raise InvalidAliasException(f"Unknown alias {alias}")

    new_cell = self.cell._replace(row=row, col=col, **props)
    self.grid[row][col] = new_cell

  def pprint(self):
    for row in self.get_frame():
      row_vals = []
      for cell in row:
        row_vals.append(f"{cell if cell else ' '}")
      print(" ".join(row_vals))
    print()

  def step(self):
    self.build_next_grid()
    for row in self.grid:
      for cell in row:
        matched = False
        for rule in self.rules:
          if self.selectors[rule.selector](self.selectors, cell, self.builtins):
            next_state = rule.func(cell)
            matched = True
            break
        if matched:
          next_cell = cell._replace(**next_state)
        else:
          next_cell = cell._replace()
        self.next_grid[cell.row][cell.col] = next_cell
    self.grid = self.next_grid

sim = Simulation()
