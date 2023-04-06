from .prompts import fix_it_prompt_v2
from .prompting_javascript import GET_ANSWER_CODE, GET_ERROR, GET_CONTEXT

BUTTON_HANDLERS = """

function addFixButton(cell, i) {
    let buttonDiv = $('<div>', {class: 'debug'});
    let existing_button = cell.element.find('.fix-container');
    if (!existing_button.length) {
        buttonDiv.html(
            '<div class="fix-container">' +
            '  <button type="button" style="margin-left: 94px;" onclick="window.writeExplanation(' + i + ')">Debug</button>' +
            '<div id="explanation-' + i + '" class="explanation" style="margin-left: 94px; margin-top: 10px;"></div>' +
            '</div>');
        cell.element.append(buttonDiv);
    }
    return cell;
}

function removeFixButton(cell) {
    let button = cell.element.find('.fix-container');
    if (button.length) {
        button.remove();
    }
}

function addUpdateCodeButton(cellIndex) {
  let cell = Jupyter.notebook.get_cell(cellIndex);
  let buttonDiv = $('<div>', {class: 'subdiv'});
  let existing_button = cell.element.find('.sub-container');
  if (!existing_button.length) {
    buttonDiv.html(
        '<div class="sub-container">' +
        '  <button type="button" style="margin-left: 94px;" onclick="window.fixCode' + cellIndex + '()">Apply Fix</button>' +
          '</div>');
      cell.element.append(buttonDiv);
  }
  return cell;
}

function removeUpdateCodeButton(cell) {
    let button = cell.element.find('.sub-container');
    if (button.length) {
        button.remove();
    }
}

function cellHasErrorOutput(cell) {
    let hasError = false;
    cell.output_area.outputs.forEach(output => {
        if (output.output_type === 'error') {
            hasError = true;
        }
    });
    return hasError;
}

function addRemoveButtons(addOnly) {
    let cells = Jupyter.notebook.get_cells();
    for (let i = 0; i < cells.length; i++) {
        let cell = cells[i];
        let cellHasError = cell.output_area.outputs.length > 0 && cellHasErrorOutput(cell);
        if (cellHasError) {
            addFixButton(cell, i);
        }
        else if (!addOnly && !cellHasError) {
            removeFixButton(cell);
        }
    }
}

"""

EXPLANATION_FUNCTION = """

    {get_answer_function}

    {get_context_function}
    
    {get_error_function}
    
    function removeFirstLine(s) {{
      let index = s.indexOf("\\n");
      if (index !== -1) {{
        return s.slice(index + 1);
      }}
      return s;
    }}
    
    function performSubstitutions(substitutions, inputString) {{
      const lines = substitutions.split("\\n");
      for (const line of lines) {{
        const [search, replace] = line.split(" -> ");
        if (search) {{
            inputString = inputString.replace(search, replace);
        }}
      }}
      return inputString;
    }}


    window.writeExplanation = async function(cellIndex) {{
        let cell = Jupyter.notebook.get_cell(cellIndex);
        let prompt = `{prompt}`;
        let context = getContext({contextSize});
        prompt = prompt.replace("[PREV_CELL_CONTEXT]", context);
        
        if ({addError}) {{
            prompt = prompt.replace("[ERROR_CONTENT]", getErrorOutput(cell));
        }}
        console.log(prompt);
        let parsingSubs = false;
        let subsText = "";
        let text = "";
        let explanationElement = document.getElementById("explanation-" + cellIndex);
        let currentParagraph = document.createElement('p');
        currentParagraph.classList.add('explanation-paragraph');
        explanationElement.appendChild(currentParagraph);
        await getAnswer((answer) => {{
          let newText = answer.choices[0]["delta"]["content"];
          // if newText has a new line, create a new paragraph
          if (!parsingSubs && newText.includes('\\n')) {{
              let splitText = newText.split('\\n');
              currentParagraph.innerHTML += splitText[0];
              for (let i = 1; i < splitText.length; i++) {{
                  currentParagraph = document.createElement('p');
                  currentParagraph.classList.add('explanation-paragraph');
                  explanationElement.appendChild(currentParagraph);
                  text = splitText[i];
                  currentParagraph.innerHTML = text;
              }}
          }}
          // the explanation is over and we are interpreting the substitutions
          else if (newText.includes('—')) {{
            let dashSeparated = newText.split('—');
            text += dashSeparated[0];
            subsText += newText.slice(newText.indexOf("—") + 1);
            parsingSubs = true;
          }}
          else if (parsingSubs) {{
            subsText += newText;
          }}
          else {{
            text += newText;
            currentParagraph.innerHTML = text;
          }}
        }}, prompt)
        const substitutionsString = removeFirstLine(subsText);
        
        console.log("substitutionsString", substitutionsString);
        window["fixCode" + cellIndex] = function () {{
            console.log("fixing code");
            for (let i = cellIndex; i >= Math.max(0, cellIndex - {contextSize}); i--) {{
                let cellToFix = Jupyter.notebook.get_cell(i);
                let cellToFixText = cellToFix.get_text();
                cellToFix.set_text(performSubstitutions(substitutionsString, cellToFixText));
            }}
            removeUpdateCodeButton(cell);
        }}
        addUpdateCodeButton(cellIndex);

    }}
        """.format(prompt=fix_it_prompt_v2(), addContext="true", addError="true", contextSize=1,
                   get_answer_function=GET_ANSWER_CODE, get_context_function=GET_CONTEXT, get_error_function=GET_ERROR)

LISTENER_JS = """
Jupyter.notebook.events.off('output_appended.OutputArea');
Jupyter.notebook.events.off('execute.CodeCell');
Jupyter.notebook.events.on('output_appended.OutputArea', () => setTimeout( () => addRemoveButtons(true), 200));
Jupyter.notebook.events.on('execute.CodeCell', () => setTimeout(() => addRemoveButtons(false), 50));

"""