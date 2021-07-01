# RQ (Redis Queue)


## How to run worker

Any of these methods:

```shell
python worker.py
```

```python
from worker import run_worker

if __name__ == "__main__":
  run_worker()
```


## How to run background tasks

You can just do that directly:

```python
task_queue.enqueue(
  f,
  args=arguments
)
```

But in this way you will not have access to current request `g` data, which may lead, for example, to selecting of incorrect translation language (because `g` stores needed data to select translation). Remember: every background task interacts with separate clean app.

In order to preserve (as much as possible) state of every separate request, it is recommended to run like this:

```python
task_data = prepare_task()

task_queue.enqueue(
  run_task,
  kwargs={
    "f": f,
    "args": arguments,
    "prepare_data": task_data
  }
)
```
