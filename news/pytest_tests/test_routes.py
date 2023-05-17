from http import HTTPStatus

import pytest
from django.shortcuts import reverse


@pytest.mark.parametrize(
    'name, args',
    (
            ('news:detail', pytest.lazy_fixture('id_for_args')),
            ('news:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
    ),
)
@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client, name, args):
    """
    Тест 1. Главная страница доступна анонимному пользователю.
    Страница отдельной новости доступна анонимному пользователю.
    Страницы регистрации пользователей, входа в учётную запись и
    выхода из неё доступны анонимным пользователям.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
