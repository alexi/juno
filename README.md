# juno

Juno is an AI collaborator for your Jupyter notebooks. Ask `juno` to write full cells of code and answer questions about your data. Juno understands your notebook context, and can even auto-debug your code as you go.

<h2 align="center">Demo April 24th 2023 </h2>

https://user-images.githubusercontent.com/100244608/234127637-d0d596fa-abfc-41ec-b01e-fafeb05e31e5.mp4

## Getting Started Guide

To use Juno, you need to install the Juno package.
```bash
pip install juno-ai
```

Then, load the extension in your Jupyter notebook.
```python
%load_ext juno
```

## Using Juno

You can ask Juno to write code for you by running `%juno` followed by your prompt in a cell.

It can write functions, create plots, or do data analysis in pandas.
It knows about the variables you have defined in your notebook, so you ask it to work with your data without giving additional context.

For example, you can ask it to sample a random number from 1-10 by running the following cell:
```python
%juno sample a random from 1-10
```
And Juno will write the following code for you:
```python
import random

# sample a random number from 1-10
random_number = random.randint(1, 10)
random_number
```

You can also ask Juno to edit code for you by clicking the ✎ button, adding a prompt after `%edit ` text, and running the cell.
For example, you could ask it to `sample from 1-100 instead` and run the cell to have Juno edit the cell above:
```python
# %edit sample from 1-100 instead
import random

# sample a random number from 1-100
random_number = random.randint(1, 100)
random_number
```

Finally, you can also use Juno to help debug errors in your code. Anytime you run into an exception in your Jupyter notebook, a `Debug` button will appear. When you click it, Juno will take a look at your error and try to fix it in a new cell.

Thanks for trying Juno! If you have any questions or feedback, please reach out to us at hellojunoai@gmail.com
