# standard library
import re

# third party
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

# Django
from django.contrib.staticfiles.testing import LiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# local Django
from pom.pages.adminRegistrationPage import AdminRegistrationPage
from pom.pageUrls import PageUrls
from registration.tokens import account_activation_token
from shift.utils import (create_organization, create_country,
                         create_state, create_city)


class SignUpAdmin(LiveServerTestCase):
    """
    SignUpAdmin Class contains tests to register a admin User
    Tests included.

    Name Fields:
        - Test Null values
        - Test legit characters in first_name, last_name fields
        - Register admin with already registered username
        - Test length of name fields ( 30 char, limit)

    Password Field:
        - Check if password and confirm password are same

    Location Field (Address, City, State, Country):
        - Test Null Values
        - Test legit characters as per Models defined

    Email Field:
        - Test Null Values
        - Test uniqueness of field

    Phone Number Field:
        - Test Null Values
        - Test validity of number against country entered
        - Test legit characters as per Models defined

    Organization Field:
        - Test Null Values
        - Test legit characters as per Models defined

    Retention of fields:
        - Field values are checked to see that they
          are not lost when the page gets reloaded
    """

    @classmethod
    def setUpClass(cls):
        """Method to initiate class level objects.

        This method initiates Firefox WebDriver, WebDriverWait and
        the corresponding POM objects for this Test Class
        """
        firefox_options = Options()
        firefox_options.add_argument('-headless')
        cls.driver = webdriver.Firefox(firefox_options=firefox_options)
        cls.driver.implicitly_wait(5)
        cls.driver.maximize_window()
        cls.page = AdminRegistrationPage(cls.driver)
        cls.wait = WebDriverWait(cls.driver, 10)
        super(SignUpAdmin, cls).setUpClass()

    def setUp(self):
        """
        Method consists of statements to be executed before
        start of each test.
        """
        create_organization()
        # country created so that phone number can be checked
        create_country()
        create_state()
        create_city()

    def tearDown(self):
        """
        Method consists of statements to be executed at
        end of each test.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Class method to quit the Firefox WebDriver session after
        execution of all tests in class.
        """
        cls.driver.quit()
        super(SignUpAdmin, cls).tearDownClass()

    def verify_field_values(self, info):
        """
        Utility function to perform assertions on user information.
        :param info:  Iterable containing information of user.
        """
        page = self.page
        values = page.get_field_values()
        self.assertEqual(values['username'], info['username'])
        self.assertEqual(values['first_name'], info['first_name'])
        self.assertEqual(values['last_name'], info['last_name'])
        self.assertEqual(values['email'], info['email'])
        self.assertEqual(values['address'], info['address'])
        self.assertEqual(values['city'], info['city'])
        self.assertEqual(values['state'], info['state'])
        self.assertEqual(values['country'], info['country'])
        self.assertEqual(values['phone'], info['phone'])
        self.assertEqual(values['organization'], info['organization'])

    def test_null_values(self):
        """
        Test errors raised when creating user with null values.
        """
        page = self.page
        page.live_server_url = self.live_server_url
        page.get_admin_registration_page()

        entry = {
            'username': '',
            'password': '',
            'confirm_password': '',
            'first_name': '',
            'last_name': '',
            'email': '',
            'address': '',
            'city': '',
            'state': '',
            'country': '',
            'phone_number': '',
            'organization': ''
        }
        page.fill_registration_form(entry)
        self.assertNotEqual(page.get_help_blocks(), None)
        # Verify that 8 of the fields are compulsory
        self.assertEqual(len(page.get_help_blocks()), 8)

    def test_successful_registration(self):
        """
        Test registration of user with valid details.
        """
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()
        self.assertEqual(page.get_help_blocks(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )

    def test_user_registration_with_same_username(self):
        """
        Test error raised when user registers with
        username which already exists.
        """
        # Register valid admin user
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()
        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

        page.get_admin_registration_page()

        entry = entry = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'admin-email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_username_error_text(),
                         page.USER_EXISTS)

    def test_user_fills_different_passwords(self):
        """
        Test error raised when user inputs different passwords while
        registering.
        """
        # register valid administrator user
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()
        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )

        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username-1',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'admin-email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)
        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_password_error_text(),
                         page.NO_MATCH)

    def test_numeric_characters_in_first_and_last_name(self):
        """
        Test error raised when using numeric characters in
        first and last name while registering.
        """
        # Register valid admin user
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()
        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username-1',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name-1',
            'last_name': 'admin-last-name-1',
            'email': 'admin-email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_first_name_error_text(),
                         page.ENTER_VALID_VALUE)
        self.assertEqual(page.get_last_name_error_text(),
                         page.ENTER_VALID_VALUE)

    def test_special_characters_in_first_and_last_name(self):
        """
        Test error raised when using special characters in
        first and last name while registering.
        """
        # Register valid admin user
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()
        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'name-!@#$%^&*()',
            'last_name': 'name-!@#$%^&*()_',
            'email': 'admin-email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_first_name_error_text(),
                         page.ENTER_VALID_VALUE)
        self.assertEqual(page.get_last_name_error_text(),
                         page.ENTER_VALID_VALUE)

    def test_length_of_first_and_last_name(self):
        """
        Test error raised when registering with length of
        first and last name greater than thirty.
        """
        # Register valid admin user
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()
        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name-!@#$%^&*()_lolwatneedlength',
            'last_name': 'admin-last-name-!@#$%^&*()_lolwatneedlength',
            'email': 'admin-email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        self.assertNotEqual(page.get_help_blocks(), None)
        error_message = page.get_first_name_error_text()
        print(str(error_message))
        self.assertTrue(
            bool(
                re.search(r'Ensure this value has at most 30 characters',
                          str(error_message))))

        error_message = page.get_last_name_error_text()
        self.assertTrue(
            bool(
                re.search(r'Ensure this value has at most 30 characters',
                          str(error_message))))

    def test_email_field(self):
        """
        Test error raised when user tries to register with an email
        address which is already in use.
        """
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()

        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

        # Try to register admin again with same email address
        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username-1',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'admin-email@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        # Verify that user wasn't registered
        self.assertEqual(page.remove_i18n(self.driver.current_url),
                         self.live_server_url + page.admin_registration_page)
        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_email_error_text(),
                         'Administrator with this Email already exists.')

    def test_phone_in_different_country(self):
        """
        Test validation of phone number in a country.
        """
        page = self.page
        page.live_server_url = self.live_server_url
        page.get_admin_registration_page()
        entry = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'admin-email@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '022 2403 6606',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

        # Try to register admin with incorrect phone number for country
        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username-1',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'admin-email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '237937913',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        # verify that user wasn't registered
        self.assertEqual(page.remove_i18n(self.driver.current_url),
                         self.live_server_url + page.admin_registration_page)
        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_phone_error_text(),
                         page.INVALID_PHONE_FOR_COUNTRY)

    def test_phone_with_invalid_characters(self):
        """
        Test error raised while using invalid characters in phone number.
        """
        page = self.page
        page.live_server_url = self.live_server_url
        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'admin-email@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '022 2403 6606',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username-1',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'admin-email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '23&79^37913',
            'organization': 'admin-org'
        }
        page.fill_registration_form(entry)

        # Verify that user wasn't registered
        self.assertEqual(page.remove_i18n(self.driver.current_url),
                         self.live_server_url + page.admin_registration_page)
        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_phone_error_text(),
                         page.INVALID_PHONE)

    def test_organization_with_numeric_characters(self):
        """
        Test error raised while using numeric characters in organization name.
        """
        page = self.page
        page.live_server_url = self.live_server_url
        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username-1',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': '13 admin-org'
        }
        page.fill_registration_form(entry)

        # verify successful registration
        self.assertNotEqual(page.get_message_box(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        self.assertEqual(
            page.remove_i18n(self.driver.current_url),
            self.live_server_url + PageUrls.admin_registration_page
        )

    def test_organization_with_invalid_characters(self):
        """
        Test error raised while using invalid characters in organization name.
        """
        page = self.page
        page.live_server_url = self.live_server_url
        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username-2',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name',
            'email': 'email2@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India',
            'phone_number': '9999999999',
            'organization': '!$&admin-org'
        }
        page.fill_registration_form(entry)

        # verify that user wasn't registered
        self.assertEqual(page.remove_i18n(self.driver.current_url),
                         self.live_server_url + page.admin_registration_page)
        self.assertNotEqual(page.get_help_blocks(), None)
        self.assertEqual(page.get_organization_error_text(),
                         page.ENTER_VALID_VALUE)

    def test_ajax_load_states(self):
        response = self.client.post(
            '/registration/load_states/',
            {'country': 'India'}
        )
        self.assertEqual(response.status_code, 302)

    def test_ajax_load_cities(self):
        response = self.client.post(
            '/registration/load_cities/',
            {
                'country': 'India',
                'state': 'Uttarakhand'
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_ajax_check_states(self):
        response = self.client.post(
            '/registration/check_states/',
            {'country': 'India'}
        )
        self.assertEqual(response.status_code, 302)

    def test_activation_email(self):
        u1 = User.objects.create_user(
            username='admin',
            password='admin'
        )
        page = self.page
        page.live_server_url = self.live_server_url
        page.register_valid_details()
        self.assertEqual(page.get_help_blocks(), None)
        self.assertEqual(
            page.get_message_box_text(),
            page.CONFIRM_EMAIL_MESSAGE
        )
        uid = urlsafe_base64_encode(force_bytes(u1.pk))
        token = account_activation_token.make_token(u1)
        response = self.client.get(
            reverse('registration:activate', args=[uid, token])
        )
        self.assertEqual(response.status_code, 200)


# Retention test are buggy and unstable, issue is open to fix them
# https://github.com/systers/vms/pull/794
'''
    def test_field_value_retention_in_first_name_state_phone_organization(self):
        """
        Test field values are retained in first name, state,
        phone and organization when
        entered invalid information in form.
        """
        page = self.page
        page.live_server_url = self.live_server_url

        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name-3',
            'last_name': 'admin-last-name',
            'email': 'email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India 15',
            'phone_number': '99999.!9999',
            'organization': '@#admin-org'
        }
        page.fill_registration_form(entry)

        # Verify that user wasn't registered and
        # that field values are not erased
        self.assertEqual(page.remove_i18n(self.driver.current_url),
                         self.live_server_url + page.admin_registration_page)
        details = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name-3',
            'last_name': 'admin-last-name',
            'email': 'email1@systers.org',
            'address': 'admin-address',
            'city': 'Roorkee',
            'state': 'Uttarakhand',
            'country': 'India 15',
            'phone_number': '99999.!9999',
            'organization': '@#admin-org'
        }
        self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        self.verify_field_values(details)

    def test_field_value_retention_in_last_name_address_city_country(self):
        """
        Test field values are retained in last name, address,
        city and country when entered
        invalid information in form.
        """
        page = self.page
        page.live_server_url = self.live_server_url

        page.get_admin_registration_page()

        entry = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name-3',
            'email': 'email1@systers.org',
            'address': 'admin-address$@!',
            'city': 'Roorkee#$',
            'state': 'Uttarakhand',
            'country': 'India 15',
            'phone_number': '99999.!9999',
            'organization': '@#admin-org'
        }
        page.fill_registration_form(entry)

        # verify that user wasn't registered and
        # that field values are not erased
        self.assertEqual(page.remove_i18n(self.driver.current_url),
                         self.live_server_url + page.admin_registration_page)
        details = {
            'username': 'admin-username',
            'password': 'admin-password!@#$%^&*()_',
            'confirm_password': 'admin-password!@#$%^&*()_',
            'first_name': 'admin-first-name',
            'last_name': 'admin-last-name-3',
            'email': 'email1@systers.org',
            'address': 'admin-address$@!',
            'city': 'Roorkee#$',
            'state': 'Uttarakhand',
            'country': 'India 15',
            'phone_number': '99999.!9999',
            'organization': '@#admin-org'
        }
        self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        self.verify_field_values(details)
'''
