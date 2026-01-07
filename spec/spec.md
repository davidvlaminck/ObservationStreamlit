This document outlines the specifications for a Streamlit application.
The purpose of the application is to allow the user to input data and display the results on a webpage.
Since this will be developed in phases, the specifications will evolve over time.

# 1. Introduction
The application will be built using Streamlit, a popular framework for creating web applications in Python.
The initial phase will focus on establishing a connection to a database, implementing user authentication, fetching data, and displaying it on a webpage.

# 2. Functional Requirements
## 2.1 User Authentication
- Users must be able to log in using a username and password.
- Passwords should be securely hashed and stored in the database.
- Implement session management to keep users logged in.
- Users should be able to register for an account (if applicable). A manual account creation process will be used in the initial phase.

## 2.2 Database Connection
- The application must connect to a specified database (e.g., PostgreSQL, MySQL, SQLite).
- Implement error handling for database connection issues.

## 2.3 Data Fetching
- After logging in, users should be able to fetch data from the database.
- Implement filters to allow users to refine the data they want to view.

## 2.4 Data Display
- Display the fetched data in a user-friendly format (e.g., tables, charts).
- The user interface should be fast to navigate and in Flemish (Dutch, Belgium).

## 2.5 Data Entry
- The user should be able to enter new data as fast as possible (few clicks, voice chat) so it works well on a tablet or smartphone.

# 3. Non-Functional Requirements
## 3.1 Performance
- The application should load data within an acceptable time frame (e.g., under 3 seconds).

## 3.2 Security
- Ensure that all user inputs are sanitized to prevent SQL injection attacks.
- Use HTTPS for secure communication between the client and server.

# 4. Future Phases
Future phases may include additional features such as:
- User registration and password recovery.
- Advanced data visualization options.
- Integration with third-party APIs for enhanced functionality.

# 5. Conclusion
This specification provides a foundation for developing a Streamlit application that connects to a database, authenticates users, fetches data, and displays it on a webpage.
As development progresses, these specifications will be refined and expanded to meet user needs and project goals.

# Testing requirements (in phases)
We will maintain automated tests alongside development:
- **Phase 0:** import/smoke checks (modules import cleanly; no side effects).
- **Phase 1 (Auth):** unit tests for password hashing/verification and session-state transitions; optional SQLite integration tests for `users` constraints.
- **Phase 2 (DB layer):** integration tests for migrations and schema creation; unit tests for DB configuration switching (SQLite dev ↔ Postgres prod).
- **Phase 3+ (Queries/UI logic):** tests for filter validation, parameterized queries (no SQL string concatenation), and graceful empty/error states.

# Responsive UI (mobile/tablet)
The application must be usable on desktop and smaller screens (tablet and mobile).

Minimum expectations:
- Core flows (login, filtering, viewing results) work on a narrow viewport.
- Layout avoids horizontal scrolling for primary content whenever feasible.
- Controls remain usable with touch input (reasonable spacing and sizing).
- Tables/charts have a readable fallback on small screens (e.g., responsive containers, pagination, or simplified views).

UI implementation approach (Streamlit + streamlit-elements)
- Build the app in Streamlit.
- For a more polished, Material-style UI, we will **prefer `streamlit-elements`** (Material UI components) for key screens and reusable widgets.
- Keep a minimal fallback path using standard Streamlit components for:
  - first-pass prototypes
  - accessibility/usability checks
  - components that don’t map cleanly to `streamlit-elements`

Other optional libraries to evaluate only if needed:
- `streamlit-option-menu` (navigation patterns)
- `streamlit-aggrid` (advanced data grid)
- `streamlit-authenticator` (auth UI helpers; still validate security assumptions)

Phased approach:
- **Phase 0:** choose a page/layout structure that doesn’t assume a wide screen.
- **Phase 3:** ensure filters and results can be used on mobile without layout breakage.
- **Phase 4:** verify charts/tables are readable and scrollable on small screens.
