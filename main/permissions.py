from rest_framework import permissions

class IsEmployeeOrReadOnly(permissions.BasePermission):
    """
    Сотрудник может создавать заявки, остальные — только смотреть
    """

    def has_permission(self, request, view):
        if request.user.role in ['EMPLOYEE', 'MANAGER', 'ACCOUNTANT', 'ADMIN']:
            return True
        return False


class IsManagerOrAccountant(permissions.BasePermission):
    """
    Только менеджеры/бухгалтеры могут одобрять или менять статус
    """

    def has_permission(self, request, view):
        return request.user.role in ['ACCOUNTANT', 'ADMIN']
