#!/usr/bin/env python3
from webflask import create_app, scheduler

app = create_app()

# Initialize the scheduler here outside the if __name__ block
scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
