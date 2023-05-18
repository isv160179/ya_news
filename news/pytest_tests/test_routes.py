from http import HTTPStatus

import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
            ('news:detail', pytest.lazy_fixture('id_news_for_args')),
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


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
            (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client,
        name,
        id_comment_for_args,
        expected_status,
):
    """
    Тест 2. Страницы удаления и редактирования
    комментария доступны автору комментария.
    Авторизованный пользователь не может зайти
    на страницы редактирования или удаления
    чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=id_comment_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
            ('news:edit', pytest.lazy_fixture('id_comment_for_args')),
            ('news:delete', pytest.lazy_fixture('id_comment_for_args')),
    ),
)
def test_redirects(client, name, args):
    """
    Тест 3. При попытке перейти на страницу редактирования или
    удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
