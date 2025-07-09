import os
from flask import current_app
from app import db
from app.models import Classification

def expire_user_classifications_after_login(user):
    jobs = Classification.query.filter_by(user_id=user.uid, is_expired=False).all()
    expired = []

    for job in jobs:
        if job.time_left is None:
            job.is_expired = True
            expired.append(job)

            try:
                zip_path = os.path.join(current_app.root_path, "..", "instance", "downloads", f"{job.download_token}.zip")
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    print(f"Usunięto ZIP: {zip_path}")
            except Exception as e:
                print(f"Błąd przy usuwaniu ZIP-a ID={job.id}: {e}")

    if expired:
        db.session.commit()
