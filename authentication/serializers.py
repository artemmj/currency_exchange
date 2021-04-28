from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import User


class RegistrationSerializer(serializers.Serializer):
    # Убедиться, что длина пароля не короче 8 символов, не длиннее 128 и что
    # пароль не может быть прочитан клиентом.
    password = serializers.CharField(
       max_length=128,
       min_length=8,
       write_only=True,
    )

    email = serializers.CharField(max_length=128)
    balance = serializers.FloatField()
    currency = serializers.CharField(max_length=3, min_length=3)

    # Клиент не должен иметь возможность послать токен вместе с запросом на
    # регистрацию. Пометить токен как read_only.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        # Массив всех полей, которые могут быть включены в запрос или ответ,
        # включая поля, указанные явно выше.
        fields = [
            'email', 'password', 'token', 'balance', 'currency'
        ]

    def create(self, validated_data):
        # Используется переопределенный метод create_user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    # username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # В методе validate мы проверяем, что текущий экземпляр LoginSerializer
        # имеет значение valid. В кейсе, когда пользователь логинится, это
        # означает факт того, что они предоставили почту и пароль, и что эта
        # комбинация соответствует одному из пользователей нашей базы данных.
        email = data.get('email', None)
        password = data.get('password', None)

        # Исключение, если почта не была предоставлена.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # Исключение, если пароль не был предоставлен.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # Метод 'authenticate' предоставляется Django и выполняет проверку для
        # пользователя, который соответствует этой комбинац. адреса электронной
        # почты и пароля. ATTENTION: мы передаем 'email' в качестве значения
        # 'username', поскольку в нашей модели User мы устанавливаем
        # `USERNAME_FIELD` в качестве` email`.
        user = authenticate(username=email, password=password)

        # Если в БД не будет найдено ни одного пользователя с парой
        # почта/пароль, метод 'authenticate' вернет None. Вызвать исключение.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django предоставляет флаг в модели User - is_active, который
        # сообщает, не деактивирована ли учетка пользователя. В случае
        # неактивности - вызвать исключение.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # Метод validate должен возвращать словарь проверенных данных. Это
        # данные, которые передаются в методы 'create' и 'update'.
        return {
            'email': user.email,
            'token': user.token
        }
