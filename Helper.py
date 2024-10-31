import re
from collections import UserDict
from datetime import datetime, timedelta
import pickle


def parse_input(user_input):
    parts = user_input.split()
    cmd = parts[0].strip().lower()
    args = parts[1:]  # Отримати всі аргументи як плоский список
    return cmd, args


def normalize_phone(number):
    # Видалення всіх символів, які не є цифрами або знаком "+"
    number = re.sub(r"[^\d+]", "", number)

    # Перевірка на різні формати телефонних номерів
    if len(number) < 10:
        return "Invalid phone number. The number must have not less than 10 digits: " + number
    elif len(number) == 10 and number.isdigit():
        return '+38' + number  # 10 цифр
    elif len(number) == 11 and number.startswith("+0") and number[2:].isdigit():
        return '+380' + number[2:]  # 10 цифр
    elif len(number) == 10 and number.startswith("+") and number[1:].isdigit():
        return '+380' + number[1:]  # 10 цифр
    elif len(number) == 12 and number.isdigit():
        return "+" + number  # 12 цифр без +
    elif len(number) == 13 and number.startswith("+") and number[1:].isdigit():
        return number  # + та 12 цифр
    elif len(number) == 13 and number.startswith("+38") and number[3:].isdigit() and len(number[3:]) == 10:
        return number  # +38 та 10 цифр
    elif len(number) == 12 and number.startswith("380") and number[3:].isdigit() and len(number[3:]) == 9:
        return "+" + number  # 380 та 9 цифр
    elif len(number) == 11 and number.startswith("0") and number[1:].isdigit():
        return "+38" + number[1:]  # + та 10 цифр, що починаються з 0
    else:
        return f"Invalid phone number: {number}. The number must have not less than 10 digits."
    return None


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, phones=None):
        self.numbers = list(phones) if phones else []
        self.value = []
        self._normalize_all_phones()

    def _normalize_all_phones(self):
        for number in self.numbers:
            normalized_phone = normalize_phone(number)
            if isinstance(normalized_phone, str):
                self.value.append(normalized_phone)
            else:
                raise ValueError(f"Invalid phone number: {number}. The number must have not less than 10 digits.")

    def add_phone(self, number):
        normalized_number = normalize_phone(number)
        if isinstance(normalized_number, str) and not normalized_number.startswith("Invalid"):
            if normalized_number not in self.value:
                self.value.append(normalized_number)
        else:
            raise ValueError(f"Invalid phone number: {number}. The number must have not less than 10 digits.")

    def find_phone(self, number):
        normalized_phone_number = normalize_phone(number)
        return normalized_phone_number in self.value

    def edit_phone(self, old_number, new_number):
        for index, num in enumerate(self.value):
            if num == normalize_phone(old_number):
                self.value[index] = normalize_phone(new_number)  # Оновлюємо значення
                return True
            return False

    def remove_phone(self):
        self.value = []


class Birthday(Field):
    def __init__(self, value):
        self.value = self._validate_birthday(value)

    def _validate_birthday(self, value):
        try:
            # Перетворення рядка на об'єкт datetime
            datetime.strptime(value, "%d.%m.%Y")
            return value  # Повертаємо коректну дату у форматі рядка
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    @input_error
    @staticmethod
    def add_birthday_to_contact(name, birthday):
        name.add_birthday(birthday)
        return f"Birthday {birthday} added for {name}."

    @input_error
    @staticmethod
    def show_birthday_of_contact(name):
        if name.birthday:
            return f"{name.name.value}'s birthday is {name.birthday.value}."
        return f"{name.name.value} does not have a birthday set."

    def change_birthday(self, new_birthday):
        self.value = new_birthday

    def remove_birthday(self):
        self.value = None


    @staticmethod
    def get_upcoming_birthdays(book):
        upcoming_birthdays = []
        today = datetime.now().date()

        for contact in book.values():
            if contact.birthday:
                birthday = datetime.strptime(contact.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if today <= birthday_this_year <= today + timedelta(days=7):
                    upcoming_birthdays.append({
                        "name": contact.name.value,
                        "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")
                    })

        return upcoming_birthdays


class Record:
    def __init__(self, name, phones=None, birthday=None, email=None):
        self.name = Name(name)
        self.phones = Phone(phones) if phones else Phone()  # Якщо телефони не передані, створити пустий Phone
        self.email = email
        if birthday:
            self.birthday = Birthday(birthday)
        else:
            self.birthday = None


    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_record(self, phones):
        for number in phones:
            normalized_number = normalize_phone(number)
            if normalized_number:
                self.phones.add_phone(normalized_number)  # Використовуємо метод add_phone

    def find_record(self, phones):
        for phone in self.phones:
            if phone.find_phone(normalize_phone(phones)):
                return phone.value
        return None

    def edit_record(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.find_phone(normalize_phone(old_phone)):
                phone.edit_phone(old_phone, new_phone)
                return True
        return False

    def add_email(self, email):
        self.email = email


    def remove_record(self, phones):
        self.phones = [phone for phone in self.phones if not phone.find_phone(normalize_phone(phones))]

    def __str__(self):
        phones = ', '.join(self.phones.value) if self.phones else ''
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        email = f", email: {self.email}" if self.email else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday_str}{email}"


class AddressBook(UserDict):
    def add_address(self, address):
        if isinstance(address.name.value, str):
            self.data[address.name.value] = address
        else:
            raise TypeError("Contact name must be a string.")

    def add_contact(self, name, phones, birthday=None, email=None):
        for phone in phones:
            normalized_number = normalize_phone(phone)
            if not isinstance(normalized_number, str) and len(normalized_number) < 10:
                raise ValueError(f"Invalid phone number: {phone}. The number must have not less than 10 digits.")

        new_address = Record(name, phones, birthday, email)
        self.data[name.value] = new_address

    def find_address(self, query):
        # Перевіряємо, чи це ім'я (алфавітні символи) або телефонний номер
        if query.isdigit() or query.startswith("+"):
            normalized_number = normalize_phone(query)  # Нормалізуємо номер для пошуку
            for record in self.data.values():
                for phone in record.phones:
                    if normalized_number in phone.value:
                        return record
        else:
            # Пошук за ім'ям
            return self.data.get(query, None)
        return None

    def edit_address(self, name, new_address):
        self.data[name] = new_address

    def delete_address(self, name):
        if name in self.data:
            del self.data[name]


def load_data(filename = 'addressbook.pkl'):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def save_data(book, filename = 'addressbook.pkl'):
    with open(filename,'wb') as f:
        pickle.dump(book, f)


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":

            if len(args) < 2:
                print("Error: Input requires at least two arguments: name and phone.")
                continue

            name = args[0]
            phone = args[1]
            phone2 = None
            birthday = None
            email = None

            # Проходимо через всі аргументи і призначаємо їх відповідним полям
            for arg in args[2:]:
                if re.match(r"^\d{10,13}$", arg):  # Перевіряємо, чи це телефонний номер
                    if not phone2:
                        phone2 = arg  # Призначаємо другий номер
                    else:
                        print(f"Warning: Ignoring additional phone number {arg}.")
                elif re.match(r"\d{2}\.\d{2}\.\d{4}$", arg):  # Перевіряємо формат дати
                    birthday = arg
                elif re.match(r"[^@]+@[^@]+\.[^@]+", arg):  # Перевіряємо формат електронної пошти
                    email = arg
                else:
                    print(f"Warning: Ignoring invalid argument '{arg}'.")
            # Перевірка на валідність основного номера телефону
            normalized_phone = normalize_phone(phone)
            if isinstance(normalized_phone, str) and normalized_phone.startswith("Invalid"):
                print(normalized_phone)  # Виводимо повідомлення про помилку
                continue  # Пропускаємо ітерацію, не створюючи контакт
            # Виконання логіки для додавання або оновлення контакту
            contact = book.find_address(name)
            if contact:
                if normalized_phone:
                    contact.phones.add_phone(normalized_phone)  # Додаємо обов'язковий номер
                    print(f'Phone number {normalized_phone} added to {name}.')
                if phone2:
                    normalized_phone2 = normalize_phone(phone2)
                    if isinstance(normalized_phone2, str) and not normalized_phone2.startswith("Invalid"):
                        contact.phones.add_phone(normalized_phone2)  # Додаємо другий номер, якщо є
                        print(f'Phone number {normalized_phone2} added to {name}.')
                    else:
                        print(f"Warning: Ignoring additional phone number {phone2}.")
                if birthday:
                    if re.match(r"^\d{2}\.\d{2}\.\d{4}$", birthday):  # Перевірка формату дати
                        contact.add_birthday(birthday)  # Додаємо день народження, якщо формат правильний
                        print(f'Birthday {birthday} added to {name}.')
                    else:
                        print("Error: Invalid birthday format. Expected DD.MM.YYYY.")
                if email:
                    contact.email = email  # Додаємо email, якщо є
                    print(f'Email {email} added to {name}.')
            else:
                # Створюємо новий контакт з обов'язковими та опційними параметрами
                phones = [phone]
                if phone2:
                    phones.append(phone2)  # Додаємо другий номер, якщо є
                record = Record(name, phones, birthday, email)  # Передаємо список телефонів
                book.add_address(record)
                print(f"New contact {name} added with phone number {phone}, "
                      f"second phone number {phone2 if phone2 else 'N/A'}, "
                      f"birthday {birthday if birthday else 'N/A'}, "
                      f"and email {email if email else 'N/A'}.")


        elif command == "change":
            if len(args) < 3:
                print("Error: Provide name, old phone, and new phone.")
            else:
                name, old_phone, new_phone = args
                contact = book.find_address(name)
                if contact:
                    if contact.phones.edit_phone(old_phone, new_phone):
                        print(f"Phone number changed from {old_phone} to {new_phone} for {name}.")
                    else:
                        print(f"Phone number {old_phone} not found for {name}.")
                else:
                    print(f"Error: Contact '{name}' not found.")

        elif command == "phone":
            if not args:
                print("Error: Provide a name.")
            else:
                name = args[0]
                contact = book.find_address(name)
                if contact:
                    print(f"{name}'s phone numbers: {', '.join(contact.phones.value)}")
                else:
                    print(f"Error: Contact '{name}' not found.")

        elif command == "all":
            if not book.data:
                print("No contacts found.")
            else:
                for contact in book.values():
                    print(contact)

        elif command == "add_birthday":
            if not args or len(args) < 2:
                print("Error: Input name and birthday.")
                continue

            name, birthday = args[0], args[1]
            contact = book.find_address(name)

            if contact:
                # Перевірка правильності формату дати за допомогою регулярного виразу
                if re.match(r"\d{2}\.\d{2}\.\d{4}$", birthday):
                    Birthday.add_birthday_to_contact(contact, birthday)
                    print(f'Birthday {birthday} added to {name}.')
                else:
                    print(f"Error: Invalid birthday format. Expected DD.MM.YYYY.")
            else:
                print(f"Error: Contact '{name}' not found.")


        elif command == "show_birthday":
            if not args:
                print('Error:Input a name.')
                continue
            name = args[0]
            contact = book.find_address(name)
            if contact:
                print(Birthday.show_birthday_of_contact(contact))
            else:
                print(f"Error: Contact '{name}' not found.")

        elif command == "birthdays":
            upcoming_birthdays = Birthday.get_upcoming_birthdays(book)
            if upcoming_birthdays:
                print('Upcoming birthdays:')
                for ub in upcoming_birthdays:
                    print(f'{ub['name']} on {ub['congratulation_date']}.')
            else:
                print('There are no upcoming birthdays.')

        else:
            print(f"Unknown command '{command}'.")

if __name__ == "__main__":
    main()
