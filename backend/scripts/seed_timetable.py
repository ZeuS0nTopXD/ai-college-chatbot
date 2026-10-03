from datetime import datetime, time

from backend.database.database import SessionLocal
from backend.models.timetable import Timetable
from backend.data.timetable_data import TIMETABLE_DATA


def _parse_time(value: str | time) -> time:
    if isinstance(value, time):
        return value
    for pattern in ("%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(value.strip(), pattern).time()
        except ValueError:
            continue
    raise ValueError(f"Unsupported timetable time: {value}")


def seed_timetable():

    # Create database session
    db = SessionLocal()

    try:

        print("Starting timetable seeding...")

        # -----------------------------------------
        # DELETE OLD TIMETABLE DATA
        # -----------------------------------------

        deleted_count = db.query(Timetable).delete()

        db.commit()

        print(f"Deleted {deleted_count} old timetable record(s).")

        # -----------------------------------------
        # INSERT NEW TIMETABLE DATA
        # -----------------------------------------

        for item in TIMETABLE_DATA:

            timetable_entry = Timetable(
                course=item["course"],
                division=item["division"],
                day=item["day"],
                start_time=_parse_time(item["start_time"]),
                end_time=_parse_time(item["end_time"]),
                subject_code=item.get("subject_code", item["subject"]),
                subject_name=item["subject"],
                teacher_names=item["teacher"],
                room=item["room"],
                session_type=item["lecture_type"]
            )

            db.add(timetable_entry)

        # Save all records
        db.commit()

        print(
            f"Successfully inserted "
            f"{len(TIMETABLE_DATA)} timetable records."
        )

    except Exception as e:

        db.rollback()

        print("Error while inserting timetable data:")
        print(e)

    finally:

        db.close()

        print("Database connection closed.")


if __name__ == "__main__":

    seed_timetable()
