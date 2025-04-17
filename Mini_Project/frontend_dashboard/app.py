# frontend_dashboard/app.py

import streamlit as st
import requests
import pandas as pd
import time

# --- Configuration ---
DJANGO_API_HOST = "http://127.0.0.1:8000"  # Update if deployed
LOGIN_URL = f"{DJANGO_API_HOST}/api/token/"
USER_DETAIL_URL = f"{DJANGO_API_HOST}/api/user/me/"
# Student URLs
MY_COURSES_URL = f"{DJANGO_API_HOST}/api/my-courses/"
MY_ASSIGNMENTS_URL = f"{DJANGO_API_HOST}/api/my-assignments/"
MY_GRADES_URL = f"{DJANGO_API_HOST}/api/my-grades/"
CHATBOT_URL = f"{DJANGO_API_HOST}/api/chatbot/query/" # Chatbot is student-specific
# Teacher URLs
TEACHER_COURSES_URL = f"{DJANGO_API_HOST}/api/teacher/my-courses/"
UPLOAD_CONTENT_URL = f"{DJANGO_API_HOST}/api/teacher/upload-content/"


# --- Session State Initialization ---
# Initialize keys if they don't exist to prevent errors on first run
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'refresh_token' not in st.session_state:
    st.session_state.refresh_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

# --- Helper Functions ---

def fetch_user_details(access_token):
    """Fetches user details from the backend to determine role."""
    if not access_token: return None
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("DEBUG: Fetching user details...") # <<< DEBUG
        response = requests.get(USER_DETAIL_URL, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"DEBUG: User details fetched: {user_data}") # <<< DEBUG
            return response.json()
        print(f"Error fetching user details: Status {response.status_code}") # Debugging
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching user details: {e}") # Debugging
        return None

def login_user(username, password):
    """Attempts login, fetches user role, and updates session state."""
    try:
        print(f"DEBUG: Attempting login for user: {username}") # <<< DEBUG
        response = requests.post(LOGIN_URL, data={'username': username, 'password': password})
        print(f"DEBUG: Login API response status: {response.status_code}") # <<< DEBUG
        if response.status_code == 200:
            tokens = response.json()
            st.session_state.access_token = tokens.get('access')
            st.session_state.refresh_token = tokens.get('refresh')
            print("DEBUG: Tokens received.") # <<< DEBUG

            # Fetch user details immediately after getting token
            user_details = fetch_user_details(st.session_state.access_token)
            st.session_state.user_role = None # Default to None
            if user_details:
                st.session_state.user_info = user_details
                groups = user_details.get('groups', [])
                print(f"DEBUG: Fetched groups for user {username}: {groups}") # Debug Print
                if 'Teachers' in groups:
                    st.session_state.user_role = 'Teacher'
                    print(f"DEBUG: Role set to 'Teacher' based on groups.") # <<< DEBUG
                elif 'Students' in groups:
                    st.session_state.user_role = 'Student'
                    print(f"DEBUG: Role set to 'Student' based on groups.") # <<< DEBUG
                print(f"DEBUG: Assigned role: {st.session_state.user_role}") # Debug Print
            else:
                 st.session_state.error_message = "Login successful, but failed to get user role details."
                 # Decide if login should fail if role cannot be determined
                 # For now, let's proceed but role will be None

            st.session_state.logged_in = True
            st.session_state.error_message = None # Clear previous errors
            print(f"DEBUG: Login successful. Final role in state: {st.session_state.user_role}. Rerunning...") # <<< DEBUG
            st.rerun() # Rerun to update UI immediately
        else:
            st.session_state.error_message = response.json().get('detail', 'Invalid credentials or server error.')
            # Clear potentially stale state on login failure
            print(f"DEBUG: Login failed. Status: {response.status_code}") # <<< DEBUG
            logout_user(silent=True) # Clear state without success message
    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"Network error during login: {e}"
        logout_user(silent=True)

def logout_user(silent=False):
    """Clears session state for logout."""
    # More robust clearing
    print("DEBUG: Logging out, clearing state.") # <<< DEBUG
    keys_to_clear = ['logged_in', 'access_token', 'refresh_token', 'user_info', 'user_role', 'error_message']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    if not silent:
        st.success("Logged out successfully.")
    st.rerun()

def fetch_protected_data(url):
    print(f"DEBUG: Fetching protected data from: {url}") # <<< DEBUG
    """Fetches data from protected API endpoints, handles 401 by logging out."""
    if not st.session_state.get('access_token'):
         st.warning("Not logged in or access token missing.")
         return None

    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Authentication expired or invalid. Please log in again.")
            logout_user(silent=True) # Log out without success message on auth error
            return None
        elif response.status_code == 403:
             # Handle forbidden access specifically if needed (though UI should prevent this)
             print(f"Forbidden access to {url}. Check user role and permissions.")
             st.error(f"Error fetching data: Access denied (Status code {response.status_code})")
             return None
        else:
             st.error(f"Error fetching data: Status code {response.status_code}")
             print(f"Error details: {response.text}") # Log more details
             return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching data: {e}")
        return None

# --- Streamlit App UI ---
st.set_page_config(layout="wide")
st.title("Academic Dashboard & Chatbot")

# --- Login View ---
if not st.session_state.get('logged_in'): # Use .get for safety
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            # login_user handles state update and rerun
            login_user(username, password)

    # Display error message if login failed
    if st.session_state.get('error_message'):
        st.error(st.session_state.error_message)
        st.session_state.error_message = None # Clear error after displaying

# --- Logged-In Dashboard View ---
else:
    role = st.session_state.get('user_role') # Use .get for safety
    print(f"--- DEBUG: RENDERING UI --- Role from session state: '{role}' (Type: {type(role)})")
    user_display_name = st.session_state.get('user_info', {}).get('username', 'User') # Safer access

    # --- Sidebar for logged-in users ---
    st.sidebar.success(f"Logged in as: {user_display_name} ({role or 'Unknown Role'})")
    st.sidebar.button("Logout", on_click=logout_user)
    st.sidebar.markdown("---") # Separator

    # --- Role-Specific Main Content ---
    print(f"DEBUG: Rendering UI for role: {role}") # Debug Print
    if role == "Student":
        print("DEBUG: Rendering STUDENT UI") # <<< DEBUG
        st.header("Student Dashboard")

        # --- Student Data Sections ---
        st.subheader("My Courses")
        courses_data = fetch_protected_data(MY_COURSES_URL)
        if courses_data:
             if courses_data: # Check if list is not empty
                try:
                    df_courses = pd.DataFrame([c.get('course', {}) for c in courses_data]) # Safer access
                    if not df_courses.empty and all(col in df_courses for col in ['code', 'name', 'teacher_username']):
                         df_display = df_courses[['code', 'name', 'teacher_username']]
                         df_display.columns = ['Course Code', 'Course Name', 'Teacher']
                         st.dataframe(df_display, use_container_width=True)
                    else:
                         st.info("Course data structure seems incorrect or incomplete.")
                         print(f"DEBUG: Incorrect course data structure: {courses_data}")
                except Exception as e:
                     st.error(f"Error processing course data: {e}")
                     print(f"DEBUG: Error processing course data: {courses_data}")
             else:
                  st.info("You are not currently enrolled in any courses.")
        else:
            # Error/warning already displayed by fetch_protected_data if fetch failed
            pass

        st.subheader("My Upcoming Assignments")
        assignments_data = fetch_protected_data(MY_ASSIGNMENTS_URL)
        if assignments_data:
            if assignments_data:
                try:
                    df = pd.DataFrame(assignments_data)
                    if not df.empty and all(col in df for col in ['course_code', 'title', 'due_date', 'total_points']):
                        df['due_date'] = pd.to_datetime(df['due_date']).dt.strftime('%Y-%m-%d %H:%M')
                        df_display_assignments = df[['course_code', 'title', 'due_date', 'total_points']]
                        df_display_assignments.columns = ['Course', 'Title', 'Due Date', 'Points']
                        st.dataframe(df_display_assignments.sort_values(by='Due Date'), use_container_width=True)
                    else:
                         st.info("Assignments data structure seems incorrect.")
                         print(f"DEBUG: Incorrect assignment data structure: {assignments_data}")
                except Exception as e:
                     st.error(f"Error processing assignments data: {e}")
                     print(f"DEBUG: Error processing assignments data: {assignments_data}")
            else:
                st.info("No upcoming assignments found.")
        else:
            pass # Error/warning already displayed

        st.subheader("My Grades")
        grades_data = fetch_protected_data(MY_GRADES_URL)
        if grades_data:
            if grades_data:
                try:
                    df = pd.DataFrame(grades_data)
                    if not df.empty and all(col in df for col in ['course_code', 'assignment_title', 'score', 'submission_status', 'submitted_at']):
                        # Handle None score before converting to float
                        df['score'] = df['score'].apply(lambda x: float(x) if x is not None else None)
                        df['display_score'] = df.apply(lambda row: f"{row['score']:.2f}" if row['score'] is not None else 'N/A', axis=1)
                        # Handle None submitted_at before formatting
                        df['submitted_at_str'] = pd.to_datetime(df['submitted_at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                        display = df[['course_code', 'assignment_title', 'display_score', 'submission_status', 'submitted_at_str']]
                        display.columns = ['Course', 'Assignment', 'Score', 'Status', 'Submitted']
                        st.dataframe(display, use_container_width=True)
                    else:
                         st.info("Grades data structure seems incorrect.")
                         print(f"DEBUG: Incorrect grades data structure: {grades_data}")
                except Exception as e:
                     st.error(f"Error processing grades data: {e}")
                     print(f"DEBUG: Error processing grades data: {grades_data}")
            else:
                 st.info("No grades found for you yet.")
        else:
            pass # Error/warning already displayed

        # --- Chatbot UI (Only for Students) ---
        st.sidebar.header("Course Chatbot")
        user_query = st.sidebar.text_input("Ask about course content or your data:")
        if st.sidebar.button("Ask Chatbot"):
            if user_query:
                st.sidebar.info("Sending query...") # User feedback
                if st.session_state.get('access_token'):
                    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
                    try:
                        resp = requests.post(CHATBOT_URL, json={"query": user_query}, headers=headers)
                        if resp.status_code == 200:
                            st.sidebar.success("Chatbot:")
                            st.sidebar.markdown(resp.json().get('response', 'Received empty response.'))
                        elif resp.status_code == 401: # Handle expired token during chat
                             st.sidebar.error("Authentication failed. Please log in again.")
                             logout_user(silent=True)
                        elif resp.status_code == 403: # Should not happen if UI is correct, but good to handle
                             st.sidebar.error("Access denied to chatbot.")
                        else:
                            st.sidebar.error(f"Chatbot error: Status {resp.status_code}")
                            print(f"Chatbot error details: {resp.text}")
                    except requests.exceptions.RequestException as e:
                        st.sidebar.error(f"Network error connecting to chatbot: {e}")
                else:
                     st.sidebar.error("Cannot query chatbot. Please log in again.")
                     logout_user(silent=True)
            else:
                st.sidebar.warning("Please enter a question.")

    elif role == "Teacher":
        print("DEBUG: Rendering TEACHER UI") # <<< DEBUG
        st.header("Teacher Dashboard")

        st.subheader("My Courses & Content Upload")
        teacher_courses = fetch_protected_data(TEACHER_COURSES_URL)

        if teacher_courses is not None: # Check fetch was successful
            if teacher_courses: # Check list not empty
                for course in teacher_courses:
                     # Use course ID in expander title for clarity if needed
                    with st.expander(f"**{course.get('code', 'N/A')} - {course.get('name', 'N/A')}**"):
                        course_id = course.get('id')
                        if course_id: # Ensure course ID exists before showing uploader
                            st.write("Upload new content (PDF, DOCX, TXT):")
                            # Use a more robust key including course_id and maybe a counter if needed
                            uploaded_file = st.file_uploader(
                                "Choose a file",
                                type=['pdf', 'docx', 'txt'],
                                key=f"upload_{course_id}"
                            )
                            if uploaded_file:
                                files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                                data = {'course_id': course_id}
                                headers = {'Authorization': f'Bearer {st.session_state.access_token}'}

                                # Use unique button key
                                if st.button(f"Upload {uploaded_file.name} for {course.get('code', 'this course')}", key=f"btn_upload_{course_id}"):
                                    with st.spinner(f"Uploading and processing {uploaded_file.name}..."):
                                        try:
                                            resp = requests.post(UPLOAD_CONTENT_URL, files=files, data=data, headers=headers)
                                            if resp.status_code == 201:
                                                st.success(f"Successfully uploaded and processed '{uploaded_file.name}'!")
                                                # Consider clearing the file uploader state here if possible/needed
                                                # This is tricky in Streamlit - often requires rerunning or more complex state mgmt
                                            elif resp.status_code == 401:
                                                st.error("Authentication error. Please log out and log back in.")
                                                logout_user(silent=True)
                                            elif resp.status_code == 403:
                                                st.error("Authorization Error: You might not be the assigned teacher for this course, or another permission issue occurred.")
                                            else:
                                                error_detail = resp.json().get('error', f'Upload failed with status {resp.status_code}')
                                                st.error(f"Upload failed: {error_detail}")
                                                print(f"Upload error details: {resp.text}")
                                        except requests.exceptions.RequestException as e:
                                            st.error(f"Network error during upload: {e}")
                        else:
                             st.warning("Course ID missing for this course entry.")
            else:
                st.info("You are not currently assigned to teach any courses.")
        else:
            # Warning/error handled by fetch_protected_data
             pass

    else:
        # Handle case where user is logged in but role is None or unexpected
        print(f"DEBUG: Rendering UNKNOWN/INVALID role UI (Role: '{role}')") # <<< DEBUG
        st.error("Invalid user role detected or role could not be determined. Access denied.")
        st.button("Logout", on_click=logout_user) # Allow logout even if role is invalid