import json 
from models.submission_models import Submission
from core.db_core import get_db_session

submission_file_path = "./input/MovieSuggestions_submissions"

session = get_db_session()

BATCH_SIZE = 200
processed = 0
batch = []


with open(submission_file_path, 'r', encoding="utf-8") as submission_file:
    for line in submission_file:
        try:
            obj = json.loads(line)
            batch.append(
                Submission(
                    id  = obj.get("id"),
                    name = obj.get("name"),
                    self_text = obj.get("selftext"),
                    title = obj.get("title"),
                    score = obj.get("url")
                )
            )

            processed += 1

            if len(batch) > BATCH_SIZE:
                session.bulk_save_objects(batch)
                session.commit()
                batch.clear()
                print(f"{processed} submissions stored!", end="\r\r\r")


        except:
            continue

if batch:
    session.bulk_save_objects(batch)
    session.commit()
    batch.clear()

print("Submission storing completed!")
print(f"{processed} submissions stored!")