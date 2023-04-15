from time import time

GET_CONTEXT = """
function getContext(contextSize) {{
    let prevCellContents = [];
    const cells = Jupyter.notebook.get_cells();
    const currentCellIndex = Jupyter.notebook.get_selected_index();
    for (let i = currentCellIndex - 1; i >= Math.max(0, currentCellIndex - 1 - contextSize); i--) {{
        let cell = cells[i];
        let cellContents = cell.get_text()
        // Don't include the prompt in the context
        if (!cellContents.trimStart().startsWith("%chat")) {{
            prevCellContents.unshift(cellContents)
        }}
    }}
    return prevCellContents.join("\\n###\\n");
}}
""".format()  # Formatting because of the double brackets included.

GET_ERROR = """
function getErrorOutput(cell) {
    let errorOutputs = cell.output_area.outputs.filter( output => output.output_type === 'error')
    if (errorOutputs.length > 0) {
        let error = errorOutputs[0];
        return `${error.ename}: ${error.evalue}`;
    }
    return "";
}
"""

GET_ANSWER_CODE = """
async function getAnswer(callback, command, ns, context, error) {{

    await fetchSSE("https://api.struct.network/query", {{
        method: "POST",
        headers: {{
            "Content-Type": "application/json"
        }},
        body: JSON.stringify({{
            command: command,
            data_info: ns,
            prev_transcript: context,
            error: error
        }}),
        onMessage(message) {{
            const allEvents = message.replaceAll("data: ", "");
            allEvents.split("\\n\\n").forEach((dataString) => {{
                dataString = dataString.trim();
                if (dataString.length === 0) {{
                    return;
                }}
                else if (dataString === "[DONE]") {{
                    console.log("COMPLETED receiving response ");
                    return;
                }}
                try {{
                    const data = JSON.parse(dataString);
                    callback(data);
                }} catch (e) {{
                    console.log("Error parsing data", dataString, e);
                }}
            }});
        }},
    }});
}}

async function* streamAsyncIterable(stream) {{
  const reader = stream.getReader();
  try {{
    while (true) {{
      const {{ done, value }} = await reader.read();
      if (done) {{
        return;
      }}
      yield value;
    }}
  }} finally {{
    reader.releaseLock();
  }}
}}

async function fetchSSE(resource, options) {{
  const {{ onMessage, ...fetchOptions }} = options;
  const resp = await fetch(resource, fetchOptions);
  for await (const chunk of streamAsyncIterable(resp.body)) {{
    const message = new TextDecoder().decode(chunk);
    onMessage(message);
  }}
}}

""".format()

def write_completion_stream(command, ns, add_context=False, context_size=5):
    """Write a javascript function that will stream completions from OpenAI's API. using a Python prompt"""
    
    js = """

{get_answer_function}

{get_context_function}

let startCell = Jupyter.notebook.get_selected_index(); 
let offset = 0
Jupyter.notebook.insert_cell_at_index("code", startCell + offset);
let cell = Jupyter.notebook.get_cell(startCell + offset);
async function main() {{
    let context, errorContent;
    if ({addContext}) {{
        context = getContext({contextSize});
    }}
    console.log(context);
    let text = "";
    let newText = "";
    await getAnswer((answer) => {{
      newText = answer;
      console.log("newText", newText);
      if (newText !== undefined && newText.includes('—')) {{
        let splitText = newText.split('—\\n');
        for (let i = 1; i < splitText.length; i++) {{
            offset += 1;
            Jupyter.notebook.insert_cell_at_index("code", startCell + offset)
            cell = Jupyter.notebook.get_cell(startCell + offset);
            text = splitText[i];
            let trimmedText = text.replace(/`+$/, ""); // Remove trailing backticks that denote end of markdown code block.
            cell.set_text(trimmedText);
        }}
      }}
      else if (newText !== undefined) {{
        text += newText;
        let trimmedText = text.replace(/`+$/, ""); // Remove trailing backticks that denote end of markdown code block.
        cell.set_text(trimmedText);
      }}
    }}, `{command}`, `{ns}`, context);
    // Select the first cell that has the code
    Jupyter.notebook.select(startCell);
}}
if ((Date.now() / 1000) - {current_time} < 2) {{
    main();
}}
    """.format(command=command, ns=ns, addContext="true" if add_context else "false", contextSize=context_size,
               get_answer_function=GET_ANSWER_CODE, get_context_function=GET_CONTEXT, current_time=round(time()))
    return js

def write_explanation_stream(command, ns, context_size=5):
    """Write a javascript function that will stream explanations from OpenAI's API. using a Python prompt"""
    js = """

    {get_answer_function}

    {get_context_function}
    
    {get_error_function}

    async function writeExplanation(cellIndex) {{
        let cell = Jupyter.notebook.get_cell(cellIndex);
        let context, errorContent;
        if ({addContext}) {{
            context = getContext({contextSize});
        }}
        if ({addError}) {{
            errorContent = getErrorOutput(cell);
        }}
        console.log(prompt);
        let text = "";
        let explanationElement = document.getElementById("explanation-" + cellIndex);
        await getAnswer((answer) => {{
          text += answer.choices[0]["delta"]["content"];
          explanationElement.innerHTML = text;
        }}, `{command}`, `{ns}`, context, errorContent);
    }}
        """.format(command=command, ns=ns, addContext="true", addError="true", contextSize=context_size,
                   get_answer_function=GET_ANSWER_CODE, get_context_function=GET_CONTEXT, get_error_function=GET_ERROR)
    return js