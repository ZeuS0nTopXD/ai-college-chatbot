from backend.database.database import SessionLocal
from backend.models.timetable import Timetable
from backend.data.timetable_data import TIMETABLE_DATA


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
                start_time=item["start_time"],
                end_time=item["end_time"],
                subject=item["subject"],
                teacher=item["teacher"],
                room=item["room"],
                lecture_type=item["lecture_type"]
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