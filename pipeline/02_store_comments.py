import json 
from models.comment_models import Comment
from core.db_core import get_db_session

comment_file_path = "./input/MovieSuggestions_comments"

session = get_db_session()

BATCH_SIZE = 20000
processed = 0
batch = []


with open(comment_file_path, 'r', encoding="utf-8") as submission_file:
    for line in submission_file:
        try:
            obj = json.loads(line)
            batch.append(
                Comment(
                    parent_id  = obj.get("parent_id"),
                    body = obj.get("body"),
                    score= obj.get("score")
                )
            )

            processed += 1

            if len(batch) > BATCH_SIZE:
                session.bulk_save_objects(batch)
                session.commit()
                batch.clear()
                print(f"{processed} comments stored!", end="\r\r\r")


        except:
            continue

if batch:
    session.bulk_save_objects(batch)
    session.commit()
    batch.clear()


session.close()
print("Comment storing completed!")
print(f"{processed} comments stored!")