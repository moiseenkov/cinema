from django.urls import reverse
from rest_framework import status

from booking.models import Movie

from booking.tests.helper import LoggedInTestCase


class MoviesDetailPositiveTestCase(LoggedInTestCase):
    def test_url_movies_detail_positive_GET(self):
        movie = Movie(name='Test movie', duration=120, premiere_year=2019)
        movie.save()
        expected_response = {
            'id': movie.pk,
            'name': movie.name,
            'duration': movie.duration,
            'premiere_year': movie.premiere_year,
        }
        response = self.client.get(path=reverse('movie-detail', args=[movie.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_movies_detail_positive_PUT_admin(self):
        input_data = {
            'name': 'Test name',
            'duration': 120,
            'premiere_year': 1999,
        }
        movie = Movie(name='Name', duration=100)
        movie.save()
        response = self.client.put(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_response = {
            'id': movie.pk,
            'name': input_data['name'],
            'duration': input_data['duration'],
            'premiere_year': input_data['premiere_year'],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_movies_detail_positive_PATCH_admin(self):
        movie = Movie(name='Name', duration=120, premiere_year=1999)
        movie.save()
        input_data = {
            'name': 'New name',
        }
        response = self.client.patch(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                     content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        movie.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(movie.name, input_data['name'])
        self.assertEqual(response.data['name'], input_data['name'])

    def test_url_movies_detail_positive_DELETE_admin(self):
        movie = Movie(name='Name', duration=120, premiere_year=1999)
        movie.save()
        pk = movie.pk
        response = self.client.delete(path=reverse('movie-detail', args=[pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        movies = Movie.objects.filter(pk=pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(movies.count(), 0)


class MoviesDetailNegativeTestCase(LoggedInTestCase):
    def test_url_movies_detail_negative_GET_unknown(self):
        movies = [Movie(name='Name', duration=120, premiere_year=year) for year in [2000, 2001, 2002]]
        Movie.objects.bulk_create(movies)
        ids = [movie.pk for movie in Movie.objects.all()]
        pk = 0
        while pk in ids:
            pk += 1

        response = self.client.get(path=reverse('movie-detail', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_movies_detail_negative_PUT_user(self):
        movie = Movie(name='Name', duration=120, premiere_year=1999)
        movie.save()
        input_data = {
            'name': 'Test name',
            'duration': 16,
            'premiere_year': 2005,
        }
        response = self.client.put(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_movies_detail_negative_PUT_unauthorized(self):
        movie = Movie(name='Name', duration=120, premiere_year=1999)
        movie.save()
        input_data = {
            'name': 'Test name',
            'duration': 16,
            'premiere_year': 2005,
        }
        response = self.client.put(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_movies_detail_negative_PATCH_user(self):
        movie = Movie(name='Name', duration=120, premiere_year=1999)
        movie.save()
        input_data = {
            'name': 'New name',
        }
        response = self.client.patch(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                     content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        movie.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_movies_detail_negative_PATCH_unauthorized(self):
        movie = Movie(name='Name', duration=120, premiere_year=1999)
        movie.save()
        input_data = {
            'name': 'New name',
        }
        response = self.client.patch(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                     content_type='application/json')
        movie.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_movies_detail_negative_PATCH_incorrect_input(self):
        movie = Movie(name='Name', duration=120, premiere_year=1999)
        movie.save()

        with self.subTest():
            input_data = {
                'name': '',
                'duration': 120,
                'premiere_year': 2000,
            }
            response = self.client.patch(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest():
            input_data = {
                'name': 'Name for movie',
                'duration': 0,
                'premiere_year': 2000,
            }
            response = self.client.patch(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest():
            input_data = {
                'name': 'Name for movie',
                'duration': 20,
                'premiere_year': 1700,
            }
            response = self.client.patch(path=reverse('movie-detail', args=[movie.pk]), data=input_data,
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_movies_detail_negative_DELETE_user(self):
        movie_data = {
            'name': 'Name for movie',
            'duration': 20,
            'premiere_year': 2000,
        }
        movie = Movie(**movie_data)
        movie.save()
        pk = movie.pk
        response = self.client.delete(path=reverse('movie-detail', args=[movie.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        movies = Movie.objects.filter(pk=pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(movies.count(), 1)
        movie = movies[0]
        self.assertEqual(movie.pk, pk)
        self.assertEqual(movie.name, movie_data['name'])
        self.assertEqual(movie.duration, movie_data['duration'])
        self.assertEqual(movie.premiere_year, movie_data['premiere_year'])

    def test_url_movies_detail_negative_DELETE_unauthorized(self):
        movie_data = {
            'name': 'Name for movie',
            'duration': 20,
            'premiere_year': 2000,
        }
        movie = Movie(**movie_data)
        movie.save()
        pk = movie.pk
        response = self.client.delete(path=reverse('movie-detail', args=[movie.pk]))

        movies = Movie.objects.filter(pk=pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(movies.count(), 1)
        movie = movies[0]
        self.assertEqual(movie.pk, pk)
        self.assertEqual(movie.name, movie_data['name'])
        self.assertEqual(movie.duration, movie_data['duration'])
        self.assertEqual(movie.premiere_year, movie_data['premiere_year'])


class MoviesListPositiveTestCase(LoggedInTestCase):
    def setUp(self) -> None:
        self.url_list = reverse('movie-list')
        super(MoviesListPositiveTestCase, self).setUp()

    def test_url_movie_list_positive_GET(self):
        sub_test_parameters = [
            {
                # Unauthorized user
                'path': self.url_list,
            },
            {
                # Authorized user
                'path': self.url_list,
                'HTTP_AUTHORIZATION': f'Bearer {self.user_token}',
            },
            {
                # Admin
                'path': self.url_list,
                'HTTP_AUTHORIZATION': f'Bearer {self.admin_token}',
            },
        ]
        movies = [Movie(name="Name", duration=120, premiere_year=year) for year in [2000, 2001, 2002]]
        Movie.objects.bulk_create(movies)
        expected_response = [
            {
                'id': movie.pk,
                'name': movie.name,
                'duration': movie.duration,
                'premiere_year': movie.premiere_year,
            } for movie in Movie.objects.all().order_by('-pk')
        ]
        for request_parameter_set in sub_test_parameters:
            with self.subTest(request_parameter_Set=request_parameter_set):
                response = self.client.get(**request_parameter_set)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsNotNone(response.data.get('results', None))
                for received, expected in zip(response.data['results'], expected_response):
                    self.assertDictEqual(dict(received), expected)

    def test_url_movie_list_positive_POST_admin(self):
        data = {
            'name': 'Name',
            'duration': 20,
            'premiere_year': 2000,
        }
        response = self.client.post(path=self.url_list, data=data, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        movies = Movie.objects.filter(name=data['name'])

        self.assertEqual(movies.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        movie = movies[0]
        expected_response = data.copy()
        expected_response['id'] = movie.pk
        self.assertDictEqual(response.data, expected_response)


class MoviesListNegativeTestCase(LoggedInTestCase):
    def setUp(self) -> None:
        self.url_list = reverse('movie-list')
        super(MoviesListNegativeTestCase, self).setUp()

    def test_url_movie_list_negative_POST_unauthorized(self):
        data = {
            'name': 'Name',
            'duration': 20,
            'premiere_year': 2000,
        }
        response = self.client.post(path=self.url_list)
        movies = Movie.objects.filter(name=data['name'])

        self.assertEqual(movies.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_movie_list_negative_POST_user(self):
        data = {
            'name': 'Name',
            'duration': 20,
            'premiere_year': 2000,
        }
        response = self.client.post(path=self.url_list, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        movies = Movie.objects.filter(name=data['name'])

        self.assertEqual(movies.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_movie_list_negative_POST_incorrect_input(self):
        cases = [
            {
                'name': 'Name',
                'duration': 20,
            },
            {
                'name': 'Name',
                'premiere_year': 2000,
            },
            {
                'duration': 20,
                'premiere_year': 2000,
            },
            {
                'name': '',
                'duration': '',
                'premiere_year': '',
            },
            {
                'name': 'Name',
                'duration': -12,
                'premiere_year': 1999,
            },
            {
                'name': 'Name',
                'duration': 102,
                'premiere_year': 1700,
            },
            {
                'name': 'Name',
                'duration': '102',
                'premiere_year': 'two thousand',
            },
        ]
        movies_control = list(Movie.objects.all().order_by('-pk'))
        for case in cases:
            with self.subTest(case=case):
                response = self.client.post(path=self.url_list, data=case,
                                            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
                movies = list(Movie.objects.all().order_by('-pk'))

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(len(movies_control), len(movies))
                for received, expected in zip(movies_control, movies):
                    self.assertEqual(received.pk, expected.pk)
                    self.assertEqual(received.name, expected.name)
                    self.assertEqual(received.rows_count, expected.rows_count)
                    self.assertEqual(received.rows_size, expected.rows_size)
