import json
from IPython.display import Javascript, clear_output, display, HTML

from .event_javascript import BUTTON_HANDLERS, LISTENER_JS, EXPLANATION_FUNCTION
from .prompting_javascript import write_completion_stream


def chat(command, notebook_state):
    completion_js = write_completion_stream(command, json.dumps(notebook_state), True, 5)
    event_handler_js = BUTTON_HANDLERS + EXPLANATION_FUNCTION + LISTENER_JS
    display(Javascript(completion_js + event_handler_js))
    clear_output()