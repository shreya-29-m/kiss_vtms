import os
from datetime import date, datetime, timedelta
from app import create_app
from app.models import (
    db, User, StudentProfile, TrainerProfile, Category, Course,
    Enrollment, SessionSchedule, Attendance, LearningMaterial,
    Assessment, AssessmentResult, Certificate, AuditLog
)
from app.utils.certificate_gen import generate_certificate_pdf

def seed_database():
    app = create_app()
    with app.app_context():
        print("Cleaning and recreating database schema...")
        db.drop_all()
        db.create_all()

        print("Seeding Vocational Training Categories...")
        categories_data = [
            ("Computer and Information Technology", "Hardware troubleshooting, software literacy, networking fundamentals, and office productivity tools."),
            ("Agriculture & Organic Farming", "Modern horticulture, organic compost preparation, mushroom cultivation, and sustainable farming."),
            ("Tailoring and Fashion Design", "Garment fabrication, pattern drafting, sewing machine operation, and modern apparel design."),
            ("Handicrafts & Tribal Art", "Indigenous crafts preservation, terracotta pottery, traditional bamboo weaving, and Dokra metal craft."),
            ("Electrical and Electronics", "Domestic electrical wiring, appliance diagnostics, solar inverter installation, and safety standards."),
            ("Hospitality & Food Production", "Culinary fundamentals, hygienic food processing, bakery operations, and customer service."),
            ("Beauty and Wellness", "Cosmetology basics, skin care regimens, wellness therapy, and professional salon hygiene."),
            ("Entrepreneurship & Self-Employment", "Micro-enterprise business planning, digital financial literacy, market linkage, and bookkeeping.")
        ]

        cat_objs = {}
        for name, desc in categories_data:
            cat = Category(name=name, description=desc, is_active=True)
            db.session.add(cat)
            cat_objs[name] = cat
        db.session.commit()

        print("Seeding System Users (Admin, Trainers, Students)...")
        # 1. Administrator
        admin_user = User(username='admin', email='admin@kiss.ac.in', role='admin')
        admin_user.set_password('Admin@12345')
        db.session.add(admin_user)
        db.session.commit()

        # 2. Trainers
        trainers_info = [
            {
                'username': 'trainer_it', 'email': 'deepak.it@kiss.ac.in', 'password': 'Trainer@12345',
                'name': 'Er. Deepak Kumar Mohapatra', 'code': 'KISS-TRN-001', 'trade': 'Computer & IT',
                'qual': 'B.Tech (CSE), Certified Hardware Engineer', 'exp': 8,
                'bio': 'Specialist in vocational computing, networking architectures, and empowering tribal youth with IT literacy.'
            },
            {
                'username': 'trainer_agri', 'email': 'santosh.agri@kiss.ac.in', 'password': 'Trainer@12345',
                'name': 'Dr. Santosh Patra', 'code': 'KISS-TRN-002', 'trade': 'Agriculture',
                'qual': 'M.Sc Agriculture, Organic Farming Fellow', 'exp': 10,
                'bio': 'Pioneering organic farm incubation, indigenous crop preservation, and micro-irrigation techniques.'
            },
            {
                'username': 'trainer_tailor', 'email': 'ananya.tailor@kiss.ac.in', 'password': 'Trainer@12345',
                'name': 'Ms. Ananya Barik', 'code': 'KISS-TRN-003', 'trade': 'Tailoring & Fashion Design',
                'qual': 'Diploma in Apparel Manufacturing & Design', 'exp': 6,
                'bio': 'Passionate garment design instructor focusing on commercial apparel production and self-employment.'
            },
            {
                'username': 'trainer_craft', 'email': 'biswanath.craft@kiss.ac.in', 'password': 'Trainer@12345',
                'name': 'Sri Biswanath Murmu', 'code': 'KISS-TRN-004', 'trade': 'Handicrafts & Tribal Art',
                'qual': 'Master Artisan, National Heritage Craftsman', 'exp': 15,
                'bio': 'Preserving tribal cultural artifacts through hands-on metal casting, terracotta modeling, and market trade.'
            },
            {
                'username': 'trainer_electric', 'email': 'subash.elec@kiss.ac.in', 'password': 'Trainer@12345',
                'name': 'Er. Subash Chandra Jena', 'code': 'KISS-TRN-005', 'trade': 'Electrical & Electronics',
                'qual': 'Diploma in Electrical Engg, ITI Master Trainer', 'exp': 9,
                'bio': 'Hands-on domestic installation trainer with industry expertise in solar renewable installations.'
            }
        ]

        trainer_objs = {}
        for t in trainers_info:
            u = User(username=t['username'], email=t['email'], role='trainer')
            u.set_password(t['password'])
            db.session.add(u)
            db.session.flush()

            tp = TrainerProfile(
                user_id=u.id,
                trainer_id_code=t['code'],
                full_name=t['name'],
                department_or_trade=t['trade'],
                contact_number='9861000000',
                qualification=t['qual'],
                experience_years=t['exp'],
                bio=t['bio']
            )
            db.session.add(tp)
            trainer_objs[t['username']] = tp
        db.session.commit()

        # 3. Students
        students_info = [
            {'username': 'student1', 'email': 'ramesh.majhi@kiss.ac.in', 'name': 'Ramesh Majhi', 'code': 'KISS-STU-2026-101', 'level': '+2 Science', 'skills': 'Computer basics, electronics curiosity'},
            {'username': 'student2', 'email': 'sunita.soren@kiss.ac.in', 'name': 'Sunita Soren', 'code': 'KISS-STU-2026-102', 'level': '+2 Arts', 'skills': 'Embroidery, sewing, sketching'},
            {'username': 'student3', 'email': 'bikram.kiskoo@kiss.ac.in', 'name': 'Bikram Kiskoo', 'code': 'KISS-STU-2026-103', 'level': '+3 Commerce', 'skills': 'Bookkeeping, agriculture, horticulture'},
            {'username': 'student4', 'email': 'laxmi.marndi@kiss.ac.in', 'name': 'Laxmi Marndi', 'code': 'KISS-STU-2026-104', 'level': 'Diploma', 'skills': 'Wiring, circuits, mobile maintenance'},
            {'username': 'student5', 'email': 'pramod.hembram@kiss.ac.in', 'name': 'Pramod Hembram', 'code': 'KISS-STU-2026-105', 'level': '+3 Arts', 'skills': 'Clay modeling, tribal woodcraft'},
            {'username': 'student6', 'email': 'minati.hansda@kiss.ac.in', 'name': 'Minati Hansda', 'code': 'KISS-STU-2026-106', 'level': '+2 Arts', 'skills': 'Fabric design, organic gardening'}
        ]

        student_objs = {}
        for s in students_info:
            u = User(username=s['username'], email=s['email'], role='student')
            u.set_password('Student@12345')
            db.session.add(u)
            db.session.flush()

            sp = StudentProfile(
                user_id=u.id,
                student_id_code=s['code'],
                full_name=s['name'],
                academic_level=s['level'],
                contact_number='9777000000',
                educational_qualification='Matriculation / Secondary Board',
                skills_and_interests=s['skills']
            )
            db.session.add(sp)
            student_objs[s['username']] = sp
        db.session.commit()

        print("Seeding Vocational Courses...")
        today = date.today()
        courses_data = [
            {
                'code': 'VT-IT-101',
                'title': 'Computer Hardware, Networking & Office IT Skills',
                'cat': 'Computer and Information Technology',
                'trainer': 'trainer_it',
                'desc': 'Hands-on practical training covering PC architecture assembly, motherboard diagnostics, operating system installation, Ethernet LAN cable crimping, router/switch configuration, and modern office documentation software.',
                'skills': 'PC Assembly, Cable Crimping, Network Troubleshooting, Operating Systems, Office Tools',
                'weeks': 8,
                'schedule': 'Mon, Wed, Fri 10:00 AM - 12:00 PM',
                'seats': 30,
                'att_req': 75.0,
                'pass_mark': 50.0,
                'start': today - timedelta(days=45),
                'end': today + timedelta(days=15)
            },
            {
                'code': 'VT-AG-201',
                'title': 'Sustainable Organic Farming & Mushroom Cultivation',
                'cat': 'Agriculture & Organic Farming',
                'trainer': 'trainer_agri',
                'desc': 'Comprehensive field course in organic vermicomposting, soil fertility preservation, oyster and paddy straw mushroom cultivation, organic pest repellent formulation, and direct market distribution channels.',
                'skills': 'Vermicomposting, Mushroom Spawning, Bio-fertilizers, Soil Testing, Post-Harvest Packaging',
                'weeks': 6,
                'schedule': 'Tue, Thu 08:00 AM - 11:00 AM',
                'seats': 25,
                'att_req': 80.0,
                'pass_mark': 50.0,
                'start': today - timedelta(days=30),
                'end': today + timedelta(days=20)
            },
            {
                'code': 'VT-FD-301',
                'title': 'Apparel Construction, Pattern Drafting & Modern Tailoring',
                'cat': 'Tailoring and Fashion Design',
                'trainer': 'trainer_tailor',
                'desc': 'Intensive vocational workshop covering industrial sewing machine operation, anatomical body measurements, precision garment pattern drafting, garment stitching, collar/cuff assembly, and quality finishing.',
                'skills': 'Industrial Sewing, Pattern Drafting, Fabric Cutting, Garment Assembly, Quality Finishing',
                'weeks': 10,
                'schedule': 'Mon, Wed, Thu 02:00 PM - 04:30 PM',
                'seats': 20,
                'att_req': 75.0,
                'pass_mark': 55.0,
                'start': today - timedelta(days=20),
                'end': today + timedelta(days=50)
            },
            {
                'code': 'VT-HA-401',
                'title': 'Indigenous Dokra Metal Casting & Terracotta Art',
                'cat': 'Handicrafts & Tribal Art',
                'trainer': 'trainer_craft',
                'desc': 'Preserving tribal art traditions through the lost-wax casting technique (Dokra), clay preparation, kiln firing, motif sculpting, and creating commercial art items for craft fairs and artisan cooperatives.',
                'skills': 'Lost-Wax Casting, Clay Conditioning, Kiln Operation, Metal Finishing, Tribal Motifs',
                'weeks': 6,
                'schedule': 'Sat 09:00 AM - 01:00 PM',
                'seats': 15,
                'att_req': 75.0,
                'pass_mark': 50.0,
                'start': today - timedelta(days=15),
                'end': today + timedelta(days=30)
            },
            {
                'code': 'VT-EE-501',
                'title': 'Domestic Electrical Wiring & Solar Photovoltaic Systems',
                'cat': 'Electrical and Electronics',
                'trainer': 'trainer_electric',
                'desc': 'Practical trade certification in single-phase and three-phase residential wiring, MCB/ELCB distribution board installation, multimeter diagnostics, inverter battery maintenance, and rooftop solar panel installation.',
                'skills': 'Residential Wiring, Conduit Installation, MCB Sizing, Solar PV Array Setup, Electrical Safety',
                'weeks': 8,
                'schedule': 'Tue, Fri 03:00 PM - 05:30 PM',
                'seats': 25,
                'att_req': 80.0,
                'pass_mark': 60.0,
                'start': today - timedelta(days=10),
                'end': today + timedelta(days=45)
            },
            {
                'code': 'VT-EN-601',
                'title': 'Micro-Enterprise Incubation & Digital Financial Literacy',
                'cat': 'Entrepreneurship & Self-Employment',
                'trainer': 'trainer_it',
                'desc': 'Practical training for aspiring micro-entrepreneurs: preparing a bankable business plan, cost estimation, digital payment systems (UPI/QR), basic ledger bookkeeping, and government subsidy schemes.',
                'skills': 'Business Model Canvas, Cost Accounting, Digital Payments, Bank Linkage, Customer Service',
                'weeks': 4,
                'schedule': 'Wed 04:00 PM - 06:00 PM',
                'seats': 40,
                'att_req': 75.0,
                'pass_mark': 50.0,
                'start': today,
                'end': today + timedelta(days=28)
            }
        ]

        course_objs = {}
        for c in courses_data:
            course = Course(
                course_code=c['code'],
                title=c['title'],
                category_id=cat_objs[c['cat']].id,
                trainer_id=trainer_objs[c['trainer']].id,
                description=c['desc'],
                skills_covered=c['skills'],
                duration_weeks=c['weeks'],
                training_schedule=c['schedule'],
                max_seats=c['seats'],
                status='active',
                attendance_requirement=c['att_req'],
                passing_score=c['pass_mark'],
                certificate_available=True,
                start_date=c['start'],
                end_date=c['end']
            )
            db.session.add(course)
            course_objs[c['code']] = course
        db.session.commit()

        print("Seeding Session Schedules & Topics...")
        # Add 5 schedules for IT-101
        it_course = course_objs['VT-IT-101']
        schedules_it = [
            (today - timedelta(days=40), "10:00 AM", "12:00 PM", "PC Components, CPU, RAM & Power Supply Architecture", "Hardware Lab 1"),
            (today - timedelta(days=33), "10:00 AM", "12:00 PM", "BIOS/UEFI Configuration & Operating System Installation", "Hardware Lab 1"),
            (today - timedelta(days=26), "10:00 AM", "12:00 PM", "Crimping Cat6 Ethernet Cables & RJ-45 Pinouts", "Networking Lab"),
            (today - timedelta(days=19), "10:00 AM", "12:00 PM", "Configuring Wi-Fi Routers, IP Addressing & Subnetting", "Networking Lab"),
            (today - timedelta(days=12), "10:00 AM", "12:00 PM", "Printer Setup, Driver Diagnostics & Peripherals", "Hardware Lab 1"),
            (today + timedelta(days=5), "10:00 AM", "12:00 PM", "Comprehensive PC Troubleshooting Lab & Final Assembly", "Hardware Lab 1")
        ]
        for s_date, st, et, topic, room in schedules_it:
            db.session.add(SessionSchedule(
                course_id=it_course.id, session_date=s_date, start_time=st, end_time=et, topic=topic, room_or_lab=room
            ))

        # Add schedules for Agriculture
        agri_course = course_objs['VT-AG-201']
        schedules_agri = [
            (today - timedelta(days=25), "08:00 AM", "11:00 AM", "Soil Testing & Vermiculture Bed Preparation", "Agricultural Demonstration Plot"),
            (today - timedelta(days=18), "08:00 AM", "11:00 AM", "Mushroom Substrate Sterilization & Spawning", "Mushroom Hatchery Shed"),
            (today - timedelta(days=11), "08:00 AM", "11:00 AM", "Humidity & Temperature Regulation in Culture Rooms", "Mushroom Hatchery Shed"),
            (today + timedelta(days=4), "08:00 AM", "11:00 AM", "Bio-pesticide Preparation: Neem & Garlic Emulsions", "Agricultural Plot")
        ]
        for s_date, st, et, topic, room in schedules_agri:
            db.session.add(SessionSchedule(
                course_id=agri_course.id, session_date=s_date, start_time=st, end_time=et, topic=topic, room_or_lab=room
            ))
        db.session.commit()

        print("Seeding Student Enrollments...")
        # Enroll students
        enrollments_data = [
            ('student1', 'VT-IT-101', 'enrolled'),
            ('student1', 'VT-EN-601', 'enrolled'),
            ('student2', 'VT-FD-301', 'enrolled'),
            ('student2', 'VT-HA-401', 'enrolled'),
            ('student3', 'VT-AG-201', 'enrolled'),
            ('student3', 'VT-EN-601', 'enrolled'),
            ('student4', 'VT-EE-501', 'enrolled'),
            ('student4', 'VT-IT-101', 'enrolled'),
            ('student5', 'VT-HA-401', 'enrolled'),
            ('student6', 'VT-FD-301', 'enrolled'),
            ('student6', 'VT-AG-201', 'enrolled')
        ]
        for s_key, c_key, status in enrollments_data:
            s_obj = student_objs[s_key]
            c_obj = course_objs[c_key]
            db.session.add(Enrollment(student_id=s_obj.id, course_id=c_obj.id, status=status))
        db.session.commit()

        print("Seeding Attendance Records...")
        # Seed attendance for VT-IT-101 (5 conducted sessions)
        it_trainer_user = User.query.filter_by(username='trainer_it').first()
        it_students = [student_objs['student1'], student_objs['student4']]
        past_dates_it = [
            today - timedelta(days=40),
            today - timedelta(days=33),
            today - timedelta(days=26),
            today - timedelta(days=12),
            today - timedelta(days=5)
        ]

        # Student1 has 100% attendance (5/5 present)
        for d in past_dates_it:
            db.session.add(Attendance(
                course_id=it_course.id,
                student_id=student_objs['student1'].id,
                attendance_date=d,
                status='present',
                remarks='Active participation in lab',
                recorded_by_id=it_trainer_user.id
            ))

        # Student4 has 60% attendance (3/5 present, 2 absent) -> demonstrates ineligibility condition
        for idx, d in enumerate(past_dates_it):
            st = 'present' if idx < 3 else 'absent'
            rmk = 'Attended' if st == 'present' else 'Uninformed absence'
            db.session.add(Attendance(
                course_id=it_course.id,
                student_id=student_objs['student4'].id,
                attendance_date=d,
                status=st,
                remarks=rmk,
                recorded_by_id=it_trainer_user.id
            ))
        db.session.commit()

        print("Seeding Assessments & Marks...")
        # Assessments for VT-IT-101
        ass1 = Assessment(
            course_id=it_course.id,
            title='Practical Exam 1: System Assembly & Cable Crimping',
            assessment_type='practical',
            max_marks=100.0,
            due_date=today - timedelta(days=20),
            description='Assemble a complete desktop CPU from scratch and crimp an RJ-45 cable with verified pin continuity test.'
        )
        ass2 = Assessment(
            course_id=it_course.id,
            title='Lab Project 2: Network Subnetting & Router Configuration',
            assessment_type='project',
            max_marks=100.0,
            due_date=today - timedelta(days=8),
            description='Configure wireless LAN SSID, WPA2 encryption, and verify packet connectivity across client terminals.'
        )
        db.session.add(ass1)
        db.session.add(ass2)
        db.session.commit()

        # Grade student1: 92/100 and 88/100 -> Average 90% (Grade A+)
        db.session.add(AssessmentResult(
            assessment_id=ass1.id,
            student_id=student_objs['student1'].id,
            marks_obtained=92.0,
            feedback='Flawless assembly, neat cable dressing, cable test passed on first attempt.',
            evaluated_by_id=it_trainer_user.id
        ))
        db.session.add(AssessmentResult(
            assessment_id=ass2.id,
            student_id=student_objs['student1'].id,
            marks_obtained=88.0,
            feedback='Accurate routing table configuration and clear documentation of IP allocation.',
            evaluated_by_id=it_trainer_user.id
        ))

        # Grade student4: 55/100 and 60/100 -> Average 57.5%
        db.session.add(AssessmentResult(
            assessment_id=ass1.id,
            student_id=student_objs['student4'].id,
            marks_obtained=55.0,
            feedback='Assembled CPU successfully; cable crimp required re-punching.',
            evaluated_by_id=it_trainer_user.id
        ))
        db.session.add(AssessmentResult(
            assessment_id=ass2.id,
            student_id=student_objs['student4'].id,
            marks_obtained=60.0,
            feedback='Basic connectivity established. Review subnet mask calculations.',
            evaluated_by_id=it_trainer_user.id
        ))
        db.session.commit()

        print("Seeding Official Certificate for Student1...")
        # Student1 has 100% attendance (req: 75%) and 90% score (req: 50%) -> Eligible!
        cert_code = "KISS-CERT-2026-00101"
        cert_filename = "cert_KISS_STU_2026_101_VT_IT_101.pdf"
        cert_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'certificates', cert_filename)

        cert = Certificate(
            certificate_code=cert_code,
            student_id=student_objs['student1'].id,
            course_id=it_course.id,
            issue_date=today,
            attendance_percentage=100.0,
            final_score=90.0,
            grade='A+',
            issued_by_admin_id=admin_user.id,
            pdf_filename=cert_filename,
            is_verified=True
        )
        db.session.add(cert)
        # Update student1's enrollment status to completed
        enr_st1 = Enrollment.query.filter_by(student_id=student_objs['student1'].id, course_id=it_course.id).first()
        enr_st1.status = 'completed'
        db.session.commit()

        # Generate actual PDF file on disk
        generate_certificate_pdf(
            student_name=student_objs['student1'].full_name,
            student_id_code=student_objs['student1'].student_id_code,
            course_title=it_course.title,
            course_code=it_course.course_code,
            category_name=it_course.category.name,
            duration_weeks=it_course.duration_weeks,
            attendance_pct=100.0,
            final_score=90.0,
            grade='A+',
            certificate_code=cert_code,
            issue_date_str=today.strftime('%d %B %Y'),
            trainer_name=it_course.trainer.full_name,
            output_filepath=cert_filepath
        )

        print("Seeding Learning Materials...")
        m1 = LearningMaterial(
            course_id=it_course.id,
            title='PC Assembly & Hardware Safety Guidelines',
            material_type='guide',
            description='Comprehensive illustrated handbook explaining anti-static precautions, motherboard standoffs, and power connectors.',
            link_url='https://example.com/hardware-handbook-sample',
            uploaded_by_id=it_trainer_user.id
        )
        m2 = LearningMaterial(
            course_id=it_course.id,
            title='Network Cabling Standard Cheat Sheet (T568A vs T568B)',
            material_type='notes',
            description='Pinout diagrams and wire color sequences for straight-through and crossover ethernet cables.',
            uploaded_by_id=it_trainer_user.id
        )
        db.session.add(m1)
        db.session.add(m2)
        db.session.commit()

        print("Seeding Initial System Audit Logs...")
        logs = [
            ('System Initialization', 'System', None, 'VTMS database schema created and seed data initialized', admin_user.id),
            ('User Creation', 'User', admin_user.id, 'Administrator account configured', admin_user.id),
            ('Category Provisioning', 'Category', None, f'Created {len(categories_data)} vocational categories', admin_user.id),
            ('Course Creation', 'Course', it_course.id, f'Course {it_course.course_code} created and assigned to trainer', admin_user.id),
            ('Certificate Issued', 'Certificate', cert.id, f'Certificate {cert_code} generated for {student_objs["student1"].student_id_code}', admin_user.id)
        ]
        for action, etype, eid, details, uid in logs:
            db.session.add(AuditLog(
                action=action, entity_type=etype, entity_id=eid, details=details, user_id=uid, ip_address='127.0.0.1'
            ))
        db.session.commit()

        print("Demonstration Database successfully populated!")

if __name__ == '__main__':
    seed_database()
