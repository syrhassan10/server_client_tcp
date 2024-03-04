
import csv

def get_averages(file_path):
    '''
    Array contents = [Lab 1,Lab 2,Lab 3,Lab 4,Midterm,Exam 1,Exam 2,Exam 3,Exam 4]
    '''
    grades = [0] * 9

    i = 3
    count =0
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            i = 3
            count = count + 1
            for j in range(9):
                grades[j] += int(row[i])
                print(j)
                i = i + 1

    
    for i in range (len(grades)):
        grades[i] = grades[i] / count


    return grades







file_path = "course_grades_2024.csv"

print(get_averages(file_path))
