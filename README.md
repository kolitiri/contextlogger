# Context Logger

1. [Description](#description)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Tutorial](#tutorial)
    * [Logging configuration](#logging-configuration)
    * [Logging without context](#logging-without-context)
    * [Logging with static context](#logging-with-static-context)
    * [Logging with dynamic context](#logging-with-dymanic-context)
    * [Logging with context in multiple modules](#logging-multiple)
    * [Structured logging](#structured-logging)
6. [Contributions](#contributions)


# Description <a name="description"></a>

A simple logger that uses the [contextvars](https://docs.python.org/3/library/contextvars.html) library to inject contextual details in your logs.

**Source Code**: https://github.com/kolitiri/contextlogger

# Requirements <a name="requirements"></a>
Python 3.7+

# Installation <a name="installation"></a>
```python
pip install contextlogger
```

# Usage <a name="usage"></a>
This is a bare minimum example to get you started. (Check the tutorial below for some more realistic scenarios)

```python
""" my_app.py """
import asyncio
import logging
from uuid import uuid4

from contextlogger import CLogVar, getCLogger


# Create and configure a CLogger instance
clogger = getCLogger(__name__)
console_handler = logging.StreamHandler()
clogger.addHandler(console_handler)
clogger.setLevel('DEBUG')

# Create a list with static or dynamic context variables
clogger.clogvars = [
    CLogVar(name='static'),
    CLogVar(name='request_id', setter=lambda: str(uuid4())),
]

async def my_func():
    # Set the value of your static variable
    clogger.setvar('static', value=1)

    # Set the value of your dynamic variable
    clogger.setvar('request_id')

    clogger.info(f"Hello World!")


async def main():
    await asyncio.gather(my_func())

if __name__ == '__main__':
    asyncio.run(main())
```

### Output
```
{'static': 1, 'request_id': '7e643fe2-bc7a-498c-a0fe-66ae58c671da'} Hello World!
```

# Tutorial <a name="tutorial"></a>
This should be as simple as it gets!

Let's assume that we have a package with the following structure:
```
my_app/
│
├── my_app/
│   ├── __init__.py
│   ├── runner.py
├── main.py
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

## Logging configuration <a name="description"></a>

In the **\_\_init\_\_.py** module of your project setup your logger.
This will be very similar to the way you would normally configure a regular logger from the standard library.
```python
""" __init__.py """
import logging
from logging.handlers import TimedRotatingFileHandler
import os

import contextlogger

# Create a CLogger instance
clogger = contextlogger.getCLogger(__name__)

# The the logging level
clogger.setLevel('DEBUG')

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
So far, the only thing that we have done differently is that instead of using the **getLogger** function of the standard logging library, we used the **getCLogger** function from the contextlogger library.

## Logging without context <a name="logging-without-context"></a>

Once your logger configuration is set, you can use your logger in your **runner.py** file (or whatever file you choose as your entry point)
```python
""" runner.py """
from my_app import clogger

async def task1():
	clogger.info(f"Hello from {task1.__name__}")

async def task2():
	clogger.info(f"Hello from {task2.__name__}")
```

As expected, if you run your **main.py** the output of the clogger will be:
```
2020-12-06 18:07:27,008 INFO my_app Hello from task1
2020-12-06 18:07:27,009 INFO my_app Hello from task2
```

## Logging with static context <a name="logging-with-static-context"></a>

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

## Logging with dynamic context <a name="logging-with-dymanic-context"></a>

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

## Logging with context in multiple modules <a name="logging-multiple"></a>

Finally, let's add an extra module just for the sake of it.

Now our directory will look like:
```
my_app/
│
├── my_app/
│   ├── __init__.py
│   ├── runner.py
│   ├── another_module.py
├── main.py
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

we should see that the log line that is printed inside our **another_module.py** has the same request_id and static values with the log line that is printed in task1. And this is expected since they belong to the same context.

```
2020-12-06 18:33:36,634 INFO my_app {'request_id': '1eff5e40-4b05-4cd1-bd9c-edbee85d2995', 'static': 1} Hello from task1
2020-12-06 18:33:36,635 INFO my_app {'request_id': '1eff5e40-4b05-4cd1-bd9c-edbee85d2995', 'static': 1} Hello from another_module
2020-12-06 18:33:36,635 INFO my_app {'request_id': 'ec68779f-46f6-4ea0-a003-9ddb053887e1', 'static': 2} Hello from task2
```

## Structured logging <a name="structured-logging"></a>

If you prefer structured logging, you can create the **clogger** instance using the 'structured' argument, which will cause the message to be printed in a structured format.

Then, just change your formatter accordingly.

```python

""" __init__.py """
import logging
from logging.handlers import TimedRotatingFileHandler
import os


import contextlogger

# Create a CLogger instance
clogger = contextlogger.getCLogger(__name__, structured=True)

# Create a logging formatter
logging_format = "{'time': '%(asctime)s', 'level': '%(levelname)s', 'name': '%(name)s', %(message)s}"
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
The output result will become:

```
{'time': '2020-12-11 15:52:11,487', 'level': 'INFO', 'name': 'my_app', 'msg': 'Hello from task1', 'static': '1', 'request_id': 'cc75cb8f-f267-4406-b49c-fc2196a686c6'}
{'time': '2020-12-11 15:52:11,487', 'level': 'INFO', 'name': 'my_app', 'msg': 'Hello from another_module', 'static': '1', 'request_id': 'cc75cb8f-f267-4406-b49c-fc2196a686c6'}
{'time': '2020-12-11 15:52:11,487', 'level': 'INFO', 'name': 'my_app', 'msg': 'Hello from task2', 'static': '2', 'request_id': '7117cdb4-a0dd-4e12-89a5-756a03d7f8b1'}
```


# Contributions  <a name="contributions"></a>
If you want to contribute to the package, please have a look at the CONTRIBUTING.md file for some basic instructions.
Feel free to reach me in my email or my twitter account, which you can find in my github profile!

# License
This project is licensed under the terms of the MIT license.

# Authors
Christos Liontos