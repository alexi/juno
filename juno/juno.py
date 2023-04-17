import base64
import json
from IPython.display import Javascript, clear_output, display, HTML

from .event_javascript import BUTTON_HANDLERS, LISTENER_JS, EXPLANATION_FUNCTION
from .prompting_javascript import write_edit_stream, write_completion_stream


def chat(command, notebook_state):
    encoded_nb_state = base64.b64encode(json.dumps(notebook_state).encode('utf-8')).decode('utf-8')
    completion_js = write_completion_stream(command, encoded_nb_state, True, 5)
    display(Javascript(completion_js))
    clear_output()
    
    
def hack():
    display(Javascript(BUTTON_HANDLERS + EXPLANATION_FUNCTION + LISTENER_JS))


def edit(command, notebook_state):
    encoded_nb_state = base64.b64encode(json.dumps(notebook_state).encode('utf-8')).decode('utf-8')
    completion_js = write_edit_stream(command, encoded_nb_state, True, 5)
    display(Javascript(completion_js))
    clear_output()
