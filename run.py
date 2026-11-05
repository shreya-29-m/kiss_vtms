import os
from app import create_app
from app.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting KISS Vocational Training Management System at http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
