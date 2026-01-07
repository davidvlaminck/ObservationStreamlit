This document describes the screens of the application.

# 1. Login Screen
The app uses an invite-only workflow with administrator-created temporary passwords (no email delivery).
- Fields: Email, Password
- Buttons: Login
- Additional flows:
  - If a user's account was created or reset by the admin, the user signs in using the temporary password and is immediately forced to pick a new password (enter twice). After successful change the user continues to the Protected Screen.
  - If the app is started with no users in the DB, the app creates an initial admin account automatically. The initial admin credentials are taken from environment variables (e.g., `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD`) if provided; otherwise a safe default of `admin` / `admin` will be created. The initial admin account is created with `must_change_password=true` and the admin will be forced to pick a new password on first login.
  - Invalid credentials show a generic "Invalid credentials" message (do not reveal whether the email exists).
- Notes:
  - Registration UI is not exposed to end users. New accounts are created by the admin from the Admin → Users screen where a one-time temporary password is generated and shown to the admin for out-of-band delivery.
  - Password reset for users is performed by the admin (Reset password) which generates a new temporary password and sets the user to must-change-password=true. No email is sent by the app.

After login is successful (and any forced password change completed), go to the Protected Screen.

# 2. Protected Screen
This will direct the user to either viewing data or entering data and thus to the respective screens. The admin section/menu is visible only to admin users and contains user & configuration management pages (see Admin → Users and Admin → Categories / Class list).

# 3. Entering data Screen
The user will select a category of observation from a list/tree.
The user will select a date from a datepicker, defaulting on "today".
The user will see a list of people for the most recent school year.
For each person, the full name will be displayed, along with:
- 6 radiobuttons, one for each possible score and NULL. Only one can be selected, the default is NULL. Lines where the value is NULL aren't stored unless there is a non-empty comment.
  - 1 = red
  - 2 = orange
  - 3 = light green
  - 4 = dark green
  - ? = light blue
  - NULL = light grey
- a comment field as a textbox that allows the user to directly input a string (single line)
- Above this list, there should be an additional row of radio buttons, so the user can select one to fill the entire list with the chosen value.
- At the bottom of the screen, there will be a "Save" button to store the observations. Saving overwrites any existing observations for the same (person, date, category). Saves for multiple selected categories (side-panel) are atomic: either all changed observations are persisted or none are.
- At the top right of the screen there should be a side panel that can be hidden or displayed, showing some additional observation categories. These have checkmarks before them. If they are marked, the corresponding observation should be added to the right of the current observation. This means 2 (or more) full tables of observations next to each other. The tables use the date and class list in common but will have separate scores and comments. The list will likely be "Andere", "Betrokkenheid", "Sociaal", "Zelfredzaamheid", "Remediëring". This should be configured in the database.
After saving, a success message should be displayed, and the user remains on the same screen to enter more data if needed.

Responsive behavior and mobile notes:
- Primary use is laptop, but the UI must be usable on phone/tablet. On narrow viewports the side-by-side tables stack vertically; on wide viewports they appear horizontally.
- Class lists will be up to 25 records. No need for pagination.

Acceptance criteria (Entering data):
- Selecting date + category shows the class list for the most recent school year.
- Changing values and clicking Save overwrites existing observations for the same person/date/category and shows a success toast.
- Saving across multiple categories is atomic.
- NULL-only rows without comments are not persisted.

# 4. Viewing entire class data Screen
The user will select a category of observation from a list/tree.
When selected a table will appear containing all observations for that category of the most recent school year.
The table will have a row for each person.
The table will display the score of that observation per date. So the dates are the column headers. These should be rotated 45° diagonally or 90° vertically so this takes up a lot less space.
Each record will have a detail toggle or button. When clicked, a popup or side panel will appear showing a list of all observations but in a list (vertically), displaying date, score, and comment. This can be hidden or shown by clicking the same button/toggle.

Export: add an "Export (XLSX)" button on this screen that creates an Excel workbook for the most recent school year. The workbook should include at least two sheets: a pivoted overview (rows = people, columns = dates) with separate columns for score and comment per date, and a flat sheet (one row per observation) for analysis.

Acceptance criteria (Viewing entire class):
- Table shows all dates for the selected category and the most recent school year.
- Detail toggle shows full list of observations for a person.
- Export button produces an XLSX file with pivot and flat sheets for the most recent school year.

# 5. Viewing single person data Screen
The user will select a single person from a listbox, filled with all people of the most recent school year.
The categories of observation will all be displayed, in hierarchical structure (tree)
For every category that has observations for that person, a table will be displayed showing the date (column), score (row) of that observation, followed by the comment.

Export: add an "Export (XLSX)" button on this screen as well. It should export all observations for the selected person for the most recent school year.

Acceptance criteria (Viewing single person):
- Selecting a person shows per-category tables of their observations with comments available.
- Export button produces an XLSX with the person's observations (flat sheet).
