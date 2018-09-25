# Custom Field Checker
# Version 1.0 25 September 2018
# Created by Jeff Mitchell
# Returns a list of students who have not had their Student ID added
# to their Course information field
# Data is sourced from the 'Student Course Information' report from the 
# Learning Platform Ad-hoc database query

# To Add:

# - Check Tutor Listed against the list of student - tutor pairings
# - Add print statements for each field loading (e.g. automatically)

import csv
import custtools.admintools as ad
import custtools.filetools as ft
import sys


def check_fields_data(report_data):
    """Check fields data has required information.
    
    Checks the Student Profile Fields report data to see if the 
    required information is present. Missing or incorrect information that is 
    non-fatal is appended to a warnings list and returned.

    Args:
        report_data (list): Profile Fields data.

    Returns:
        True if warnings list has had items appended to it, False otherwise.
        warnings (list): Warnings that have been identified in the data.

    File Structure (Student Profile Fields data):
        idnumber, firstname, lastname, data.
        
    File Source (Student Profile Fields data):
        Student Course Information database query in the Learning Platform.
    """
    errors = []
    warnings = ['\nStudent Profile Fields Report Warnings:\n']
    for student in report_data:
        if student[1] in (None, ''):
            warnings.append('First Name is missing for student with '
                            'Student ID {}'.format(student[0]))
        if student[2] in (None, ''):
            warnings.append('Last Name is missing for student with Student ID'
                          ' {}'.format(student[0]))
        if student[3] in (None, ''):
            errors.append('Data is missing for student with Student ID {}'
                          .format(student[0]))
    # Check if any errors have been identified, save error log if they have
    if len(errors) > 0:
        ft.process_error_log(errors, 'Student Profile Fields Report')
    # Check if any warnings have been identified, save error log if they have
    if len(warnings) > 1:
        return True, warnings
    else:
        return False, warnings


def check_s_t(report_data):
    """Check students tutors data has required information.
    
    Checks the Students Tutors report data to see if the required information
    is present. Missing or incorrect information that is non-fatal is appended
    to a warnings list and returned.

    Args:
        report_data (list): Students Tutors data.

    Returns:
        True if warnings list has had items appended to it, False otherwise.
        warnings (list): Warnings that have been identified in the data.

    File Structure (Students Tutors data):
        StudentPK, NameGiven, NameSurname, CoursePK, Tutor.
        
    File Source (Students Tutors data):
        qryStudentsTutors + added students from Student Database.
    """
    errors = []
    warnings = ['\nStudents Tutors data Warnings:\n']
    for student in report_data:
        if student[1] in (None, ''):
            warnings.append('First Name is missing for student with '
                            'Student ID {}'.format(student[0]))
        if student[2] in (None, ''):
            warnings.append('Last Name is missing for student with Student ID'
                          ' {}'.format(student[0]))
        if student[3] in (None, ''):
            warnings.append('Course is missing for student with Student ID {}'
                          .format(student[0]))
        if student[4] in (None, ''):
            errors.append('Tutor is missing for student with Student ID {}'
                          .format(student[0]))
    # Check if any errors have been identified, save error log if they have
    if len(errors) > 0:
        ft.process_error_log(errors, 'Student Tutors Data')
    # Check if any warnings have been identified, save error log if they have
    if len(warnings) > 1:
        return True, warnings
    else:
        return False, warnings


def extract_items(st_data):
    """Extract lists from a list of lists.
    
    Args:
        st_data (list): List of lists of student data.
        
    Returns:
        extracted_lists (list): Each item is a list.
    """
    extracted_lists = []
    # ad.debug_list(st_data)
    # print(st_data[0][0])
    i = 0
    while i < len(st_data[0]):
        student = st_data[0][i]
        extracted_lists.append(student)
        i += 1
    return extracted_lists


def extract_tutors(tutor_data):
    """Generate list of tutors.
    
    Extracts each tutor that is a list within a list and returns one list
    with each item being a tutor.
    
    Args:
        tutor_data (list): List of lists containing Tutor names.
        
    Returns:
        extracted_tutors (list): Single list with each item being one
        tutor name.
    """
    extracted_tutors = []
    i = 0
    while i < len(tutor_data[0]):
        # Get tutor (as a list)
        item = tutor_data[0][i]
        # Append tutor as a string
        extracted_tutors.append(item[0])
        i += 1
    return extracted_tutors


def find_student_ids(student_data):
    """Find missing students.
    
    Looks for the string 'FitNZ' within the data field for each student. If
    'FitNZ' is not found the Student ID, First Name and Last Name of the
    student are added to the list that is returned. If the string is found,
    checks if the Student ID number provided matches the students correct
    Student ID.
    
    Args:
        student_data (list): Student data to be checked.
        
    Returns:
        missing_students (list): Students that are missing their Student ID.
    """
    identifier = 'FitNZ'
    missing_students = []
    i = 0
    while i < len(student_data[0]):
        student = student_data[0][i]
        this_student = []
        if identifier in student[3]:
            # Check if Student ID is correct
            # Get location of start of 'FitNZ'
            location = student[3].find(identifier)
            # Take 9 characters of Student ID
            student_id = student[3][location:location + 9]
            # Compare this to student[0]
            # If different, append to missing_students
            if student_id != student[0]:
                this_student.append(student[0])
                this_student.append(student[1])
                this_student.append(student[2])
                missing_students.append(this_student)
            i += 1
        else: # Student ID not found
            this_student.append(student[0])
            this_student.append(student[1])
            this_student.append(student[2])
            missing_students.append(this_student)
            i += 1
    return missing_students
    

def find_tutors(student_data, tutor_names, st_data):
    """Find students that are missing their tutor.
    
    Looks for one of the valid tutor names within the data field for each
    student. If noen are found the Student ID, First Name and Last Name of the
    student are added to the list that is returned.
    
    Args:
        student_data (list): Student data to be checked.
        tutor_names (list): Valid tutor names.
        st_data (list): List of students and their tutor in Learning Platform.
        
    Returns:
        missing_tutors (list): Students that are missing their Tutor name.
    """
    # For each student, check for each tutor in list
    # If a tutor is found, move on to next student
    # If none of the tutors are found, add student to the missing list
    missing_tutors = []
    i = 0
    while i < len(student_data[0]):
        student = student_data[0][i]
        tutor_found = False
        this_student = []
        # Check if each tutor name is present
        j = 0 # Position of tutor in tutor_names
        while j < len(tutor_names) and not tutor_found:
            # print('Tutor: {}'.format(tutor_names[j]))
            # print('Student: {}'.format(student[3]))
            if tutor_names[j] in student[3]:
                # Tutor found, check if it is the correct tutor for the student
                for item in st_data:
                    # print('Item 0: {}'.format(item[0]))
                    if item[0] == student[0]:
                        # Student IDs match
                        # print('Student found!')
                        if tutor_names[j] != item[4]:
                            # Tutors are different
                            """
                            print('Student found: {}'.format(student[0]))
                            print('tutor_names: {}'.format(tutor_names[j]))
                            print('st_data tutor: {}'.format(item[4]))
                            """
                            this_student.append(student[0])
                            this_student.append(student[1])
                            this_student.append(student[2])
                            this_student.append(item[4])
                            missing_tutors.append(this_student)
                        break 
                # print('Tutor found: {}'.format(tutor_found))
                tutor_found = True
            else:
                j += 1
        if not tutor_found: # Tutor not found
            # Get tutor name
            tutor = ''
            for item in st_data:
                # Find student
                if item[0] == student[0]:
                    tutor = item[4]
                    break
            this_student.append(student[0])
            this_student.append(student[1])
            this_student.append(student[2])
            this_student.append(tutor)
            missing_tutors.append(this_student)
        i += 1
    # ad.debug_list(missing_tutors)
    return missing_tutors


def load_data(file_name, source):
    """Read data from a file.

    Args:
        file_name (str): The name of the file to be read.
        source (str): The code for the table that the source data belongs to.

    Returns:
        read_data (list): A list containing the data read from the file.
        True if warnings list has had items appended to it, False otherwise.
        warnings (list): Warnings that have been identified in the data.
    """
    read_data = []
    warnings = []
    # print('File name = ' + str(file_name))
    # Check that file exists
    valid_file = False
    while not valid_file:
        try:
            file = open(file_name + '.csv', 'r')
        except IOError:
            print('The file {}.csv does not exist. Please check the file name '
                  'before trying again.'.format(file_name))
            file_name = input('What is the name of the file? ')
        else:
            file.readline()
            reader = csv.reader(file, delimiter=',', quotechar='"')
            for row in reader:
                if row[0] not in (None, ''):
                    read_data.append(row)
            file.close()
            # Check that data has entries for each required column
            if source == 'fields_data':
                check_fields_data(read_data)
            elif source == 'students_tutors':
                check_s_t(read_data)
            valid_file = True
    if len(warnings) > 0:
        return read_data, True, warnings
    else:
        return read_data, False, warnings


def main():
    repeat = True
    low = 1
    high = 3
    while repeat:
        try_again = False
        main_message()
        try:
            action = int(input('\nPlease enter the number for your '
                               'selection --> '))
        except ValueError:
            print('Please enter a number between {} and {}.'.format(low, high))
            try_again = True
        else:
            if int(action) < low or int(action) > high:
                print('\nPlease select from the available options ({} - {})'
                      .format(low, high))
                try_again = True
            elif action == low:
                process_student_ids()
            elif action == 2:
                process_tutor_names()
            elif action == high:
                print('\nIf you have generated any files, please find them '
                      'saved to disk. Goodbye.')
                sys.exit()
        if not try_again:
            repeat = ad.check_repeat()
    print('\nPlease find your files saved to disk. Goodbye.')


def main_message():
    """Print the main message."""
    print('\n\n*************==========================*****************')
    print('\nCustom Field Checker version 1.0')
    print('Created by Jeff Mitchell, 2018')
    print('\nOptions:')
    print("\n1 Check Student ID's")
    print('2 Check Tutor Names')
    print('3 Exit')


def process_student_ids():
    """Process missing Student ID's from Student Profile Field."""
    warnings = ['\nProcessing Student IDs data Warnings:\n']
    warnings_to_process = False
    print('\nStudent ID Data.')
    # Confirm the required files are in place
    required_files = ['Student Profile Fields Data']
    ad.confirm_files('Student ID Data', required_files)
    # Load data
    f_name = ft.get_load_file_name()
    s_name = 'Missing_Student_IDs_{}'.format(ft.generate_time_string())
    print('\nLoading {}...'.format(f_name))
    student_data = load_data(f_name, 'fields_data')
    print('\nLoaded {}.'.format(f_name))
    # print('Student_data = {}'.format(len(student_data)))
    # ad.debug_list(student_data)
    missing_students = find_student_ids(student_data)
    headings = ['Student ID', 'First Name', 'Last Name']
    save_students(missing_students, headings, s_name)
    ft.process_warning_log(warnings, warnings_to_process)
    

def process_tutor_names():
    """Check if Student Profile fields contains a valid Tutor."""
    warnings = ['\nProcessing Tutor Names data Warnings:\n']
    warnings_to_process = False
    print('\nTutor Names Data.')
    # Confirm the required files are in place
    required_files = ['Student Profile Fields Data', 'Tutors',
                      'Student Tutors']
    ad.confirm_files('Tutor Names Data', required_files)
    # Load student data
    f_name = ft.get_load_file_name()
    print('Loading Tutor Names data...')
    student_data = load_data(f_name, 'fields_data')
    print('\nLoaded {}.'.format(f_name))
    # Load tutor names
    tutor_f_name = 'tutors'
    print('Loading Tutors data')
    tutor_data = load_data(tutor_f_name, 'tutor_names')
    print('\nLoaded {}.'.format('tutors.csv'))
    # Create a list with tutor names
    tutors = extract_tutors(tutor_data)
    # Load student - tutor pairings (Student Database)
    st_name = 'studentstutors'
    print('Loading Student-Tutors data')
    st_data = load_data(st_name, 'studentstutors.csv')
    print('\nLoaded {}.'.format('tutors.csv'))
    st_data = extract_items(st_data)
    # ad.debug_list(st_data)
    missing_tutors = find_tutors(student_data, tutors, st_data)
    # ad.debug_list(missing_tutors)
    headings = ['Student ID', 'First Name', 'Last Name', 'Tutor']
    s_name = 'Missing_Tutors_{}'.format(ft.generate_time_string())
    save_students(missing_tutors, headings, s_name)
    ft.process_warning_log(warnings, warnings_to_process)


def save_students(input_data, headings_data, file_name):
    """Save the data to a CSV file.
    
    Args:
        input_data (list): Data to be saved.
        headings_data (list): Column headings to be used.
        file_name (str): File name to be saved to.
    """
    i_data = input_data
    headings = headings_data
    d_name = file_name
    f_name = file_name + '.csv'
    try:
        open(f_name, 'w')
    except IOError:
        print('Unable to save {} data. Please try again.'.format(d_name))
    else:
        with open(f_name, 'w', newline='') as csv_file:
            headingWriter = csv.DictWriter(csv_file,
                                           fieldnames=headings)
            headingWriter.writeheader()
            writer = csv.writer(csv_file)
            for item in i_data:
                writer.writerows([item])
        print('{} has been saved to {}'.format(d_name, f_name))


if __name__ == '__main__':
    main()