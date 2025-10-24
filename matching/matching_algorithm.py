def calculate_match_score(student_request, company_or_job_request):
    """
    محاسبه امتیاز مچینگ بین درخواست دانشجو و شرکت
    
    Args:
        student_request: درخواست دانشجو
        company_or_job_request: درخواست شغلی شرکت یا کاربر شرکت
    
    Returns:
        float: امتیاز مچینگ بین 0 تا 1
    """
    score = 0.0
    total_weight = 0.0
    
    # اگر company_or_job_request یک کاربر شرکت است، درخواست شغلی آن را بگیر
    if hasattr(company_or_job_request, "job_requests"):
        # این یک کاربر شرکت است
        job_requests = company_or_job_request.job_requests.filter(is_active=True)
        if not job_requests.exists():
            return 0.0
        job_request = job_requests.first()  # اولین درخواست فعال
    else:
        # این یک درخواست شغلی است
        job_request = company_or_job_request
    
    # 1. تطبیق رشته تحصیلی (وزن: 0.3)
    if student_request.field_of_study and job_request.field_of_study:
        if student_request.field_of_study.lower() == job_request.field_of_study.lower():
            score += 0.3
        else:
            # بررسی شباهت رشته‌ها
            similar_fields = check_similar_fields(student_request.field_of_study, job_request.field_of_study)
            if similar_fields:
                score += 0.2
    total_weight += 0.3
    
    # 2. تطبیق نوع شغل (وزن: 0.2)
    if student_request.job_type == job_request.job_type:
        score += 0.2
    total_weight += 0.2
    
    # 3. تطبیق نوع کار (وزن: 0.15)
    if student_request.work_type == job_request.work_type:
        score += 0.15
    total_weight += 0.15
    
    # 4. تطبیق مهارت‌ها (وزن: 0.2)
    skills_match = calculate_skills_match(student_request.skills, job_request.required_skills)
    score += skills_match * 0.2
    total_weight += 0.2
    
    # 5. تطبیق موقعیت جغرافیایی (وزن: 0.1)
    if job_request.work_type != "remote":  # فقط برای کارهای غیردورکاری
        location_match = calculate_location_match(student_request, job_request)
        score += location_match * 0.1
    else:
        score += 0.1  # برای کارهای دورکاری، امتیاز کامل
    total_weight += 0.1
    
    # 6. تطبیق حقوق (وزن: 0.05)
    salary_match = calculate_salary_match(student_request, job_request)
    score += salary_match * 0.05
    total_weight += 0.05
    
    # محاسبه امتیاز نهایی
    if total_weight > 0:
        final_score = score / total_weight
    else:
        final_score = 0.0
    
    return min(final_score, 1.0)  # حداکثر امتیاز 1


def check_similar_fields(field1, field2):
    """بررسی شباهت رشته‌های تحصیلی"""
    field1 = field1.lower()
    field2 = field2.lower()
    
    # لیست رشته‌های مشابه
    similar_groups = [
        ["کامپیوتر", "نرم‌افزار", "برنامه‌نویسی", "it", "فناوری اطلاعات"],
        ["برق", "الکترونیک", "کنترل", "مخابرات"],
        ["مکانیک", "صنایع", "تولید"],
        ["مدیریت", "بازرگانی", "اقتصاد", "حسابداری"],
        ["روانشناسی", "مشاوره", "اجتماعی"],
    ]
    
    for group in similar_groups:
        if any(field in field1 for field in group) and any(field in field2 for field in group):
            return True
    
    return False


def calculate_skills_match(student_skills, required_skills):
    """محاسبه تطبیق مهارت‌ها"""
    if not student_skills or not required_skills:
        return 0.0
    
    student_skills_list = [skill.strip().lower() for skill in student_skills.split(",")]
    required_skills_list = [skill.strip().lower() for skill in required_skills.split(",")]
    
    if not required_skills_list:
        return 1.0
    
    matched_skills = 0
    for required_skill in required_skills_list:
        for student_skill in student_skills_list:
            if required_skill in student_skill or student_skill in required_skill:
                matched_skills += 1
                break
    
    return matched_skills / len(required_skills_list)


def calculate_location_match(student_request, job_request):
    """محاسبه تطبیق موقعیت جغرافیایی"""
    if not student_request.city or not job_request.city:
        return 0.5  # اگر اطلاعات موقعیت موجود نیست، امتیاز متوسط
    
    # تطبیق کامل شهر
    if student_request.city.lower() == job_request.city.lower():
        return 1.0
    
    # تطبیق استان
    if (student_request.province and job_request.province and 
        student_request.province.lower() == job_request.province.lower()):
        return 0.7
    
    return 0.0


def calculate_salary_match(student_request, job_request):
    """محاسبه تطبیق حقوق"""
    if not student_request.expected_salary or not job_request.min_salary:
        return 0.5  # اگر اطلاعات حقوق موجود نیست، امتیاز متوسط
    
    expected_salary = student_request.expected_salary
    min_salary = job_request.min_salary
    max_salary = job_request.max_salary or min_salary * 2
    
    # اگر حقوق مورد انتظار در محدوده باشد
    if min_salary <= expected_salary <= max_salary:
        return 1.0
    
    # اگر حقوق مورد انتظار کمتر از حداقل باشد
    if expected_salary < min_salary:
        return 0.8
    
    # اگر حقوق مورد انتظار بیشتر از حداکثر باشد
    if expected_salary > max_salary:
        return 0.3
    
    return 0.5
