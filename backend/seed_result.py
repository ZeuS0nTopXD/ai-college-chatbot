# ============================================================
# VSIT RESULT DATABASE SEEDER
# ============================================================

from backend.database.database import SessionLocal
from backend.models.result import Result
from backend.data.result_data import RESULT_DATA


def seed_results():

    db = SessionLocal()

    try:

        print("Starting VSIT result seeding...")

        # ----------------------------------------------------
        # DELETE OLD RESULT DATA
        # ----------------------------------------------------

        deleted_count = db.query(Result).delete(
            synchronize_session=False
        )

        db.commit()

        print(
            f"Deleted {deleted_count} old result record(s)."
        )

        # ----------------------------------------------------
        # INSERT RESULT DATA
        # ----------------------------------------------------

        for item in RESULT_DATA:

            result_entry = Result(
                course=item["course"],
                semester=item["semester"],
                batch=item["batch"],
                year=item["year"],
                title=item["title"],
                url=item["url"]
            )

            db.add(result_entry)

        # ----------------------------------------------------
        # SAVE DATA
        # ----------------------------------------------------

        db.commit()

        print(
            f"Successfully inserted "
            f"{len(RESULT_DATA)} result record(s)."
        )

    except Exception as e:

        db.rollback()

        print("ERROR while inserting result data:")
        print(e)

    finally:

        db.close()

        print("Database connection closed.")


# ============================================================
# RUN SEEDER
# ============================================================

if __name__ == "__main__":

    seed_results()