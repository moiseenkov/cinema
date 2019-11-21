from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from booking.models import Movie
from booking.tests import helper
from booking.tests.helper import LoggedInUserTestCase, LoggedInAdminTestCase


class TestURLMovies(TestCase):
    def setUp(self) -> None:
        self.url_list = reverse('movie-list')
        self.movies_data = [
            {
                'name': 'Movie 1',
                'duration': 128
            },
            {
                'name': 'Movie 2',
                'duration': 256,
                'premiere_year': 2019
            }
        ]
        movies = [Movie(**info) for info in self.movies_data]
        Movie.objects.bulk_create(movies)
        self.movies = helper.get_movies_dict()

    def test_url_movies_get_list(self):
        response = self.client.get(path=self.url_list, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))
        self.assertEqual(len(response.data['results']), len(self.movies))
        for expected in self.movies:
            with self.subTest(expected=expected):
                movies_found = [movie_ for movie_ in response.data['results'] if movie_['id'] == expected['id']]
                self.assertEqual(len(movies_found), 1)
                self.assertSetEqual(set(expected.items()), set(movies_found[0].items()))

    def test_url_movies_get_detail(self):
        for movie in self.movies:
            with self.subTest(movie=movie):
                response = self.client.get(path=reverse('movie-detail', args=[movie['id']]), data={})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsInstance(response.data, dict)
                self.assertDictEqual(response.data, movie)

    def test_url_movies_post(self):
        data = {
            'name': 'New name'
        }
        response = self.client.post(path=self.url_list, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_movies_put_patch_delete(self):
        movie = self.movies[0]
        url = reverse('movie-detail', args=[movie['id']])
        data = {
            'name': 'Changed name by unauthorised user'
        }

        with self.subTest():
            response = self.client.put(path=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest():
            response = self.client.patch(path=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest():
            response = self.client.delete(path=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestURLMoviesUser(LoggedInUserTestCase):
    def setUp(self) -> None:
        self.url_list = reverse('movie-list')
        self.movies_data = [
            {
                'name': 'Movie 1',
                'duration': 128
            },
            {
                'name': 'Movie 2',
                'duration': 256,
                'premiere_year': 2019
            }
        ]
        movies = [Movie(**info) for info in self.movies_data]
        Movie.objects.bulk_create(movies)
        self.movies = helper.get_movies_dict()
        super(TestURLMoviesUser, self).setUp()

    def test_url_movies_get_list(self):
        response = self.client.get(path=reverse('movie-list'), data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))
        self.assertEqual(len(response.data['results']), len(self.movies))
        for expected in self.movies:
            with self.subTest(expected=expected):
                movies_found = [movie_ for movie_ in response.data['results'] if movie_['id'] == expected['id']]
                self.assertEqual(len(movies_found), 1)
                self.assertSetEqual(set(expected.items()), set(movies_found[0].items()))

    def test_url_movies_get_detail(self):
        for movie in self.movies:
            with self.subTest(movie=movie):
                response = self.client.get(path=reverse('movie-detail', args=[movie['id']]), data={},
                                           HTTP_AUTHORIZATION=f'Bearer {self.token}')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsInstance(response.data, dict)
                self.assertDictEqual(response.data, movie)

    def test_url_movies_post(self):
        data = {
            'name': 'New name'
        }
        response = self.client.post(path=reverse('movie-list'), data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_movies_put_patch_delete(self):
        movie = self.movies[0]
        url = reverse('movie-detail', args=[movie['id']])
        data = {
            'name': 'Changed name by unauthorised user'
        }

        with self.subTest():
            response = self.client.put(path=url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest():
            response = self.client.patch(path=url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest():
            response = self.client.delete(path=url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestURLMoviesAdmin(LoggedInAdminTestCase):
    def setUp(self) -> None:
        super(TestURLMoviesAdmin, self).setUp()
        self.new_movie_name = 'Test movie'
        self.new_movie_data = {
            'name': self.new_movie_name,
            'duration': 15,
            'premiere_year': 2017
        }

    def test_url_movies_put(self):
        movie = Movie(**self.new_movie_data)
        movie.save()
        self.assertIsNotNone(movie)

        data = {
            'name': 'Changed name'
        }
        response = self.client.put(path=reverse('movie-detail', args=[movie.pk]), data=data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['duration'] = -10
        response = self.client.put(path=reverse('movie-detail', args=[movie.pk]), data=data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['name'] = 'Another new name'
        data['duration'] = 200
        data['premiere_year'] = 2018
        response = self.client.put(path=reverse('movie-detail', args=[movie.pk]), data=data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data['id'] = movie.pk
        self.assertDictEqual(response.data, data)

    def test_url_movies_post(self):
        response = self.client.post(path=reverse('movie-list'), data=self.new_movie_data,
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_movie = Movie.objects.filter(name=self.new_movie_name).first()
        self.assertIsNotNone(new_movie)

        expected_data = self.new_movie_data.copy()
        expected_data['id'] = new_movie.pk
        self.assertDictEqual(response.data, expected_data)

    def test_url_movies_post_empty(self):
        response = self.client.post(path=reverse('movie-list'), data={},
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_movies_post_already_exist(self):
        movie = Movie(**self.new_movie_data)
        movie.save()
        response = self.client.post(path=reverse('movie-list'), data=self.new_movie_data,
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_movies_patch(self):
        movie = Movie(**self.new_movie_data)
        movie.save()

        changed_name = 'Changed name'
        data = {
            'name': changed_name
        }
        response = self.client.patch(path=reverse('movie-detail', args=[movie.pk]), data=data,
                                     content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('name', None))
        self.assertEqual(response.data['name'], changed_name)

    def test_url_movies_patch_already_exist(self):
        movie1 = Movie(**self.new_movie_data)
        movie1.save()
        movie2 = Movie(name='Second movie',
                       duration=self.new_movie_data['duration'],
                       premiere_year=self.new_movie_data['premiere_year'])
        movie2.save()
        data = {
            'name': movie2.name
        }
        response = self.client.patch(path=reverse('movie-detail', args=[movie1.pk]), data=data,
                                     content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_movies_delete(self):
        movie = Movie(**self.new_movie_data)
        movie.save()
        self.assertIsNotNone(movie)

        response = self.client.delete(path=reverse('movie-detail', args=[movie.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(path=reverse('movie-detail', args=[movie.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
