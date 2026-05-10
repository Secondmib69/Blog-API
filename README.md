# Blog API

A RESTful Blog API built with Django and Django REST Framework. It supports user management, JWT cookie authentication, blog posts with public/private visibility, comments with moderation, likes, search, ordering, pagination, OpenAPI schema generation, and optional local or S3-compatible media storage.

## Features

- Custom user model with profile fields such as job title, bio, and phone number
- JWT authentication using `dj-rest-auth` and Simple JWT cookies
- User registration and account endpoints through `django-allauth` / `dj-rest-auth`
- CRUD operations for blog posts
- Public and private post visibility
- Slug-based post detail routes
- Image upload support for posts
- Like/unlike posts with like count
- Comment creation, listing, editing, deleting, and staff approval workflow
- Role-aware permissions for users, posts, and comments
- Search, filtering, ordering, and pagination
- Swagger UI and OpenAPI schema via `drf-spectacular`
- Docker and Docker Compose setup with PostgreSQL
- Optional S3-compatible storage support

## Tech Stack

- Python 3.12+
- Django 6
- Django REST Framework
- PostgreSQL
- Simple JWT
- dj-rest-auth
- django-allauth
- django-filter
- drf-spectacular
- django-storages / boto3
- Pillow
- Docker and Docker Compose

## Project Structure

```text
Blog-API/
|-- blog/                 # Blog app: models, serializers, views, urls, permissions
|-- core/                 # Django project settings and root urls
|-- manage.py             # Django management script
|-- requirements.txt      # Python dependencies
|-- Dockerfile            # Docker image definition
|-- docker-compose.yml    # Django + PostgreSQL services
|-- .env.example          # Example environment variables
`-- README.md
```

## Getting Started

### Prerequisites

Make sure you have one of the following setups installed:

- Python 3.12+ and PostgreSQL, or
- Docker and Docker Compose

### Environment Variables

Create your local `.env` file from the example:

```bash
cp .env.example .env
```

Configure the values in `.env`:

```env
DJANGO_SECRET_KEY=your_generated_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=blog_db
POSTGRES_USER=blog_user
POSTGRES_PASSWORD=strong_password
DB_HOST=localhost
DJANGO_STORAGE=local
```

Generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated value into `DJANGO_SECRET_KEY` in your `.env` file. Use `DJANGO_DEBUG=True` for local development and set it to `False` in production. Set `DJANGO_ALLOWED_HOSTS` to a comma-separated list of hostnames or IP addresses that can serve the app.

For Docker Compose, use `DB_HOST=postgres` because the database service name is `postgres`.

> Note: `.env` should not be committed to GitHub. Keep secrets out of version control.

## Installation Without Docker

1. Clone the repository:

```bash
git clone https://github.com/your-username/Blog-API.git
cd Blog-API
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file, generate `DJANGO_SECRET_KEY`, and set `DB_HOST=localhost`.

5. Run migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## Running With Docker

1. Create a `.env` file:

```bash
cp .env.example .env
```

2. Set Docker database host:

```env
DB_HOST=postgres
```

3. Build and start the containers:

```bash
docker compose up --build
```

The Django app will run on:

```text
http://127.0.0.1:8000/
```

PostgreSQL is exposed on host port `5431` and container port `5432`.

## API Documentation

Swagger UI:

```text
GET /api/docs/
```

OpenAPI schema:

```text
GET /api/schema/
```

Admin panel:

```text
GET /admin/
```

## Authentication Endpoints

Authentication is provided by `dj-rest-auth` and registration is provided by `dj-rest-auth` with `django-allauth`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login/` | Log in and receive JWT cookies |
| POST | `/auth/logout/` | Log out |
| POST | `/auth/password/reset/` | Request password reset |
| POST | `/auth/password/reset/confirm/<uidb64>/<token>/` | Confirm password reset |
| POST | `/auth/password/change/` | Change authenticated user's password |
| GET | `/auth/user/` | Get current authenticated user |
| PUT/PATCH | `/auth/user/` | Update current authenticated user |
| POST | `/auth/registration/` | Register a new account |
| POST | `/auth/registration/verify-email/` | Verify registration email, if enabled |
| POST | `/auth/registration/resend-email/` | Resend verification email, if enabled |

## Blog Endpoints

Base URL for blog resources:

```text
/blog/
```

### Users

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| GET | `/blog/users/` | List users | Public, role-aware output |
| POST | `/blog/users/` | Create user | Superuser only |
| GET | `/blog/users/{id}/` | Retrieve user profile | Public, role-aware output |
| PUT/PATCH | `/blog/users/{id}/` | Update user | Owner/staff/superuser by role |
| DELETE | `/blog/users/{id}/` | Delete user | Staff/superuser by role |

Supported query parameters:

| Parameter | Description |
|---|---|
| `search` | Search users by username, first name, last name, and job title. Staff can also search email and phone. |
| `ordering` | Order by `date_joined`. Use `-date_joined` for descending order. |
| `slug` | List users who liked a specific post slug. |
| `is_active` | Staff-only filter. |
| `is_staff` | Staff-only filter. |
| `is_superuser` | Staff-only filter. |
| `page` | Page number for paginated results. |

### Posts

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| GET | `/blog/posts/` | List posts | Public for public posts |
| POST | `/blog/posts/` | Create a post | Authenticated users |
| GET | `/blog/posts/{slug}/` | Retrieve post detail | Public for public posts |
| PUT/PATCH | `/blog/posts/{slug}/` | Update a post | Post author |
| DELETE | `/blog/posts/{slug}/` | Delete a post | Post author, staff, or superuser |
| POST | `/blog/posts/{slug}/like/` | Like or unlike a post | Authenticated users except post author |

Supported query parameters:

| Parameter | Description |
|---|---|
| `search` | Search by title, content, or author username. |
| `ordering` | Order by `created`, `updated`, or `likes_count`. Prefix with `-` for descending order. |
| `user_id` | Filter posts by author ID. |
| `status` | Staff-only filter for `PB` public or `PV` private. |
| `page` | Page number for paginated results. |

Example post request body:

```json
{
  "title": "My First Post",
  "content": "This is the post content.",
  "status": "PB"
}
```

Post status values:

| Value | Meaning |
|---|---|
| `PB` | Public |
| `PV` | Private |

### Comments

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| GET | `/blog/posts/{slug}/comments/` | List comments for a post | Public for active comments |
| POST | `/blog/posts/{slug}/comments/` | Create a comment | Authenticated users |
| GET | `/blog/posts/{slug}/comments/{id}/` | Retrieve a comment | Public for active comments |
| PUT/PATCH | `/blog/posts/{slug}/comments/{id}/` | Update comment or approve as staff | Comment owner/staff |
| DELETE | `/blog/posts/{slug}/comments/{id}/` | Delete a comment | Comment owner/staff |

Supported query parameters:

| Parameter | Description |
|---|---|
| `search` | Search comments by username. |
| `ordering` | Order by `created`. Use `-created` for descending order. |
| `is_active` | Staff-only filter for moderation. |
| `limit` | Number of comments to return. |
| `offset` | Offset for pagination. |

Example comment request body:

```json
{
  "body": "Great article!"
}
```

Staff can approve or hide a comment with:

```json
{
  "is_active": true
}
```

## Permissions Summary

- Anonymous users can read public posts, public profiles, and active comments.
- Authenticated users can create posts and comments.
- Post authors can update their own posts.
- Post authors cannot like their own posts.
- Comment owners can read and delete their own active comments.
- Staff users can moderate comments and access staff-only filters.
- Superusers have the highest level of user-management permissions.

## Pagination, Search, Filtering, and Ordering

The API uses Django REST Framework pagination.

- Default page size: `5`
- Post list pagination: page-number pagination
- User list pagination: page-number pagination
- Comment list pagination: limit-offset pagination

Common examples:

```text
/blog/posts/?search=django
/blog/posts/?ordering=-likes_count
/blog/posts/?user_id=1
/blog/posts/my-post/comments/?limit=10&offset=0
/blog/users/?search=john
```

## Media Storage

The project supports two storage modes:

| Mode | Description |
|---|---|
| `local` | Stores uploaded media files in the local `media/` directory. |
| `s3` | Uses S3-compatible object storage through `django-storages` and `boto3`. |

Set the storage mode in `.env`:

```env
DJANGO_STORAGE=local
```

For S3-compatible storage, set `DJANGO_STORAGE=s3` and provide the required storage credentials in your environment.

## Useful Commands

Run migrations:

```bash
python manage.py migrate
```

Create migrations:

```bash
python manage.py makemigrations
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run development server:

```bash
python manage.py runserver
```

Run tests:

```bash
python manage.py test
```

Generate OpenAPI schema:

```bash
python manage.py spectacular --file schema.yml
```

## GitHub Checklist

Before pushing to GitHub:

- Keep `.env` out of version control.
- Commit `.env.example` instead of real credentials.
- Remove local database files if they are not needed in the repository.
- Run migrations and tests.
- Update the repository URL in this README.

## License

Add your preferred license here, for example MIT License.
