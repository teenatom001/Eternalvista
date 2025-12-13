"""
EternalVista Application Entry Point.
This script initializes and runs the Flask application.
"""
import os
from eternaal import create_app

app = create_app()

if __name__ == '__main__':
    # Run the application
    # host='0.0.0.0' allows access from other machines/containers
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
