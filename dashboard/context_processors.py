def user_role(request):
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        return {
            'role_admin': user.is_admin_role,
            'role_tutor': user.is_tutor_role,
            'role_student': user.is_student_role,
        }
    return {'role_admin': False, 'role_tutor': False, 'role_student': False}
