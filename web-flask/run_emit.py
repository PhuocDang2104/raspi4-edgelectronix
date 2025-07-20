# run_emit.py
from celery_tasks.emit import run_emit_loop

if __name__ == '__main__':
    run_emit_loop()
