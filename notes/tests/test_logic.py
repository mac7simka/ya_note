from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNotes(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'slug'
    SLUG_LENGHT = 100

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.form_data['slug'] = self.NOTE_SLUG
        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически.
        """
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])[:self.SLUG_LENGHT]
        self.assertEqual(expected_slug, note.slug)


class TestNotesEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'
    NOTE_EDIT_TITLE = 'Новый заголовок'
    NOTE_EDIT_TEXT = 'Новый текст заметки'
    NOTE_EDIT_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, author=cls.author)
        cls.form_data = {
            'title': cls.NOTE_EDIT_TITLE,
            'text': cls.NOTE_EDIT_TEXT,
            'slug': cls.NOTE_EDIT_SLUG
        }
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response,
                             reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_EDIT_TITLE)
        self.assertEqual(self.note.text, self.NOTE_EDIT_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_EDIT_SLUG)

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.not_author_client.post(
            self.url_edit, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response,
                             reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        response = self.not_author_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
