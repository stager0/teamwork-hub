# TeamWork Hub  
## *Task Tracker / Project Team Manager for IT Company*

---

## 1. Description

**TeamWork Hub** is an application designed for managing projects within IT teams. It allows users to:

- Create teams via a unique 10-character team code  
- Assign tasks based on team roles  
- Track task progress  
- Perform code reviews  
- Archive completed tasks and projects  

**Team structure:**

- `Leader` — full CRUD permissions and review access  
- `Member` — limited access, assigned tasks only  

**Directions supported:**

- Development  
- Backend  
- Design  
- Project Management  
- QA  
- Team Lead  

---

## 2. Features

✅ Team registration via unique 10-character code  
🔐 Role-based access: Leader vs Member  
🛠️ Full CRUD for Leaders (projects & tasks)  
🧩 Task assignment by direction (Frontend, Backend, QA, etc.)  
📊 Progress tracking with status updates and percentage  
🔄 Code Review system and task archiving  
🗂️ Project and Task Archives  
👥 Team overview and editable member info (Leader only)  
🔎 Search & filter by project title and direction  
📎 GitHub solution links in task details  
📱 Responsive and intuitive interface  

---

## 3. Diagram

![diagram](screenshots/my_diagram.png)

---

## 4. Screenshots with Detailed Description of Functionality

### 📝 Registration

Users enter:
- First & last name  
- Email & password  
- 10-character team code  
- Direction (Frontend, Backend, etc.)

**Leader:** first to register using team code  
**Member:** everyone else joining the same team code

![register page](screenshots/register.png)  
**Direction selection:**  
![register-direction](screenshots/register%20direction.png)

---

### 🔐 Login Page

After registration, users log in with their credentials.

![login page](screenshots/login.png)

---

### 🏠 Home Page

Displays:
- Total team members  
- Active projects  
- User's completed tasks  

Includes a navigation panel:

![home-page](screenshots/home.png)  
**Leader view:**  
![home-page-nav](screenshots/home-nav.png)

**Tabs overview:**
- Projects → "Projects List"  
  ![home-page2](screenshots/home-scr1.png)

- (Leader only) Review Tasks → "Pending Review"  
  ![home-page2](screenshots/home-scr2.png)

- My Tasks → "Current" & "Archived"  
  ![home-page3](screenshots/home-scr3.png)

- Our Command → "Team Members" & "Project Archive"  
  ![home-page4](screenshots/home-scr4.png)

- Welcome {Name} → Sign Out  
  ![home-page4](screenshots/home-scr5.png)

---

## 📁 Projects

Users see projects from their direction only.  
Leaders can create new projects.

![project-list](screenshots/proj%20list.png)  
![project-list-admin](screenshots/proj%20list1.png)  
![project-list-creation](screenshots/proj%20list3.png)

**Search by title:**  
![project-list-search](screenshots/proj%20list2.png)

Each project includes:
- Details  
- Tasks  

![project-list-project](screenshots/proj%20list4.png)

---

### 📄 Project Details

Shows all project info and linked tasks.  
Leaders can update, archive, or delete.

![project-list-project](screenshots/proj.png)  
![project-list-project](screenshots/proj1.png)  
**Update confirmation:**  
![project-detail-update](screenshots/proj%20update.png)  
**Delete confirmation:**  
![project-detail-update](screenshots/proj%20delete.png)

---

### ✅ Tasks in Project

Displays:
- Type, status, deadline, progress  
- "My Task" label for assigned tasks  

![project-tasks](screenshots/proj%20det.png)  
**Leader view:**  
![project-tasks-lead](screenshots/proj%20det1.png)

---

### 📌 Task Details

If unassigned + status = "To Do" → “Assign Me” button shown.  
After assignment → status updates to "In Progress".

![project-tasks-lead](screenshots/task%20detail.png)  
Additional options appear:
- Unassign  
- Change status  
- Add GitHub link  

![project-tasks-lead](screenshots/task%20detail1.png)  
![project-tasks-lead](screenshots/task%20detail2.png)

Once task is 100% done → status set to `75% - code review`, and sent to review list.

![project-tasks-lead](screenshots/task%20detail3.png)  
Leader's view:  
![project-tasks-lead](screenshots/task%20detail4.png)

---

## 🧪 Review Tasks (Leader Only)

Tasks under code review with:
- User name  
- Solution link  
- Project name  

![project-tasks-lead](screenshots/task%20rev.png)

**"Confirm & Archive"** button marks the task as completed and archives it.

---

## 🧑‍💻 My Tasks

### - Current Tasks

Tasks assigned or self-assigned by user.

![project-tasks-lead](screenshots/tasks%20curr.png)

### - Task Archive

Tasks marked `Done` or `Review`, including project links.

![project-tasks-lead](screenshots/arch1.png)  
![project-tasks-lead](screenshots/arch2.png)  
![project-tasks-lead](screenshots/arch3.png)

---

## 🧑‍🤝‍🧑 Our Command

### - Team Members

Displays all team members and their departments.  
Leaders can edit incorrect info.

![project-tasks-lead](screenshots/archive.png)  
![project-tasks-lead](screenshots/archive1.png)  
**Details:**  
![project-tasks-lead](screenshots/click.png)  
![project-tasks-lead](screenshots/click%201.png)

**Leader’s view:**  
![project-tasks-lead](screenshots/scr1.png)  
![project-tasks-lead](screenshots/scr2.png)  
![project-tasks-lead](screenshots/scr3.png)

---

## 📦 Project Archive

Displays completed projects.  
Details view available.

![project-tasks-lead](screenshots/scr4.png)  
![project-tasks-lead](screenshots/scr5.png)

---

## 🔚 Logout

Hover over "Welcome {username}" to reveal the **Sign Out** option.  
Logs out the user and redirects to the login page.



---
# 5. ⚙️ Getting Started

### 📦 Prerequisites

- Python 3.10+
- PostgreSQL (or SQLite for local)
- pip
- virtualenv (recommended)

### 🔧 Installation


## Clone the repo
git clone https://github.com/stager0/teamwork-hub.git
cd teamwork-hub

## Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

## Install dependencies
pip install -r requirements.txt

## Apply database migrations
python manage.py migrate

## 👤 Create a Superuser (for Admin Access)

python manage.py createsuperuser

or load test data using:

python manage.py loaddata fixture.db.json

## Run the development server
python manage.py runserver

## Run all unit tests
python manage.py test