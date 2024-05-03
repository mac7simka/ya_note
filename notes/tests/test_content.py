from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.not_author = User.objects.create(username='not_author')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author)

    def test_notes_list_for_author(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок и в
        список заметок одного пользователя не попадают заметки другого
        пользователя.
        """
        url = reverse('notes:list')
        users_note_in_list = ((self.author, True), (self.not_author, False),)
        for user, note_in_list in users_note_in_list:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertTrue((self.note in object_list) is note_in_list)

    def test_add_and_edit_has_form(self):
        """Hа страницы создания и редактирования заметки передаются формы."""
        urls_args = (('notes:add', None), ('notes:edit', (self.note.slug,)))
        self.client.force_login(self.author)
        for url, args in urls_args:
            with self.subTest():
                url = reverse(url, args=args)
                response = self.client.get(url)
        self.assertIn('form', response.context)
