# =========================================================
# VSIT KNOWLEDGE BASE SEEDER
# =========================================================

from backend.database.database import SessionLocal
from backend.models.knowledge import KnowledgeBase


# =========================================================
# SEED KNOWLEDGE
# =========================================================

def seed_knowledge():

    db = SessionLocal()

    try:

        print("Starting VSIT knowledge seeding...")

        # =================================================
        # DELETE OLD VSIT KNOWLEDGE
        # =================================================

        deleted = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.category == "VSIT")
            .delete(
                synchronize_session=False
            )
        )

        db.commit()

        print(
            f"Deleted {deleted} old VSIT knowledge record(s)."
        )

        # =================================================
        # VSIT KNOWLEDGE DATA
        # =================================================

        knowledge_data = [

            # =================================================
            # ABOUT VSIT
            # =================================================

            {
                "category": "VSIT",
                "topic": "About College",
                "question": "What is VSIT?",
                "answer": (
                    "Vidyalankar School of Information Technology (VSIT) "
                    "is an autonomous institute affiliated to the University "
                    "of Mumbai. It is located at Vidyalankar College Marg, "
                    "Wadala (East), Mumbai - 400037. VSIT provides higher "
                    "education in areas including Information Technology, "
                    "Computer Science, Data Science, Management, Commerce "
                    "and Mass Media."
                )
            },

            {
                "category": "VSIT",
                "topic": "About College",
                "question": "Tell me about VSIT.",
                "answer": (
                    "Vidyalankar School of Information Technology (VSIT) "
                    "is an autonomous institute affiliated to the University "
                    "of Mumbai. VSIT focuses on quality education and the "
                    "holistic development of students. The institute offers "
                    "programmes across Information Technology, Computer "
                    "Science, Data Science, Management, Commerce and Mass "
                    "Media. VSIT is located at Vidyalankar College Marg, "
                    "Wadala (East), Mumbai - 400037."
                )
            },

            {
                "category": "VSIT",
                "topic": "About College",
                "question": (
                    "What is Vidyalankar School of Information Technology?"
                ),
                "answer": (
                    "Vidyalankar School of Information Technology (VSIT) "
                    "is an autonomous institute affiliated to the University "
                    "of Mumbai. VSIT provides undergraduate and postgraduate "
                    "education in several disciplines including Information "
                    "Technology, Computer Science, Data Science, Management, "
                    "Commerce and Mass Media."
                )
            },

            {
                "category": "VSIT",
                "topic": "About College",
                "question": "Where is VSIT located?",
                "answer": (
                    "Vidyalankar School of Information Technology is located "
                    "at Vidyalankar College Marg, Wadala (East), Mumbai - "
                    "400037."
                )
            },

            {
                "category": "VSIT",
                "topic": "About College",
                "question": "Is VSIT affiliated to the University of Mumbai?",
                "answer": (
                    "Yes. VSIT is an autonomous institute affiliated to the "
                    "University of Mumbai."
                )
            },

            {
                "category": "VSIT",
                "topic": "About College",
                "question": "Is VSIT an autonomous institute?",
                "answer": (
                    "Yes. Vidyalankar School of Information Technology is "
                    "an autonomous institute affiliated to the University "
                    "of Mumbai."
                )
            },


            # =================================================
            # HISTORY
            # =================================================

            {
                "category": "VSIT",
                "topic": "History",
                "question": "When was VSIT established?",
                "answer": (
                    "The VSIT website timeline records 2002 as the inception "
                    "of Vidyalankar School of Information Technology, when "
                    "the B.Sc. IT course was started with an intake of "
                    "60 students."
                )
            },

            {
                "category": "VSIT",
                "topic": "History",
                "question": "When did VSIT start B.Sc. IT?",
                "answer": (
                    "According to the VSIT website timeline, the B.Sc. IT "
                    "course started in 2002 with an intake of 60 students."
                )
            },


            # =================================================
            # VISION
            # =================================================

            {
                "category": "VSIT",
                "topic": "Vision",
                "question": "What is the vision of VSIT?",
                "answer": (
                    "The vision of VSIT is to establish a leading centre "
                    "of imparting Quality Education in the field of Science, "
                    "Commerce and Management, with emphasis on ensuring that "
                    "students learn fundamental concepts in various "
                    "disciplines, motivating students to apply scientific "
                    "and technological knowledge to develop problem-solving "
                    "capabilities, and making students aware of societal and "
                    "environmental needs with appreciation of the emerging "
                    "global context."
                )
            },

            {
                "category": "VSIT",
                "topic": "Vision",
                "question": "What is VSIT's vision?",
                "answer": (
                    "VSIT's vision is to establish a leading centre of "
                    "imparting Quality Education in Science, Commerce and "
                    "Management. The vision emphasizes fundamental concepts, "
                    "application of scientific and technological knowledge "
                    "for problem solving, and awareness of societal and "
                    "environmental needs in the global context."
                )
            },


            # =================================================
            # MISSION
            # =================================================

            {
                "category": "VSIT",
                "topic": "Mission",
                "question": "What is the mission of VSIT?",
                "answer": (
                    "The mission of VSIT is to provide an educational "
                    "environment where students can reach their full "
                    "potential in their chosen discipline and become "
                    "responsible citizens without compromising on ethics."
                )
            },

            {
                "category": "VSIT",
                "topic": "Mission",
                "question": "What is VSIT's mission?",
                "answer": (
                    "VSIT's mission is to provide an educational environment "
                    "where students can reach their full potential in their "
                    "chosen discipline and become responsible citizens "
                    "without compromising on ethics."
                )
            },


            # =================================================
            # CORE VALUES
            # =================================================

            {
                "category": "VSIT",
                "topic": "Core Values",
                "question": "What are the core values of VSIT?",
                "answer": (
                    "The core values highlighted by Vidyalankar are "
                    "Honesty, Integrity, Excellence, Responsibility, "
                    "Commitment and Salubrious Attitude."
                )
            },

            {
                "category": "VSIT",
                "topic": "Core Values",
                "question": "What values does VSIT promote?",
                "answer": (
                    "VSIT promotes values including honesty, integrity, "
                    "excellence, responsibility, commitment and a salubrious "
                    "attitude. These values are intended to guide the "
                    "attitudes and behaviour of members of the Vidyalankar "
                    "family."
                )
            },


            # =================================================
            # COURSES
            # =================================================

            {
                "category": "VSIT",
                "topic": "Courses",
                "question": "What courses does VSIT offer?",
                "answer": (
                    "The VSIT website currently lists programmes including "
                    "B.A. Multimedia & Mass Communication, B.A. Digital "
                    "Marketing Communication, M.A. Entertainment, Media and "
                    "Advertising, B.M.S. Management Studies, B.Com. Business "
                    "Administration, B.Com. Business Management, M.Com. "
                    "Business Management, B.Sc. Information Technology, "
                    "B.Sc. Data Science, B.Sc. Computer Science "
                    "(Artificial Intelligence and Machine Learning), "
                    "B.Sc. Computer Science (Software Engineering), and "
                    "M.Sc. Information Technology."
                )
            },

            {
                "category": "VSIT",
                "topic": "Courses",
                "question": "Which courses are available at VSIT?",
                "answer": (
                    "VSIT offers programmes in Mass Media, Digital Marketing, "
                    "Management, Commerce, Information Technology, Data "
                    "Science and Computer Science. The website lists "
                    "undergraduate and postgraduate programmes in these "
                    "areas."
                )
            },

            {
                "category": "VSIT",
                "topic": "Courses",
                "question": "What programs are offered by VSIT?",
                "answer": (
                    "VSIT offers undergraduate and postgraduate programmes "
                    "in areas such as Information Technology, Data Science, "
                    "Computer Science, Management, Commerce and Mass Media."
                )
            },


            # =================================================
            # STUDENT EXPERIENCE
            # =================================================

            {
                "category": "VSIT",
                "topic": "Student Facilities",
                "question": "What does VSIT offer to students?",
                "answer": (
                    "VSIT provides students with a technology-enabled "
                    "learning environment that includes modern laboratories, "
                    "projects, seminars and exhibitions, campus activities "
                    "and a green campus. The institute also emphasizes "
                    "teamwork, practical learning, industry awareness and "
                    "student development."
                )
            },

            {
                "category": "VSIT",
                "topic": "Student Facilities",
                "question": "What facilities are available at VSIT?",
                "answer": (
                    "VSIT highlights modern laboratories, a technology-enabled "
                    "campus, project-based learning, seminars and exhibitions, "
                    "campus activities and a green campus as part of the "
                    "student experience."
                )
            },


            # =================================================
            # PLACEMENTS
            # =================================================

            {
                "category": "VSIT",
                "topic": "Placements",
                "question": "Does VSIT provide placement assistance?",
                "answer": (
                    "Yes. VSIT has a dedicated placement team that works "
                    "to ensure final-year students receive placement "
                    "opportunities through campus recruitment. The placement "
                    "cell interacts with companies and prepares students "
                    "for corporate requirements by addressing technical, "
                    "domain and soft-skill gaps."
                )
            },

            {
                "category": "VSIT",
                "topic": "Placements",
                "question": "Tell me about placements at VSIT.",
                "answer": (
                    "VSIT has a dedicated placement cell for campus "
                    "placements. It interacts with companies to understand "
                    "their manpower requirements and prepares students for "
                    "corporate requirements. The placement cell works on "
                    "technical skills, domain skills and soft skills."
                )
            },

            {
                "category": "VSIT",
                "topic": "Placements",
                "question": "What placement opportunities are available at VSIT?",
                "answer": (
                    "VSIT's placement cell releases information about "
                    "upcoming placement opportunities, including company "
                    "details, job descriptions, required skills, eligibility "
                    "criteria and salary information when provided by the "
                    "company. Eligible registered students can participate "
                    "in the campus placement process."
                )
            },


            # =================================================
            # INTERNSHIPS
            # =================================================

            {
                "category": "VSIT",
                "topic": "Internships",
                "question": "Does VSIT provide internship opportunities?",
                "answer": (
                    "Yes. VSIT encourages students to undertake internships "
                    "at organizations and companies and also initiates "
                    "in-house internships. The internship programme is "
                    "intended to bridge the gap between theoretical learning "
                    "and practical experience in the industry."
                )
            },

            {
                "category": "VSIT",
                "topic": "Internships",
                "question": "How can students find internships through VSIT?",
                "answer": (
                    "The VSIT Placement Cell motivates and helps students "
                    "undertake internships at organizations or companies "
                    "and also initiates in-house internships. Internship "
                    "opportunities can therefore be pursued with support "
                    "from the concerned department and placement system."
                )
            },


            # =================================================
            # PLACEMENT PROCESS
            # =================================================

            {
                "category": "VSIT",
                "topic": "Placements",
                "question": "How can I participate in campus placements at VSIT?",
                "answer": (
                    "Students who have enrolled or registered for placements "
                    "and meet the eligibility criteria specified by a "
                    "company can register for placement opportunities. "
                    "Registration may take place directly on the company "
                    "website or through a Google Form shared by the "
                    "placement cell."
                )
            },

            {
                "category": "VSIT",
                "topic": "Placements",
                "question": "What are the stages of the VSIT placement process?",
                "answer": (
                    "A typical campus placement process may include a "
                    "pre-placement talk, aptitude or technical test, "
                    "group discussion and technical or HR interview. "
                    "The exact process can vary from company to company."
                )
            },

            {
                "category": "VSIT",
                "topic": "Placements",
                "question": "When do campus placements begin at VSIT?",
                "answer": (
                    "According to the VSIT placement information, campus "
                    "placements typically begin in the fifth semester for "
                    "undergraduate courses and in the third semester for "
                    "postgraduate courses. A typical placement cycle starts "
                    "around August and generally continues until the end "
                    "of the academic year."
                )
            },


            # =================================================
            # CONTACT
            # =================================================

            {
                "category": "VSIT",
                "topic": "Contact",
                "question": "How can I contact VSIT?",
                "answer": (
                    "VSIT can be contacted at +91 22 2410 42 44. "
                    "The institute is located at Vidyalankar College Marg, "
                    "Wadala (East), Mumbai - 400037. The official contact "
                    "information also lists principal@vsit.edu.in."
                )
            },

            {
                "category": "VSIT",
                "topic": "Contact",
                "question": "What is the address of VSIT?",
                "answer": (
                    "Vidyalankar School of Information Technology is located "
                    "at Vidyalankar College Marg, Wadala (East), "
                    "Mumbai - 400037."
                )
            },

            {
                "category": "VSIT",
                "topic": "Contact",
                "question": "What is the phone number of VSIT?",
                "answer": (
                    "The VSIT contact number is +91 22 2410 42 44."
                )
            },

            {
                "category": "VSIT",
                "topic": "Contact",
                "question": "What is the email address of VSIT?",
                "answer": (
                    "The official VSIT contact information lists "
                    "principal@vsit.edu.in."
                )
            },


            # =================================================
            # ACCREDITATION
            # =================================================

            {
                "category": "VSIT",
                "topic": "Accreditation",
                "question": "Is VSIT accredited by NAAC?",
                "answer": (
                    "Yes. VSIT has been accredited by the National "
                    "Assessment and Accreditation Council (NAAC). "
                    "The official VSIT website states that the college "
                    "has been re-accredited with an A Grade."
                )
            },

            {
                "category": "VSIT",
                "topic": "Accreditation",
                "question": "What is the NAAC grade of VSIT?",
                "answer": (
                    "The official VSIT website states that the college "
                    "has been re-accredited with an A Grade by the "
                    "National Assessment and Accreditation Council (NAAC)."
                )
            },


            # =================================================
            # COLLEGE STRENGTH / HIGHLIGHTS
            # =================================================

            {
                "category": "VSIT",
                "topic": "College Highlights",
                "question": "What is VSIT known for?",
                "answer": (
                    "VSIT focuses on quality education, practical learning, "
                    "technology-enabled education and holistic student "
                    "development. The official website highlights modern "
                    "labs, projects, seminars and exhibitions, campus "
                    "activities and a green campus."
                )
            },

            {
                "category": "VSIT",
                "topic": "College Highlights",
                "question": "What are the main objectives of VSIT?",
                "answer": (
                    "The objectives reflected in VSIT's vision include "
                    "helping students understand fundamental concepts, "
                    "encouraging them to apply scientific and technological "
                    "knowledge to solve problems, and creating awareness "
                    "about societal and environmental needs in the emerging "
                    "global context."
                )
            }

        ]


        # =================================================
        # INSERT KNOWLEDGE
        # =================================================

        for item in knowledge_data:

            knowledge_entry = KnowledgeBase(
                category=item["category"],
                topic=item["topic"],
                question=item["question"],
                answer=item["answer"]
            )

            db.add(knowledge_entry)


        # =================================================
        # SAVE DATA
        # =================================================

        db.commit()

        print(
            f"Successfully inserted "
            f"{len(knowledge_data)} VSIT knowledge records."
        )


    except Exception as e:

        db.rollback()

        print(
            "Error while inserting VSIT knowledge data:"
        )

        print(e)


    finally:

        db.close()

        print(
            "Database connection closed."
        )


# =========================================================
# RUN SEEDER
# =========================================================

if __name__ == "__main__":

    seed_knowledge()
    