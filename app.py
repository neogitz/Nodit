from ext import app
from routes import home, edit_user, view_post, view_thread, about, create_post, create_thread, create_comment, \
    delete_thread, search, delete_comment, nod, login, logout, register, delete_user, profile, userlist, userprofile, \
    delete_post, feedback

app.run(debug=True, host="0.0.0.0")
