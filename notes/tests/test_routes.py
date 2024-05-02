from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):

    #@classmethod
    #def setUpTestData(cls):
    #    cls.note = Note.objects.create(title='Заголовок', text='Текст')
    #    print(cls.note.slug)
#
    #def test_home_page(self):
    #    url = reverse('notes:home')
    #    response = self.client.get(url)
    #    self.assertEqual(response.status_code, HTTPStatus.OK)
#

    def test_pages_availability(self):
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

    #def test_redirect_for_anonymous_client(self):
    #    # Сохраняем адрес страницы логина:
    #    login_url = reverse('users:login')
    #    # В цикле перебираем имена страниц, с которых ожидаем редирект:
    #    for name in ('notes:list', 'notes:add', 'notes:delete',
    #                 'notes:detail', 'notes:success', 'notes:detail'):
    #        with self.subTest(name=name):
    #            # Получаем адрес страницы редактирования или удаления комментария:
    #            url = reverse(name, args=(self.slug,))
    #            # Получаем ожидаемый адрес страницы логина, 
    #            # на который будет перенаправлен пользователь.
    #            # Учитываем, что в адресе будет параметр next, в котором передаётся
    #            # адрес страницы, с которой пользователь был переадресован.
    #            redirect_url = f'{login_url}?next={url}'
    #            response = self.client.get(url)
    #            # Проверяем, что редирект приведёт именно на указанную ссылку.
    #            self.assertRedirects(response, redirect_url)
