import sys
import sqlite3
from PyQt5 import QtWidgets
from Mainpage import Ui_MainWindow
from Secondpage import Ui_MusicSelectingWindow
from LastPage import Ui_MyMuiscLIstWindow

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui_main = Ui_MainWindow()
        self.ui_main.setupUi(self)

        self.music_window = QtWidgets.QMainWindow()
        self.ui_music = Ui_MusicSelectingWindow()
        self.ui_music.setupUi(self.music_window)

        self.list_window = QtWidgets.QMainWindow()
        self.ui_list = Ui_MyMuiscLIstWindow()
        self.ui_list.setupUi(self.list_window)

        self.selected_songs = []

        self.ui_main.Register_btn.clicked.connect(self.register_user)
        self.ui_main.LogIn_btn.clicked.connect(self.login_user)
        self.ui_main.Quit_btn.clicked.connect(self.close)

        self.ui_music.SeeList_Button.clicked.connect(self.show_list_window)
        self.ui_music.Add_button.clicked.connect(self.add_selected_to_db)
        self.ui_music.Quit2_Button.clicked.connect(self.music_window.close)

        self.ui_music.Search_LineEdit.returnPressed.connect(self.search_songs)

        self.ui_list.Quit_button2.clicked.connect(self.list_window.close)

        self.ui_main.Password_editline.setEchoMode(QtWidgets.QLineEdit.Password)

        self.ui_main.Username_editline.mousePressEvent = self.clear_username
        self.ui_main.Password_editline.mousePressEvent = self.clear_password

        conn = sqlite3.connect("MyList.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS my_songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_name TEXT,
                artist_name TEXT,
                released_year INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def clear_username(self, event):
        self.ui_main.Username_editline.clear()
        QtWidgets.QLineEdit.mousePressEvent(self.ui_main.Username_editline, event)

    def clear_password(self, event):
        self.ui_main.Password_editline.clear()
        QtWidgets.QLineEdit.mousePressEvent(self.ui_main.Password_editline, event)

    def register_user(self):
        username = self.ui_main.Username_editline.text()
        password = self.ui_main.Password_editline.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "გთხოვთ შეავსოთ ორივე ველი!")
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            QtWidgets.QMessageBox.information(self, "Success", "რეგისტრაცია წარმატებით შესრულდა!")
        except sqlite3.IntegrityError:
            QtWidgets.QMessageBox.warning(self, "Error", "მომხმარებელი უკვე არსებობს!")
        conn.close()

    def login_user(self):
        username = self.ui_main.Username_editline.text()
        password = self.ui_main.Password_editline.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "გთხოვთ შეავსოთ ორივე ველი!")
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            QtWidgets.QMessageBox.information(self, "Success", "შესვლა წარმატებულია!")
            self.load_music_data()
            self.music_window.show()
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "არ გაქვთ რეგისტრაცია გავლილი!")

    def load_music_data(self):
        conn = sqlite3.connect("MusicList.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT DISTINCT `artist(s)_name` FROM MusicList")
            artists = cursor.fetchall()
            self.ui_music.Genre_comboBox.clear()
            self.ui_music.Genre_comboBox.addItem("All artists")
            for artist in artists:
                self.ui_music.Genre_comboBox.addItem(artist[0])

            cursor.execute("SELECT DISTINCT released_year FROM MusicList ORDER BY released_year")
            years = cursor.fetchall()
            self.ui_music.Year_comboBox.clear()
            self.ui_music.Year_comboBox.addItem("All years")
            for year in years:
                self.ui_music.Year_comboBox.addItem(str(year[0]))

            self.ui_music.Rating_comboBox.clear()
            self.ui_music.Rating_comboBox.addItems(["From highest", "From lowest"])

            cursor.execute("SELECT track_name, `artist(s)_name`, released_year FROM MusicList")
            songs = cursor.fetchall()

            self.checkboxes = []
            layout = QtWidgets.QVBoxLayout()
            for song in songs:
                song_text = f"{song[0]} — {song[1]} — {song[2]}"
                checkbox = QtWidgets.QCheckBox(song_text)
                checkbox.track_name = song[0]
                checkbox.artist_name = song[1]
                checkbox.released_year = song[2]
                self.checkboxes.append(checkbox)
                layout.addWidget(checkbox)

            content_widget = QtWidgets.QWidget()
            content_widget.setLayout(layout)
            self.ui_music.scrollArea_for_music.setWidget(content_widget)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"ბაზის წაკითხვის პრობლემა: {e}")

        conn.close()

    def add_selected_to_db(self):
        conn = sqlite3.connect("MyList.db")
        cursor = conn.cursor()

        added = False
        for cb in self.checkboxes:
            if cb.isChecked():
                cursor.execute("INSERT INTO my_songs (track_name, artist_name, released_year) VALUES (?, ?, ?)",
                               (cb.track_name, cb.artist_name, cb.released_year))
                added = True

        if added:
            conn.commit()
            QtWidgets.QMessageBox.information(self.music_window, "Success", "მონიშნული სიმღერები დაემატა სიაში!")
        else:
            QtWidgets.QMessageBox.warning(self.music_window, "Warning", "გთხოვ მონიშნე სიმღერები დასამატებლად!")

        conn.close()

    def show_list_window(self):
        conn = sqlite3.connect("MyList.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT track_name, artist_name, released_year FROM my_songs")
            songs = cursor.fetchall()

            layout = QtWidgets.QVBoxLayout()
            for song in songs:
                song_text = f"{song[0]} — {song[1]} — {song[2]}"
                label = QtWidgets.QLabel(song_text)
                layout.addWidget(label)

            content_widget = QtWidgets.QWidget()
            content_widget.setLayout(layout)
            self.ui_list.scrollArea_for_mylist.setWidget(content_widget)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"ჩემი სიის წაკითხვის პრობლემა: {e}")

        conn.close()

        self.list_window.show()
        self.music_window.hide()

    def search_songs(self):
        search_text = self.ui_music.Search_LineEdit.text().lower()

        for cb in self.checkboxes:
            if search_text in cb.track_name.lower():
                cb.show()
            else:
                cb.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
