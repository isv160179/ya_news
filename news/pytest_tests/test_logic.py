from http import HTTPStatus

from django.shortcuts import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        client, news, form_data
):
    """
    Тест 1. Анонимный пользователь не может отправить комментарий.
    """
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, form_data):
    """
    Тест 2. Авторизованный пользователь может отправить комментарий.
    """
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(admin_client, news):
    """
    Тест 3. Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment):
    """
    Тест 4. Авторизованный пользователь может удалять свои комментарии.
    """
    url = reverse('news:detail', args=(comment.news_id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """
    Тест 5. Авторизованный пользователь не может удалять чужие комментарии.
    """
    delete_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment, form_data):
    """
    Тест 6. Авторизованный пользователь может редактировать свои комментарии.
    """
    url = reverse('news:detail', args=(comment.news_id,))
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment, form_data):
    """
    Тест 7. Авторизованный пользователь не может
    редактировать чужие комментарии.
    """
    text = comment.text
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == text
