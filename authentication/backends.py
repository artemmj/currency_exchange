import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        Метод 'authenticate' вызывается каждый раз при каждом запросе,
        независимо от того, требуется ли конечная точка аутентификации.

        'authenticate' имеет для возможных вызываемых значения:

        1) 'None' - мы будет возвращать None в случае если значем, что
        аутентификация не удастся, например, если не был передан токен.

        2) '(user, token)' - возвращаем комбинацию user/token в случае, если
        аутентификация прошла успешно.

        Если ни один из вариантов не выполнен, это означает, что произошла
        ошибка, и мы ничего не возвращаем. Мы просто вызываем исключение
        'AuthenticationFailed' и позволяем Django REST Framework обработать.
        """
        request.user = None

        # 'auth_header' должен быть массивом с двумя элементами:
        # 1) именем заголовка аутентификации (в данном случае 'Token') и
        # 2) JWT, с которым мы должны аутентифицироваться.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Неверный заголовок токена.
            # Учетные данные не предоставлены.
            # Проверка подлинности не пройдена.
            return None

        elif len(auth_header) > 2:
            # Неверный заголовок токена.
            # Строка токена не должна содержать пробелы.
            # Проверка подлинности не пройдена.
            return None

        # Библиотека JWT, которую мы используем, не может обрабатывать тип
        # 'byte', который обычно используется стандартными библиотеками в
        # Python3. Чтобы обойти это, нам просто нужно декодировать 'prefix' и
        # 'token'. Это не путь чистого кода, конечно, но это хорошее решение,
        # потому что мы получили бы ошибку если не декодировали эти значения.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # Префикс заголовка auth не тот, который ожидался.
            # Проверка подлинности не пройдена.
            return None

        # К настоящему моменту мы полагаем, что есть шанс на успешную
        # аутентификацию. Мы делегируем фактическую аутентификацию учетных
        # данных для метода ниже.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Попытка проверить подлинность указанных учетных данных. Если
        аутентификация прошла успешно, вернуть пользователя и токен.
        Если нет, выкинутьте ошибку.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except Exception:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
