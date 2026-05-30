import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users
#новый
def test_display_users_empty_db(setup_database, capsys):
    """Тест отображения пользователей при пустой БД."""
    display_users()
    captured = capsys.readouterr()
    assert captured.out == "", "При пустой БД не должно быть вывода"
#новый

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""


def test_add_duplicate_user(setup_database, connection):
    """Тест добавления пользователя с существующим логином."""
    add_user('duplicate', 'dup1@example.com', 'pass1')
    result = add_user('duplicate', 'dup2@example.com', 'pass2')
    assert result is False, "Добавление дубликата должно вернуть False"
    
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='duplicate';")
    count = cursor.fetchone()[0]
    assert count == 1, "Дубликат не должен добавляться в БД"

def test_successful_authentication(setup_database, connection):
    """Тест успешной аутентификации."""
    add_user('authuser', 'auth@example.com', 'correctpass')
    assert authenticate_user('authuser', 'correctpass') is True

def test_authenticate_nonexistent_user(setup_database, connection):
    """Тест аутентификации несуществующего пользователя."""
    assert authenticate_user('ghost', 'anypass') is False

def test_authenticate_wrong_password(setup_database, connection):
    """Тест аутентификации с неправильным паролем."""
    add_user('wrongpassuser', 'wrong@example.com', 'realpass')
    assert authenticate_user('wrongpassuser', 'wrongpass') is False

def test_display_users_output(setup_database, connection, capsys):
    """Тест отображения списка пользователей (вывод в консоль)."""
    add_user('display1', 'd1@example.com', 'p1')
    add_user('display2', 'd2@example.com', 'p2')
    
    display_users()
    captured = capsys.readouterr()
    
    assert 'Логин: display1, Электронная почта: d1@example.com' in captured.out
    assert 'Логин: display2, Электронная почта: d2@example.com' in captured.out

def test_add_user_with_empty_fields(setup_database, connection):
    """Тест добавления пользователя с пустыми полями."""
    result = add_user('', '', '')
    assert result is not False, "Пустые поля могут быть добавлены (БД не запрещает)"
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='';")
    user = cursor.fetchone()
    assert user is not None

def test_authenticate_case_sensitivity(setup_database, connection):
    """Тест чувствительности к регистру логина и пароля."""
    add_user('CaseUser', 'case@example.com', 'SecretPass')
    
    assert authenticate_user('caseuser', 'SecretPass') is False
    assert authenticate_user('CaseUser', 'secretpass') is False
    assert authenticate_user('CaseUser', 'SecretPass') is True



def test_add_user_special_characters(setup_database, connection):
    """Тест добавления пользователя со спецсимволами."""
    add_user('user@#$%', 'test@site.com', 'p@ssw0rd!')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='user@#$%';")
    user = cursor.fetchone()
    assert user is not None

def test_add_user_long_data(setup_database, connection):
    """Тест добавления очень длинных строк (граничный тест)."""
    long_username = 'a' * 500
    long_email = 'b' * 500 + '@example.com'
    long_password = 'c' * 1000
    
    result = add_user(long_username, long_email, long_password)
    assert result is True
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (long_username,))
    user = cursor.fetchone()
    assert user is not None