1. Late Sign-in Main Page
127.0.0.1:5500/
127.0.0.1:5500/signin/<signinid>

2. Teacher Panel
127.0.0.1:5500/teacher
Use Admin Panel to create a teacher account FIRST
A teacher may: 1. Change their password
2. View late sign-in data, and mark them as valid or invalid
3. Search data by student name or unique sign-in id

3. Admin Panel
127.0.0.1:5500/admin1022
**Default username: admin1022
Password: WSCLateSignInAdmin10221022**
An admin may:
1. Add students / edit or delete student records
2. Add teachers / edit or delete teacher records
3. Edit or delete sign-in records

Main changes made:
1. Connected to SQLite database, which can be edited via admin panel or by DB Browser for SQLite
2. Sign-in detail can be reviewed by student via 127.0.0.1:5500/signin/<signin_id>. E.g. 127.0.0.1:5500/signin/3
3. Teacher needs to log in to validate or invalidate records
4. Admin can edit student, teacher and signin information
5. All operations are done in the backend, which means code will not be shown in the frontend (others can’t see by developer tools)


