from django.contrib.auth.mixins import UserPassesTestMixin

class RolMixin(UserPassesTestMixin):
    roles_permitidos = []

    def test_func(self):
        return self.request.user.groups.filter(
            name__in=self.roles_permitidos
        ).exists()