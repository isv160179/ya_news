from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news(admin_client):
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def id_news_for_args(news):
    return news.pk,


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def id_comment_for_args(comment):
    return comment.pk,


@pytest.fixture
def news_list(admin_client):
    today = datetime.today()
    news_list = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index)
             ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))
    return news_list


@pytest.fixture
def news_detail_url_with_comments(news, author):
    detail_url = reverse('news:detail', args=(news.pk,))
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return detail_url
