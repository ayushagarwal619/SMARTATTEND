from src.database.config import supabase
import bcrypt



def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Check for unique username, returns false when username is already taken
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0 



def create_teacher(username, password, name, mobile_number=None):
    data = {"username": username, "password": hash_pass(password), "name": name}
    if mobile_number:
        data["mobile_number"] = mobile_number
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None


def get_all_students():
    response = supabase.table('students').select("*").execute()
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {'name': new_name, 'face_embedding':face_embedding, "voice_embedding": voice_embedding}
    response = supabase.table('students').insert(data).execute()
    return response.data


def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data


    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions


        sub.pop('subject_student', None)
        sub.pop('attendance_logs', None)

    return subjects


def  enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response= supabase.table('subject_students').insert(data).execute()
    return response.data


def  unenroll_student_to_subject(student_id, subject_id):
    response= supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return response.data



def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def get_student_attendance(student_id):
    response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def create_attendance(logs):
    response = supabase.table('attendance_logs').insert(logs).execute()
    return response.data

def get_attendance_for_teacher(teacher_id):
    response = supabase.table('attendance_logs').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
    return response.data



def reset_teacher_password(mobile_number, new_password):
    """Reset teacher password by mobile number. Returns True if successful."""
    response = supabase.table("teachers").select("teacher_id").eq("mobile_number", mobile_number).execute()
    if not response.data:
        return False
    teacher_id = response.data[0]['teacher_id']
    supabase.table("teachers").update({"password": hash_pass(new_password)}).eq("teacher_id", teacher_id).execute()
    return True


def get_session_notes(teacher_id, subject_id):
    import os, json
    notes_file = os.path.join(os.path.dirname(__file__), "session_notes.json")
    if not os.path.exists(notes_file):
        return ""
    try:
        with open(notes_file, "r", encoding="utf-8") as f:
            notes_data = json.load(f)
        key = f"{teacher_id}_{subject_id}"
        return notes_data.get(key, "")
    except Exception:
        return ""


def save_session_notes(teacher_id, subject_id, notes):
    import os, json
    notes_file = os.path.join(os.path.dirname(__file__), "session_notes.json")
    notes_data = {}
    if os.path.exists(notes_file):
        try:
            with open(notes_file, "r", encoding="utf-8") as f:
                notes_data = json.load(f)
        except Exception:
            pass
    key = f"{teacher_id}_{subject_id}"
    notes_data[key] = notes
    try:
        with open(notes_file, "w", encoding="utf-8") as f:
            json.dump(notes_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
