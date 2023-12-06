import db_helper as dbh
import level_functions as lf
from pathlib import Path
import random
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Static, TextArea
from time import monotonic
from tree_sitter_languages import get_language

#Helps TextArea to recognize SQL for syntax highlighting
sql_language = get_language("sql")
sql_highlight_query = (Path(__file__).parent / "assets/scm/highlights.scm").read_text()

#Get the sprite animations
icons = {}
for i in range(6):
    if i + 1 == 1:
        for j in range(8):
            path = f"assets/ascii/icon{i+1}/icon{i+1}_{j}.ascii"
            with open(path, "r") as f:
                anim = f.read()
                if i+1 not in icons:
                    icons[i+1] = [anim]
                else:
                    icons[i+1].append(anim)
    else:
        for j in range(4):
            path = f"assets/ascii/icon{i+1}/icon{i+1}_{j}.ascii"
            with open(path, "r") as f:
                anim = f.read()
                if i+1 not in icons:
                    icons[i+1] = [anim]
                else:
                    icons[i+1].append(anim)

#Encapsulates the game state
class GameState:
    def __init__(self):
        self.level = 1
        self.stars = 0

state = GameState()

class HUD(Static):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(f"Level: {state.level}", id="level"),
            Static(f"Stars: {state.stars}", id="stars"),
            Button("Exit", id="exit"),
            id="hud"
        )

class WizardBox(Static):
    start_time = reactive(monotonic)
    time = reactive(0.0)
    frame = reactive(0)
    dir = reactive(1)
    
    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        icon: Static = self.query_one("#icon1")
        if self.time > 0.3:
            self.start_time = monotonic()
            self.frame += 1 * self.dir
            if self.frame == 0 or self.frame == 7:
                self.dir *= -1
            icon.update(icons[1][self.frame])

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(icons[1][self.frame], id="icon1"),
            Static(id="message1"),
            id="wizard"
        )

class PatientBox(Static):
    start_time = reactive(monotonic)
    time = reactive(0.0)
    frame = reactive(0)
    dir = reactive(1)
    sprite = random.randint(2, 6)
    
    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        icon: Static = self.query_one("#icon2")
        if self.time > 0.3:
            self.start_time = monotonic()
            self.frame += 1 * self.dir
            if self.frame == 0 or self.frame == 3:
                self.dir *= -1
            icon.update(icons[self.sprite][self.frame])

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(id="message2"),
            Static(id="icon2"),
            id="patient"
        )

class SQLArea(Static):
    def compose(self) -> ComposeResult:
        text_area = TextArea(theme="monokai", id="editor")
        text_area.register_language(sql_language, sql_highlight_query)
        text_area.language = "sql"
        yield Horizontal(
            text_area,
            DataTable(id="table"),
            id="sql"
        )

class BottomButtons(Static):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("Run", id="run"),
            Button("Submit", id="submit"),
            Button("Next", id="next"),
            id="bottom"
        )

class Game(App):
    CSS_PATH = "assets/tcss/style.tcss"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        editor: TextArea = self.query_one("#editor")
        table: DataTable = self.query_one("#table")
        if button_id == "run":
            table.clear(columns=True)
            res, col = dbh.run_sql("assets/db/game.db", editor.text)
            table.add_columns(*col)
            table.add_rows(res)

    def compose(self) -> ComposeResult:
        yield HUD()
        yield WizardBox()
        yield PatientBox()
        yield SQLArea()
        yield BottomButtons()

lf.lvl_1()

game = Game()
game.run()