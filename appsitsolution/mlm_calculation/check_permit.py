def check_permission(request):
    try:
        # checking if user has permission to view this page
        permission = request.user.menu_permission.realtime
        if permission:
            permission = list(permission.split('\''))
            if ('1' and '2' and '3' and '4') not in permission:
                return False
        else:
            return False
        return True
    except:
        return False