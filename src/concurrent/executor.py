from flask_executor import Executor


# That's really not the best approach to do asynchronous things.
# Usage of this should be avoided if possible, especially with
# another extensions, like SQLAlchemy.
# However, it is simple, unlike "Redis Queue" and "Celery".
# And if you want something asynchronous, then you can use this,
# but very carefully!
executor = Executor()
