# django-streamlit
a demo for combining django and streamlit to create a website that allows users to enter required information for their respective reports. Facilitates login, user permisions report etc.
The purpose of this system is the following: 
- accept user data that must be entered manually for reports
- manage user permissions and their report access rights
- validate user data before pushing to the db


# Reports 
The `Report()` object in the context of this site reffers to the manual data entry portion of some report from the RCMA department. 

### Report Types

- **Deadline** - reports with a deadline have a time and/or date deadline (attriubte in their model) that is not null - this will automatically mean the report is of the deadline variety.
- **non-deadline** - reports without a deadline (such as mapping sheets) may be updated at any time. 



# Users

### General Interface Requirements 
- Users shall be notified of upcoming reports by way of their home page
- Users shall see all dates and deadlines with respect to their time zone

### User Account Requirements

#### Users shall be able to save the following attributes to their user profile in some capacity:
 - name
 - role
 - work location (acbo, wcbo, corporate office) -> maps to timezone

#### Users shall be able to perform the following on reports they have access to:
- view the current state of the report
- edit (if permitted) an existing manual entry form that has already been completed
- be given the option (if allowed to edit) to modify the most recently submitted report if past deadline


# Data Entry 
if a user has permission to edit a report, he or she will be directed to a streamlit app that will do the following:

1. fetch a dataframe from the db of rows that tie to this user via their email
2. load a streamlit table populated with the information in that dataframe
3. allow the user to add,edit, and remove rows from the table
4. once the table is ready for submission, ensure the following:
 - all data types match the column types of the db
 - any integrity violations (null, foreignkey violation, uniqueness) are raised to the user


### Data Entry Form (Streamlit) Requirements
- Concurrent data entry shall be allowed
- Data type validation shall not be allowed to enter the db
- Data type validation checks shall notify the user if he/she attempts to input a value of the wrong
- Valid data entries shall be automatically pushed to the db






