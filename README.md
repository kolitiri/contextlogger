# Context Logger

A simple logger that uses the contexvars library to inject extra details in your logs.

## Installation
```python
pip install contextlogger
```

## Usage
This should be as simple as it gets!

Let's assume that we have a package with the following structure:

```
- my_app
  - my_app
    - __init__.py
    - runner.py
  main.py
```

where your **main.py** is simply running the two tasks defined in your runner.py module.

```python
""" main.py """
import asyncio

from my_app.runner import task1, task2


async def main():
	await asyncio.gather(
		task1(),
		task2(),
	)
asyncio.run(main())
```

```python
""" runner.py """
async def task1():
	pass

async def task2():
	pass
```

In the \_\_init\_\_.py module of your project setup your logger as you would normaly do. (you might want to skip logging to a file)
```python
""" __init__.py """
import logging
from logging.handlers import TimedRotatingFileHandler
import os

import contextlogger

# Create a CLogger instance
clogger = contextlogger.getCLogger(__name__)

# Create a logging formatter
logging_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
formatter = logging.Formatter(logging_format)

# Create handlers for console logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
clogger.addHandler(console_handler)

# Create handlers for file logger
LOG_DIR = 'logs'
APP = 'MY-APP'
if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR)

file_handler = TimedRotatingFileHandler(f"{LOG_DIR}/{APP}.log", when="midnight", interval=1)
file_handler.setFormatter(formatter)
file_handler.suffix = "%Y%m%d"
clogger.addHandler(file_handler)
```
Notice that instead of using the **getLogger** function of the standard logging library, we now use the **getCLogger** from the contextlogger package.

Once your logger configuration is set, you can use your logger in your **runner.py** file (or whichever the entry point of your package you chose to be)
```python
""" runner.py """
from my_app import clogger

async def task1():
	clogger.info(f"Hello from {task1.__name__}")

async def task2():
	clogger.info(f"Hello from {task2.__name__}")
```

As expected, the output of the clogger will be:
```
2020-12-06 18:07:27,008 INFO my_app Hello from task1
2020-12-06 18:07:27,009 INFO my_app Hello from task2
```

Now lets add some context to our logging.

We can do that by adding a list of **CLogVar** (context log variables) to our logger.

Let's add a 'static' attribute... Not very useful but why not!

```python
""" runner.py """
from contextlogger import CLogVar
from my_app import clogger

clogger.clogvars = [
	CLogVar(name='static'),
]

async def task1():
    # Set our 'static' value for task1
	clogger.setvar('static', value=1)

	clogger.info(f"Hello from {task1.__name__}")

async def task2():
    # Set our 'static' value for task2
	clogger.setvar('static', value=2)

	clogger.info(f"Hello from {task2.__name__}")
```
And voila! Now the output of the clogger includes our static values:

```
2020-12-06 18:12:07,505 INFO my_app {'static': 1} Hello from task1
2020-12-06 18:12:07,505 INFO my_app {'static': 2} Hello from task2
```

Ok but that was not very handy, right? Let's do something more realistic. Let's pretend that this is our FastApi application and we want to add a 'request_id' to every request we receive.

Now, things get interesting! Our CLogVar can also accept a 'setter' argument which is a function that generates a new uuid every time we enter a new context. Every time we call the **setvar** without a value, it will try to find a **setter** to do the job!

```python
from uuid import uuid4

from contextlogger import CLogVar
from my_app import clogger

clogger.clogvars = [
	CLogVar(name='static'),
	CLogVar(name='request_id', setter=lambda: str(uuid4())),
]

async def task1():
	# Set our 'static' value for task1
	clogger.setvar('static', value=1)
	
	# Set our request_id value for task1
	clogger.setvar('request_id')

	clogger.info(f"Hello from {task1.__name__}")

async def task2():
    # Set our 'static' value for task2
	clogger.setvar('static', value=2)
	
	# Set our 'request_id' value for task2
	clogger.setvar('request_id')

	clogger.info(f"Hello from {task2.__name__}")
```

And here we are, with something a lot more useful than just a static value:
```
2020-12-06 18:21:17,626 INFO my_app {'request_id': 'd3961bd9-f701-4222-ad32-f204e9eb968a', 'static': 1} Hello from task1
2020-12-06 18:21:17,626 INFO my_app {'request_id': '6d4cdab2-e24b-481b-b54b-12c6ee9bcc1b', 'static': 2} Hello from task2
```

Finally, let's add an extra module just for sake of it.

Now our directory will look like:
```
- my_app
  - my_app
    - __init__.py
    - runner.py
    - another_module.py
  main.py
```

where our **another_module.py** simply imports the logger and uses it in a function:
```python
from my_app import clogger


def test():
	clogger.info(f"Hello from another_module")
```

Now, if we call our test function inside the task1 of our **runner.py**:

```python
from uuid import uuid4

from contextlogger import CLogVar
from my_app import clogger
from my_app.another_module import test

clogger.clogvars = [
	CLogVar(name='static'),
	CLogVar(name='request_id', setter=lambda: str(uuid4())),
]

async def task1():
	# Set our 'static' value for task1
	clogger.setvar('static', value=1)
	
	# Set our request_id value for task1
	clogger.setvar('request_id')

	clogger.info(f"Hello from {task1.__name__}")
	
	test()

async def task2():
    # Set our 'static' value for task2
	clogger.setvar('static', value=2)
	
	# Set our 'request_id' value for task2
	clogger.setvar('request_id')

	clogger.info(f"Hello from {task2.__name__}")
```

we should see that the log line that is printed inside our **another_module.py** has the same uuid with the log line that is printed in task1

```
2020-12-06 18:33:36,634 INFO my_app {'request_id': '1eff5e40-4b05-4cd1-bd9c-edbee85d2995', 'static': 1} Hello from task1
2020-12-06 18:33:36,635 INFO my_app {'request_id': '1eff5e40-4b05-4cd1-bd9c-edbee85d2995', 'static': 1} Hello from another_module
2020-12-06 18:33:36,635 INFO my_app {'request_id': 'ec68779f-46f6-4ea0-a003-9ddb053887e1', 'static': 2} Hello from task2
```

## Contribute
I am currently working on the contributions documentation so for now, if you would like to create a pull request drop me a message on instagram.

## Authors
Christos Liontos