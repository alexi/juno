from time import time

def inject_start_agent(command, notebook_state):
    return """
console.log("running start agent")
let startCell = Jupyter.notebook.get_selected_index() - 1;
let cell = Jupyter.notebook.get_cell(startCell);
async function main() {{
    console.log("running main", "cell:", cell)
    window.juno.agent_manager.start(cell, "{command}", "{ns}");
}}
if ((Date.now() / 1000) - {current_time} < 2) {{
    main();
}}
""".format(command=command, ns=notebook_state, current_time=round(time()))


def inject_stream_action(command, notebook_state, add_context=True, context_size=5):
    return """
async function main() {{
    window.juno.agent_manager.stream_action(
        `{command}`,
        `{ns}`,
        {addContext},
        {contextSize},
    )
}}
if ((Date.now() / 1000) - {current_time} < 2) {{
    main();
}}
    """.format(command=command, ns=notebook_state, addContext="true" if add_context else "false", 
               contextSize=context_size, current_time=round(time()))