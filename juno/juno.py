import base64
import json
from IPython.display import Javascript, clear_output, display, HTML

from .event_javascript import JUNO_PKG_JS, get_info_injection
from .prompting_javascript import write_edit_stream, write_completion_stream, submit_feedback, set_api_key
from .agent_injection import inject_start_agent, inject_stream_action


def _handle_api_key(notebook_state):
    if 'juno_api_key' in notebook_state:
        display(Javascript(set_api_key(notebook_state['juno_api_key']['value'])))
        clear_output()


def chat(command, notebook_state):
    _handle_api_key(notebook_state)
    encoded_nb_state = base64.b64encode(json.dumps(notebook_state).encode('utf-8')).decode('utf-8')
    completion_js = write_completion_stream(command, encoded_nb_state, True, 5)
    display(Javascript(JUNO_PKG_JS + completion_js))
    clear_output()
    

def hack():
    display(Javascript(JUNO_PKG_JS + get_info_injection('')))


def edit(command, notebook_state):
    _handle_api_key(notebook_state)
    encoded_nb_state = base64.b64encode(json.dumps(notebook_state).encode('utf-8')).decode('utf-8')
    completion_js = write_edit_stream(command, encoded_nb_state, True, 5, False)
    display(Javascript(JUNO_PKG_JS + completion_js))
    clear_output()


def debug(_, notebook_state):
    _handle_api_key(notebook_state)
    command = ""
    encoded_nb_state = base64.b64encode(json.dumps(notebook_state).encode('utf-8')).decode('utf-8')
    completion_js = write_edit_stream(command, encoded_nb_state, True, 5, True)
    display(Javascript(JUNO_PKG_JS + completion_js))
    clear_output()


def feedback(command):
    completion_js = submit_feedback(command)
    display(Javascript(JUNO_PKG_JS + completion_js))
    clear_output()


def start_agent(command, notebook_state):
    _handle_api_key(notebook_state)
    encoded_nb_state = base64.b64encode(json.dumps(notebook_state).encode('utf-8')).decode('utf-8')
    completion_js = inject_start_agent(command, encoded_nb_state)
    display(Javascript(JUNO_PKG_JS + completion_js))
    clear_output()


def agent_action(command, notebook_state):
    encoded_nb_state = base64.b64encode(json.dumps(notebook_state).encode('utf-8')).decode('utf-8')
    completion_js = inject_stream_action(command, encoded_nb_state)
    display(Javascript(JUNO_PKG_JS + completion_js))
    clear_output()
    # display js to start agent and call agent_next from js
    
    # agent_next:
    # if steps remaining:
    # returns %action command string that gets streamed into cell and then run almost as normal
    # if error, then %action-debug
    # else %agent-next called in invisible cell
    
    # if no steps remaining:
    # returns AGENT_DONE message which is caught by the streamer
    