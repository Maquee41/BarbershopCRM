import sys

from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QPushButton, QLabel, QWidget, QVBoxLayout, \
    QHBoxLayout, QFormLayout, QLineEdit, QDateTimeEdit, QSpinBox, QDialogButtonBox
from PyQt5.uic import loadUi
import database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('windows/main_window.ui', self)
        self.history_add_dialog = None
        self.service_add_dialog = None
        self.client_add_dialog = None

        self.historyButton.clicked.connect(self.history_callback)
        self.serviceButton.clicked.connect(self.service_callback)
        self.clientsButton.clicked.connect(self.clients_callback)
        self.createButton.clicked.connect(self.create_item_callback)

        self.data_type = 'history'
        self.history_callback()

    def display_data(self):
        content = QWidget()
        area_layout = QVBoxLayout(content)
        self.scrollArea.setWidget(content)
        self.scrollArea.setWidgetResizable(True)

        data_functions = {
            'history': database.select_full_history,
            'service': database.select_all_services,
            'client': database.select_all_clients
        }

        row_format = {
            'history': lambda row_: (
                f"id: {row_['id']}\nИмя: {row_['full_name']}\nТелефон: {row_['phone']}\nУслуга: {row_['item']}\nЦена: {row_['price']}\nДата и время: {row_['datetime']}\nОценка: {row_['feedback']}",
                row_['id']),
            'service': lambda row_: (
                f"id: {row_['id']}\nНазвание услуги: {row_['item']}\nЦена: {row_['price']}", row_['id']),
            'client': lambda row_: (f"id: {row_['id']}\nИмя: {row_['full_name']}\nТелефон: {row_['phone']}", row_['id'])
        }

        rows = data_functions[self.data_type]()
        for row in rows:
            data_text, current_id = row_format[self.data_type](row)
            data_label = QLabel(data_text)
            h_layout = QHBoxLayout()
            edit_button = QPushButton('Редактировать')

            edit_button.clicked.connect(lambda _, id_=current_id: self.edit_window(id_))

            h_layout.addWidget(data_label)
            h_layout.addWidget(edit_button)
            if self.data_type != 'client':
                delete_button = QPushButton('Удалить')
                delete_button.clicked.connect(lambda _, id_=current_id: self.delete_window(id_))
                h_layout.addWidget(delete_button)
            area_layout.addLayout(h_layout)

    def edit_window(self, id_):
        match self.data_type:
            case 'history':
                data = database.get_history_item(id_)
            case 'service':
                data = database.get_service_item(id_)
            case 'client':
                data = database.get_client_info(id_)
            case _:
                data = 'error'
        dialog = EditDialog(self.data_type, data)
        dialog.exec_()
        self.display_data()

    def delete_window(self, id_):
        match self.data_type:
            case 'history':
                data = database.get_history_item(id_)
                message = f'Подтвердите удаление\nid: {data['id']}\tclient_name: {data['client_name']}\t'
                message += f'client_phone: {data['client_phone']}\tОценка: {data['feedback']}\n'
                message += f'Дата и время: {data['datetime']}\tУслуга: {data['item']}\tЦена: {data['price']}'
            case 'service':
                data = database.get_service_item(id_)
                message = f'Подтвердите удаление\nid: {data['id']}\tУслуга: {data['item']}\tЦена: {data['price']}'
            case _:
                message = 'error'
        dialog = DeleteDialog(id_, self.data_type, message)
        dialog.exec_()
        self.display_data()

    def history_callback(self):
        self.data_type = 'history'
        self.display_data()

    def service_callback(self):
        self.data_type = 'service'
        self.display_data()

    def clients_callback(self):
        self.data_type = 'client'
        self.display_data()

    def create_item_callback(self):
        dialog_classes = {
            'history': AddHistoryItemDialog,
            'service': AddServiceDialog,
            'client': AddClientDialog
        }
        dialog = dialog_classes[self.data_type]()
        dialog.exec_()
        self.display_data()


class EditDialog(QDialog):
    def __init__(self, data_type: str, data: dict):
        super().__init__()
        self.data_type = data_type
        self.data = data

        self.setWindowTitle('Редактирование данных')

        self.layout = QFormLayout(self)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox.accepted.connect(self.edit_run)
        self.buttonBox.rejected.connect(self.reject)

        self.client_name = QLineEdit(self)
        self.client_phone = QLineEdit(self)

        self.item_edit = QLineEdit(self)
        self.price_edit = QLineEdit(self)
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.feedback_spin_box = QSpinBox(self)
        self.feedback_spin_box.setRange(1, 5)
        self.layout.addRow('Имя:', self.client_name)
        self.layout.addRow('Телефон:', self.client_phone)
        self.layout.addRow('Услуга:', self.item_edit)
        self.layout.addRow('Цена:', self.price_edit)
        self.layout.addRow('Дата и время:', self.datetime_edit)
        self.layout.addRow('Оценка:', self.feedback_spin_box)
        self.layout.addRow(self.buttonBox)

        self.setLayout(self.layout)

        self.set_values()

    def set_values(self):
        match self.data_type:
            case 'history':
                self.client_name.setEnabled(False)
                self.client_phone.setEnabled(False)
                self.feedback_spin_box.setEnabled(False)
                self.client_name.setText(self.data['client_name'])
                self.client_phone.setText(self.data['client_phone'])
                self.item_edit.setText(self.data['item'])
                self.price_edit.setText(self.data['price'])
                self.datetime_edit.setDateTime(self.data['datetime'])
                self.feedback_spin_box.setValue(self.data['feedback'])
            case 'service':
                self.item_edit.setText(self.data['item'])
                self.price_edit.setText(self.data['price'])

                self.layout.itemAt(0, 0).widget().hide()
                self.layout.itemAt(0, 1).widget().hide()

                self.layout.itemAt(1, 0).widget().hide()
                self.layout.itemAt(1, 1).widget().hide()

                self.layout.itemAt(4, 0).widget().hide()
                self.layout.itemAt(4, 1).widget().hide()

                self.layout.itemAt(5, 0).widget().hide()
                self.layout.itemAt(5, 1).widget().hide()
            case 'client':
                self.client_name.setEnabled(True)
                self.client_phone.setEnabled(True)
                self.client_name.setText(self.data['full_name'])
                self.client_phone.setText(self.data['phone'])

                self.layout.itemAt(2, 0).widget().hide()
                self.layout.itemAt(2, 1).widget().hide()

                self.layout.itemAt(3, 0).widget().hide()
                self.layout.itemAt(3, 1).widget().hide()

                self.layout.itemAt(4, 0).widget().hide()
                self.layout.itemAt(4, 1).widget().hide()

                self.layout.itemAt(5, 0).widget().hide()
                self.layout.itemAt(5, 1).widget().hide()

    def edit_run(self):
        match self.data_type:
            case 'history':
                item_id = self.data['id']
                item = self.item_edit.text()
                price = self.price_edit.text()
                datetime = self.datetime_edit.dateTime().toPyDateTime()
                feedback = self.data['feedback']
                if database.edit_history_item(item_id, item, price, datetime, feedback) == 'update':
                    self.show_message(1)
                else:
                    self.show_message(0)
            case 'service':
                item_id = self.data['id']
                item = self.item_edit.text()
                price = self.price_edit.text()
                if database.edit_service_item(item_id, item, price) == 'update':
                    self.show_message(1)
                else:
                    self.show_message(0)
            case 'client':
                user_id = self.data['id']
                client_name = self.client_name.text()
                client_phone = self.client_phone.text()
                if database.edit_client_item(user_id, client_name, client_phone):
                    self.show_message(1)
                else:
                    self.show_message(0)

    @staticmethod
    def show_message(success):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information if success else QMessageBox.Critical)
        msg.setText("Данные успешно изменены" if success else "Ошибка")
        msg.setWindowTitle("Информация")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class DeleteDialog(QDialog):
    def __init__(self, id_: int, data_type: str, message: str):
        super().__init__()
        loadUi('windows/delete_dialog.ui', self)
        self.id_ = id_
        self.data_type = data_type
        self.dataMessage.setText(message)
        self.dataMessage.adjustSize()
        self.buttonBox.accepted.connect(self.delete_run)
        self.buttonBox.rejected.connect(self.reject)

    def delete_run(self):
        match self.data_type:
            case 'history':
                if database.delete_history_item(self.id_) == 'delete':
                    self.show_message(1)
                else:
                    self.show_message(0)
            case 'service':
                if database.delete_service_item(self.id_) == 'delete':
                    self.show_message(1)
                else:
                    self.show_message(0)

    @staticmethod
    def show_message(success):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information if success else QMessageBox.Critical)
        msg.setText("Данные успешно изменены" if success else "Ошибка")
        msg.setWindowTitle("Информация")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class AddClientDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('windows/add_client.ui', self)
        self.buttonBox.accepted.connect(self.add_client_callback)

    def add_client_callback(self):
        full_name = self.fullNameEdit.text()
        phone = self.phoneEdit.text()
        self.show_message(database.create_client(full_name, phone))

    @staticmethod
    def show_message(success):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information if success else QMessageBox.Critical)
        msg.setText("Данные успешно записаны" if success else "Ошибка")
        msg.setWindowTitle("Информация")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class AddServiceDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('windows/add_service.ui', self)
        self.buttonBox.accepted.connect(self.add_service_callback)

    def add_service_callback(self):
        item = self.serviceLineEdit.text()
        price = self.priceLineEdit.text()
        self.show_message(database.create_service(item, price))

    @staticmethod
    def show_message(success):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information if success else QMessageBox.Critical)
        msg.setText("Данные успешно записаны" if success else "Ошибка")
        msg.setWindowTitle("Информация")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class AddHistoryItemDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('windows/add_history_item.ui', self)
        self.clientComboBox.addItems(database.get_all_clients())
        self.serviceComboBox.addItems(database.get_all_service_items())
        self.buttonBox.accepted.connect(self.add_history_item_callback)

    def add_history_item_callback(self):
        client_name = self.clientComboBox.currentText()
        item = self.serviceComboBox.currentText()
        datetime = self.dateTimeEdit.dateTime().toPyDateTime()
        feedback = self.feedbackSpinBox.value()
        self.show_message(database.create_history_item(client_name, item, datetime, feedback))

    @staticmethod
    def show_message(success):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information if success else QMessageBox.Critical)
        msg.setText("Данные успешно записаны" if success else "Ошибка")
        msg.setWindowTitle("Информация")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
