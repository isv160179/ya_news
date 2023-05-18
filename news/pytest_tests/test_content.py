import pytest
from django.conf import settings
from django.shortcuts import reverse

HOME_URL = reverse('news:home')


def test_news_count(client, news_list):
    """
    Тест 1. Количество новостей на главной странице — не более 10.
    """
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    """
    Тест 2. Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    first_news_date = object_list[0].date
    all_dates = [news.date for news in object_list]
    assert first_news_date == max(all_dates)


def test_comments_order(client, news_detail_url_with_comments):
    """
    Тест 3. Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url_with_comments)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, exam',
    (
            (pytest.lazy_fixture('client'), False),
            (pytest.lazy_fixture('admin_client'), True)
    ),
)
def test_comment_form_availability_for_different_users(
        parametrized_client, id_news_for_args, exam
):
    """
    Тест 4. Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=id_news_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is exam
