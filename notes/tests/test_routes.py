from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.not_author = User.objects.create(username='not_author')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author)

    def test_pages_availability(self):
        """
        Главная страница, страницы регистрации пользователей, входа
        в учётную запись и выхода из неё доступны всем пользователям.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_detail_delete(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки доступны
        только автору заметки. Если на эти страницы попытается зайти другой
        пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_list_done_add(self):
        """
        Аутентифицированному пользователю доступна страница со списком заметок
        notes/, страница успешного добавления заметки done/, страница
        добавления новой заметки add/.
        """
        user = self.author
        self.client.force_login(user)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(user=user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """
        При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:success', None))
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
