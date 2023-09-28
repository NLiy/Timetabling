# By Group 2
# NURULAIN LIYANA BINTI ALILOR (BI20110162)
# NURUL SYAFIKA BINTI MUHAMAD (BI20110178)
# NURSYAHIRAH BINTI MURAT (BI20110133)
# SITI ASMAH BINTI MUHAMAD (BI20160305)

# 91 courses; 417 classes; 33 rooms; 821 students; 645 distributions

from lxml import etree 
import random
import math
import copy
import time

def classList(root):
    classes = root.findall('courses/course/config/subpart/class')

    classList = []
    for i, kelas in enumerate(classes):
        classList.append(kelas.get('id'))

    return classList

def classTime(root):
    classes = root.findall('courses/course/config/subpart/class')

    classTime = []
    
    for i, kelas in enumerate(classes):
        timeList = []
        for time in kelas.findall('time'):
            days = time.get('days')
            start = time.get('start')
            length = time.get('length')
            weeks = time.get('weeks')
            penalty = time.get('penalty')
            timeset = (days, start, length, weeks, penalty)
            timeList.append(timeset)

        classTime.append(timeList)
    
    return classTime

def classRoom(root):
    classes = root.findall('courses/course/config/subpart/class')

    classRoom = []
    
    for i, kelas in enumerate(classes):
        roomList = []
        for room in kelas.findall('room'):
            roomId = room.get('id')
            penalty = room.get('penalty')
            roomset = (roomId, penalty) #
            roomList.append(roomset) #

        classRoom.append(roomList)
    
    return classRoom

def studentCourse(root):
    students = root.findall('students/student')
    courses = root.findall('courses/course')

    matrix = [
        [0 for j in range(len(courses))]
        for i in range(len(students))
        ]
    
    # Dictionary col_index to map the course IDs to column indices
    col_index = {}
    for i, course in enumerate(courses):
        col_index[course.get('id')] = i

    # Populate the matrix with the data
    for i, student in enumerate(students):
        for course in student.findall('course'):
            j = col_index[course.get('id')]
            matrix[i][j] = 1
    
    return matrix

def courseConfig(root):
    courses = root.findall('courses/course')
    
    courseConfig = []
    
    for i, course in enumerate(courses):
        configList = []
        for config in course.findall('config'):
            configId = config.get('id')
            configList.append(configId) 

        courseConfig.append(configList)
    
    return courseConfig

def configSubpart(root):
    configs = root.findall('courses/course/config')
    
    configSubpart = []
    
    for i, config in enumerate(configs):
        subpartList = []
        for subpart in config.findall('subpart'):
            subpartId = subpart.get('id')
            subpartList.append(subpartId) 

        configSubpart.append(subpartList)
    
    return configSubpart

def subpartClass(root):
    subparts = root.findall('courses/course/config/subpart')
    
    subpartClass = []
    
    for i, subpart in enumerate(subparts):
        subpartList = []
        for kelas in subpart.findall('class'):
            classId = kelas.get('id')
            subpartList.append(classId) 

        subpartClass.append(subpartList)
    
    return subpartClass

def studentClass(root):
    StudentCourse = studentCourse(root)
    CourseConfig = courseConfig(root)
    ConfigSubpart = configSubpart(root)
    SubpartClass = subpartClass(root)

    studentClassList = []
    #student sectioning:
    # Iterate over the student and extract the courses taken by each student.
    for student in range(len(StudentCourse)):
        classList = []
        for course in range(len(StudentCourse[student])):
            if StudentCourse[student][course] == 1:
                # For each course, select one config and all subparts of that config.
                selectedConfig = random.choice(CourseConfig[course])
                selectedSubpart = ConfigSubpart[CourseConfig[course].index(selectedConfig)]

                # For each subpart, select one class.
                for kelas in range(len(selectedSubpart)):
                    selectedClass = random.choice(SubpartClass)
                    classList.append(selectedClass)
        
        studentClassList.append(classList)

    return studentClassList

def satisfies_maxdayload(distributions, curClass, curLength, Timetable):
    maxDayLoadList = []
    for distribution in distributions:
        distribution_type = distribution.get('type')
        if distribution_type.startswith('MaxDayLoad'):
            max_day_load = int(distribution_type.split('(')[1].split(')')[0])
            MDLlist = []
            for kelas in distribution.findall('class'):
                MDLlist.append(kelas.get('id'))
            maxDayLoadList.append((MDLlist, max_day_load))

    totalLength = 0
    for sublist in maxDayLoadList:
        if curClass in sublist[0]:
            for classid in sublist[0]:
                
                for day in Timetable:
                    for timeslot in day:
                        for room in timeslot:
                            if (room != 0) and (classid in room) and (classid != curClass):
                                totalLength += 1
            
            if (totalLength + curLength) <= sublist[1]:
                return True
            else:
                return False
    return True

def satisfies_samedays(distributions, curClass, curDay, Timetable):
    sameDaysList = []
    for distribution in distributions:
        if distribution.get('type') == 'SameDays' and distribution.get('required') == 'true':
            SDlist = []
            for kelas in distribution.findall('class'):
                SDlist.append(kelas.get('id'))
            sameDaysList.append(SDlist)

    for sublist in sameDaysList:
        if curClass in sublist:
            for classid in sublist:

                for d, day in enumerate(Timetable):
                    for timeslot in day:
                        for room in timeslot:
                            if (room != 0) and (classid != curClass) and (d == curDay):
                                return True
                            else:
                                return False
    return True

def satisfies_differentdays(distributions, curClass, curDay, Timetable):
    differentDaysList = []
    for distribution in distributions:
        if distribution.get('type') == 'DifferentDays' and distribution.get('required') == 'true':
            DDlist = []
            for kelas in distribution.findall('class'):
                DDlist.append(kelas.get('id'))
            differentDaysList.append(DDlist)

    for sublist in differentDaysList:
        if curClass in sublist:
            for classid in sublist:

                for d, day in enumerate(Timetable):
                    for timeslot in day:
                        for room in timeslot:
                            if (room != 0) and (classid != curClass) and (d != curDay):
                                return True
                            else:
                                return False
    return True

def satisfies_sameattendees(distributions, rooms, curClass, curDay, curStart, curLength, curRoomId, Timetable):
    sameAttendeesList = []
    for distribution in distributions:
        if distribution.get('type') == 'SameAttendees' and distribution.get('required') == 'true':
            SAlist = []
            for kelas in distribution.findall('class'):
                SAlist.append(kelas.get('id'))
            if len(SAlist) > 1:
                sameAttendeesList.append(SAlist)
            else:
                print(f"Warning: SameAttendees distribution with only one class: {SAlist}")
    
    travelRoomList = []
    for room in rooms:
        roomid = room.get('id')

        travelInfo = []
        for travel in room.findall('travel'):
            travelroom = travel.get('room')
            travelvalue = travel.get('value')
            travelInfo.append((travelroom, travelvalue))

        travelRoomList.append((roomid, travelInfo))

    curEnd = curStart + curLength
    length_2 = 0
    for sublist in sameAttendeesList:
        if curClass in sublist[0]:
            for classid in sublist[0]:
                
                for d, day in enumerate(Timetable):
                    for start_2, timeslot in enumerate(day):
                        for roomid, room in enumerate(timeslot):
                            if (room != 0) and (classid in room) and (classid != curClass):
                                length_2 = 0

            end_2 = start_2 + length_2

            gap1 = start_2 - curEnd
            gap2 = curStart - end_2

            if curDay == d:
                for subtravel in travelRoomList:
                    if str(curRoomId) in subtravel[0]:
                        for travelroom in subtravel[1]:
                            if (subtravel[1] != []) and str(roomid) in travelroom[0]:
                                value = int(travelroom[1])
                                if (value <= gap1) or (value <= gap2):
                                    return True
                                else:
                                    return False
    return True 

def satisfies_mingap(distributions, curClass, curStart, curLength, Timetable):
    minGapList = []
    for distribution in distributions:
        distribution_type = distribution.get('type')
        if distribution_type.startswith('MinGap'):
            min_gap = int(distribution_type.split('(')[1].split(')')[0])
            MGlist = []
            for kelas in distribution.findall('class'):
                MGlist.append(kelas.get('id'))
            minGapList.append((MGlist, min_gap))
    
    curEnd = curStart + curLength

    length_2 = 0
    for sublist in minGapList:
        if curClass in sublist[0]:
            for classid in sublist[0]:
                
                for day in Timetable:
                    for start_2, timeslot in enumerate(day):
                        for room in timeslot:
                            if (room != 0) and (classid in room) and (classid != curClass):
                                length_2 = 0

            end_2 = start_2 + length_2

            if (start_2 - curEnd <= sublist[1]) or (curStart - end_2 <= sublist[1]):
                return True
            else:
                return False

    return True 

def initialSolution():
    start_time = time.time()

    xmlFile = etree.parse('yach-fal17.xml')
    root = xmlFile.getroot()
    distributions = root.findall('distributions/distribution')
    rooms = root.findall('rooms/room')

    # lists
    ClassList = classList(root)
    UnassignClassList = copy.copy(ClassList)
    ClassTime = classTime(root)
    ClassRoom = classRoom(root)

    # initialize timetable
    Timetable = [[[0 for k in range(33)] for j in range(288)] for i in range(7)]

    Max_iteration = 2000
    iteration_count = 0

    while UnassignClassList:
        if iteration_count < Max_iteration:
            iteration_count += 1

            # pick a random class
            curClass = random.choice(UnassignClassList)
            curClassIndex = ClassList.index(curClass)

            # pick a random timeset
            curTime = random.choice(ClassTime[curClassIndex])
            curDay = int(curTime[0])
            curStart = int(curTime[1])
            curLength = int(curTime[2])

            if curDay // 1000000 == 1:
                day = 0  # mon
            elif curDay // 100000 == 1:
                day = 1  # tue
            elif curDay // 10000 == 1:
                day = 2  # wed
            elif curDay // 1000 == 1:
                day = 3  # thu
            elif curDay // 100 == 1:
                day = 4  # fri
            elif curDay // 10 == 1:
                day = 5  # sat
            elif curDay // 1 == 1:
                day = 6  # sun

            # pick a random room
            curRoom = random.choice(ClassRoom[curClassIndex])
            curRoomId = int(curRoom[0])
            
            # check constraints
            violation_flag = True

            if satisfies_maxdayload(distributions, curClass, curLength, Timetable):
                if satisfies_samedays(distributions, curClass, day, Timetable):
                    if satisfies_differentdays(distributions, curClass, day, Timetable):
                        if satisfies_sameattendees(distributions, rooms, curClass, day, curStart, curLength, curRoomId, Timetable):
                            if satisfies_mingap(distributions, curClass, curStart, curLength, Timetable):
                                violation_flag = False
                            else: #not satisfies_mingap
                                continue
                        else: #not satisfies_sameattendees
                            continue
                    else: #not satisfies_differentdays
                        continue
                else: #not satisfies_samedays
                    continue
            else: #not satisfies_maxdayload
                continue
                
            if not violation_flag: 
                UnassignClassList.remove(curClass)
                # assign the class into timetable
                for i in range(curLength):
                    if Timetable[day][curStart-1][curRoomId-1] == 0:
                        Timetable[day][curStart-1][curRoomId-1] = [curClass]
                    else:
                        Timetable[day][curStart-1][curRoomId-1].append(curClass)
                    curStart += 1
        
        else:
            # pick a random class
            curClass = random.choice(UnassignClassList)
            curClassIndex = ClassList.index(curClass)

            # pick a random timeset
            curTime = random.choice(ClassTime[curClassIndex])
            curDay = int(curTime[0])
            curStart = int(curTime[1])
            curLength = int(curTime[2])

            if curDay // 1000000 == 1:
                day = 0  # mon
            elif curDay // 100000 == 1:
                day = 1  # tue
            elif curDay // 10000 == 1:
                day = 2  # wed
            elif curDay // 1000 == 1:
                day = 3  # thu
            elif curDay // 100 == 1:
                day = 4  # fri
            elif curDay // 10 == 1:
                day = 5  # sat
            elif curDay // 1 == 1:
                day = 6  # sun

            # pick a random room
            curRoom = random.choice(ClassRoom[curClassIndex])
            curRoomId = int(curRoom[0])

            # assign the class into timetable
            UnassignClassList.remove(curClass)
            for i in range(curLength):
                if Timetable[day][curStart-1][curRoomId-1] == 0:
                    Timetable[day][curStart-1][curRoomId-1] = [curClass]
                else:
                    Timetable[day][curStart-1][curRoomId-1].append(curClass)
                curStart += 1
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Initial solution execution time: {execution_time} seconds")
    return Timetable

def timetableHash(timetable):
    timetableHash = {}

    for day, day_schedule in enumerate(timetable):
        for timeslot, timeslot_schedule in enumerate(day_schedule):
            for room, classIDs in enumerate(timeslot_schedule):
                if isinstance(classIDs, list) and classIDs:
                    for classID in classIDs:
                        if classID not in timetableHash:
                            timetableHash[classID] = []

                        start = timeslot

                        position = day, start, room

                        timetableHash[classID].append(position)

    return timetableHash

def getClassPosition(timetableHash, classID):
    listPos = timetableHash[classID]
    day = listPos[0][0]
    start = listPos[0][1]
    room = listPos[0][2]
    duration = len(listPos)
    end = start + duration - 1

    position = day, start, end, room

    return position

def sameRoom(root, timetable):
    distributions = root.findall('distributions/distribution')

    sameRoomList = []
    penaltyList = []
    for distribution in distributions:
        if distribution.get('type') == 'SameRoom':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            sameRoomList.append(classList)
            penaltyList.append(distribution.get('penalty'))
            
    TimetableHash = timetableHash(timetable)
    for i, row in enumerate(sameRoomList):
        for j, classID in enumerate(row):
            classID = sameRoomList[i][j]
            position = getClassPosition(TimetableHash, classID) 
            
            if position:
                room = position[3]

                sameRoomList[i][j] = room+1 
    
   # calculate the penalty
    penaltySameRoom = 0
    for i in range(len(sameRoomList)):
        for j in range(len(sameRoomList[i])):
            for k in range(j+1, len(sameRoomList[i])):
                # check which pair of room has different room
                if sameRoomList[i][j] != sameRoomList[i][k]:
                    penaltySameRoom = penaltySameRoom + int(penaltyList[i]) 
    
    return penaltySameRoom

def sameDays(root, timetable):
    distributions = root.findall('distributions/distribution')
    
    sameDaysList = []
    for distribution in distributions:
        if distribution.get('type') == 'SameDays' and distribution.get('required') == 'true':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            sameDaysList.append(classList)

    # If no SameDays distributions with required="true" and multiple classes are found, return -1
    if not sameDaysList:
        print("Error: No SameDays distributions with required=\"true\" and multiple classes found.")
        return -1
    
    # Calculate the penalty for violating the SameDays constraint
    TimetableHash = timetableHash(timetable)
    penaltySameDays = 0
    for classList in sameDaysList:
        days = set()
        # Check if all classes in the SameDaysList are scheduled on the same day
        for classID in classList:
            # Get the position of the current class in the timetable
            position = getClassPosition(TimetableHash, classID)
            if position:
                # Add the day of the week on which the current class is scheduled to the days set
                days.add(position[0])
        if len(days) > 1:
            # If the classes in the SameDaysList are scheduled on different days, increment the penalty value
            penaltySameDays += len(days) - 1

    return penaltySameDays

def sameAttendees(root, timetable):
    distributions = root.findall('distributions/distribution')
   
    sameAttendeesList = []
    for distribution in distributions:
        if distribution.get('type') == 'SameAttendees' and distribution.get('required') == 'true':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            if len(classList) > 1:
                sameAttendeesList.append(classList)
            else:
                print(f"Warning: SameAttendees distribution with only one class: {classList}")
    if not sameAttendeesList:
        print("Warning: No SameAttendees distributions with required=\"true\" and multiple classes found.")
        return 0
    
    # Search room id for each class ID; replace the class id with its room id value
    TimetableHash = timetableHash(timetable)
    for i, row in enumerate(sameAttendeesList):
        for j, classID in enumerate(row):
            position = getClassPosition(TimetableHash, classID)
            if position:
                day, start, end, room = position
                sameAttendeesList[i][j] = (classID, room+1)
            else:
                print(f"Error: Class ID {classID} not found in timetable.")
                return -1
    
    # Calculate the penalty
    penaltySameAttendees = 0
    for i in range(len(sameAttendeesList)):
        for j in range(len(sameAttendeesList[i])):
            for k in range(j+1, len(sameAttendeesList[i])):
                if sameAttendeesList[i][j][1] != sameAttendeesList[i][k][1]:
                    penaltySameAttendees += 1 

    return penaltySameAttendees

def differentDays(root, timetable):
    distributions = root.findall('distributions/distribution')
    differentDaysList = []
    for distribution in distributions:
        if distribution.get('type') == 'DifferentDays' and distribution.get('required') == 'true':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            differentDaysList.append(classList)

    TimetableHash = timetableHash(timetable)
    for i, row in enumerate(differentDaysList):
        for j, classID in enumerate(row):
            position1 = getClassPosition(TimetableHash, classID)
            if position1:
                day = position1[0]
                differentDaysList[i][j] = day

    penaltyDifferentDays = 0
    for i in range(len(differentDaysList)):
        for j in range(len(differentDaysList[i])):
            for k in range(j+1, len(differentDaysList[i])):
               
                if differentDaysList[i][j] == differentDaysList[i][k]:
                    penaltyDifferentDays += 1

    return penaltyDifferentDays

def notOverlap(root, timetable):
    distributions = root.findall('distributions/distribution')

    notOverlapList = []
    penaltyList = []
    for distribution in distributions:
        if distribution.get('type') == 'NotOverlap':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            notOverlapList.append(classList)
            penaltyList.append(distribution.get('penalty'))

    # calculate the penalty
    TimetableHash = timetableHash(timetable)
    penaltyNotOverlap = 0
    for i in range(len(notOverlapList)):
        for j in range(len(notOverlapList[i])):
            for k in range(j+1, len(notOverlapList[i])):

                classID_1 = notOverlapList[i][j]
                position_1 = getClassPosition(TimetableHash, classID_1) 

                if position_1:
                    day_1 = position_1[0]
                    start_1 = position_1[1]
                    end_1 = position_1[2]

                classID_2 = notOverlapList[i][k]
                position_2 = getClassPosition(TimetableHash, classID_2)

                if position_2:
                    day_2 = position_2[0]
                    start_2 = position_2[1]
                    end_2 = position_2[2]

                #if the 2 classes on the same day, must not overlap the timeslot
                if day_1 == day_2:
                    if not (end_1 <= start_2 or end_2 <= start_1):
                        penaltyNotOverlap = penaltyNotOverlap + int(penaltyList[i])

    return penaltyNotOverlap

def MinGap(root, timetable):
    distributions = root.findall('distributions/distribution')

    minGapList = []
    for distribution in distributions:
        if distribution.get('type') == 'MinGap(6)' and distribution.get('required') == 'true':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            minGapList.append(classList)

    # Calculate the penalty based on minimum gap between classes
    TimetableHash = timetableHash(timetable)
    penaltyMinGap = 0
    for i in range(len(minGapList)):
        for j in range(len(minGapList[i])):
            for k in range(j + 1, len(minGapList[i])):

                classID_1 = minGapList[i][j]
                position_1 = getClassPosition(TimetableHash, classID_1)

                if position_1:
                    start_1 = position_1[1]
                    end_1 = position_1[2]

                classID_2 = minGapList[i][k]
                position_2 = getClassPosition(TimetableHash, classID_2)

                if position_2:
                    start_2 = position_2[1]
                    end_2 = position_2[2]

                # the different between 2 timeslot cannot less than 6
                timeslot_1 = start_2 - end_1 + 1
                timeslot_2 = start_1 - end_2 + 1
                if timeslot_1 < 6 or timeslot_2 < 6:
                    penaltyMinGap += 1  # 1 penalty for each violation

    return penaltyMinGap

def MaxDayLoad(root, timetable):
    distributions = root.findall('distributions/distribution')

    maxDayLoadList = []
    TimetableHash = timetableHash(timetable)
    penaltyMaxDayLoad = 0
    for distribution in distributions:
        if distribution.get('type') == 'MaxDayLoad(72)' and distribution.get('required') == 'true':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            maxDayLoadList.append(classList)

            total_timeslot = 0

            for i in range(len(maxDayLoadList)):
                for j in range(len(maxDayLoadList[i])):
                    for k in range(j + 1, len(maxDayLoadList[i])):

                        classID = maxDayLoadList[i][j]
                        position = getClassPosition(TimetableHash, classID)

                        if position:
                            start = position[1]
                            end = position[2]

                        # calcuate the total timeslot
                        timeslot = start - end + 1
                        total_timeslot += timeslot

                        if total_timeslot > 60:
                            penaltyMaxDayLoad += 1  # 1 penalty for each violation

        if distribution.get('type') == 'MaxDayLoad(60)' and distribution.get('required') == 'true':
            classList = []
            for kelas in distribution.findall('class'):
                classList.append(kelas.get('id'))
            maxDayLoadList.append(classList)

            total_timeslot = 0

            for i in range(len(maxDayLoadList)):
                for j in range(len(maxDayLoadList[i])):
                    for k in range(j + 1, len(maxDayLoadList[i])):

                        classID = maxDayLoadList[i][j]
                        position = getClassPosition(TimetableHash, classID)

                        if position:
                            start = position[1]
                            end = position[2]

                        # calcuate the total timeslot
                        timeslot = start - end + 1
                        total_timeslot += timeslot
                        
                        if total_timeslot > 60:
                            penaltyMaxDayLoad += 1  # 1 penalty for each violation

    return penaltyMaxDayLoad

def checkHardConstraint(timetable):
    hardConstraint = 0
    xmlFile = etree.parse('yach-fal17.xml')
    root = xmlFile.getroot()

    penaltySameDays = sameDays(root, timetable)
    penaltySameAttendees = sameAttendees(root, timetable)
    penaltyDifferentDay = differentDays(root, timetable)
    penaltyMinGap = MinGap(root, timetable)
    penaltyMaxDayLoad = MaxDayLoad(root, timetable)

    hardConstraint = penaltySameDays + penaltySameAttendees + penaltyDifferentDay + penaltyMinGap + penaltyMaxDayLoad

    return hardConstraint

def checkSoftConstraint(timetable):
    softConstraint = 0
    xmlFile = etree.parse('yach-fal17.xml')
    root = xmlFile.getroot()

    penaltySameRoom = sameRoom(root, timetable)
    penaltyNotOverlap = notOverlap(root, timetable)

    softConstraint = penaltySameRoom + penaltyNotOverlap 

    return softConstraint

def tweak(timetableSolution):
    xmlFile = etree.parse('yach-fal17.xml')
    root = xmlFile.getroot()
    ClassList = classList(root)
    TimetableHash = timetableHash(timetableSolution)

    #choose 6 classID and get their positions
    i = 0
    list_ClassID = [] 
    list_position = []
    while i < 6:
        classID = random.choice(ClassList)
        position = getClassPosition(TimetableHash, classID)

        if classID not in list_ClassID:
            list_ClassID.append(classID)
            list_position.append(position)
            i += 1

    #delete their original positions from timetable
    i=0
    while i < 6:
        if list_position[i]:
                day = list_position[i][0]
                start = list_position[i][1]
                end = list_position[i][2]
                room = list_position[i][3]

        j=0
        while start+j <= end:
            list_element = timetableSolution[day][start+j][room]
            list_element.remove(list_ClassID[i])
            j += 1

        i += 1

    #MOVE 1 = pilih 1 kelas rand then masuk timeslot n room
    classID_1 = list_ClassID[0]

    #assign classId to rand timeslot
    curClassIndex = ClassList.index(classID_1)
    curTime = random.choice(classTime(root)[curClassIndex])

    #assign classID to rand room 
    curClassIndex = ClassList.index(classID_1)
    curRoomId = random.choice(classRoom(root)[curClassIndex])

    curDay = int(curTime[0])
    if curDay // 1000000 == 1:
        day = 0  # mon
    elif curDay // 100000 == 1:
        day = 1  # tue
    elif curDay // 10000 == 1:
        day = 2  # wed
    elif curDay // 1000 == 1:
        day = 3  # thu
    elif curDay // 100 == 1:
        day = 4  # fri
    elif curDay // 10 == 1:
        day = 5  # sat
    elif curDay // 1 == 1:
        day = 6  # sun
    curStart = int(curTime[1])
    curLength = int(curTime[2])
    curRoomId = int(curRoomId[0])

    #assign classID_1 to all timeslots
    for i in range(curLength):
        if isinstance(timetableSolution[day][curStart-1][curRoomId-1], int):
            timetableSolution[day][curStart-1][curRoomId-1] = [classID_1]
        else:
            timetableSolution[day][curStart-1][curRoomId-1].append(classID_1)
        curStart += 1

    #MOVE 2 = select 2 rand class then swap timeslot n room
    classID_2 = list_ClassID[1]
    position_2 = list_position[1]
    day_2 = position_2[0]
    start_2 = position_2[1]
    end_2 = position_2[2]
    room_2 = position_2[3]

    classID_3 = list_ClassID[2]
    position_3 = list_position[2]
    day_3 = position_3[0]
    start_3 = position_3[1]
    end_3 = position_3[2]
    room_3 = position_3[3]

    #swap
    tempDay = day_2
    tempStart = start_2
    tempEnd = end_2
    tempRoom = room_2

    day_2 = day_3
    start_2 = start_3
    end_2 = end_3
    room_2 = room_3

    day_3 = tempDay
    start_3 = tempStart
    end_3 = tempEnd
    room_3 = tempRoom
    
    #assign into the new position
    duration_2 = end_2 - start_2 + 1
    for i in range(duration_2):
        if isinstance(timetableSolution[day_2][start_2-1][room_2-1], int):
            timetableSolution[day_2][start_2-1][room_2-1] = [classID_2]
        else:
            timetableSolution[day_2][start_2-1][room_2-1].append(classID_2)
        start_2 += 1

    duration_3 = end_3 - start_3 + 1
    for i in range(duration_3):
        if isinstance(timetableSolution[day_3][start_3-1][room_3-1], int):
            timetableSolution[day_3][start_3-1][room_3-1] = [classID_3]
        else:
            timetableSolution[day_3][start_3-1][room_3-1].append(classID_3)
        start_3 += 1

    #MOVE 3 = select 3 rand class then swap each other
    classID_4 = list_ClassID[3]
    position_4 = list_position[3]
    day_4 = position_4[0]
    start_4 = position_4[1]
    end_4 = position_4[2]
    room_4 = position_4[3]

    classID_5 = list_ClassID[4]
    position_5 = list_position[4]
    day_5 = position_5[0]
    start_5 = position_5[1]
    end_5 = position_5[2]
    room_5 = position_5[3]

    classID_6 = list_ClassID[5]
    position_6 = list_position[5]
    day_6 = position_6[0]
    start_6 = position_6[1]
    end_6 = position_6[2]
    room_6 = position_6[3]

    #swap 
    tempDay = day_4
    tempStart = start_4
    tempEnd = end_4
    tempRoom = room_4

    day_4 = day_5
    start_4 = start_5
    end_4 = end_5
    room_4 = room_5

    day_5 = day_6
    start_5 = start_6
    end_5 = end_6
    room_5 = room_6

    day_6 = tempDay
    start_6 = tempStart
    end_6 = tempEnd
    room_6 = tempRoom

    #assign into the new position
    duration_4 = end_4 - start_4 + 1
    for i in range(duration_4):
        if isinstance(timetableSolution[day_4][start_4-1][room_4-1], int):
            timetableSolution[day_4][start_4-1][room_4-1] = [classID_4]
        else:
            timetableSolution[day_4][start_4-1][room_4-1].append(classID_4)
        start_4 += 1

    duration_5 = end_5 - start_5 + 1
    for i in range(duration_5):
        if isinstance(timetableSolution[day_5][start_5-1][room_5-1], int):
            timetableSolution[day_5][start_5-1][room_5-1] = [classID_5]
        else:
            timetableSolution[day_5][start_5-1][room_5-1].append(classID_5)
        start_5 += 1

    duration_6 = end_6 - start_6 + 1
    for i in range(duration_6):
        if isinstance(timetableSolution[day_6][start_6-1][room_6-1], int):
            timetableSolution[day_6][start_6-1][room_6-1] = [classID_6]
        else:
            timetableSolution[day_6][start_6-1][room_6-1].append(classID_6)
        start_6 += 1

    return timetableSolution

currentSolution = initialSolution()

currentHardConstPenalty = checkHardConstraint(currentSolution)
currentSoftConstPenalty = checkSoftConstraint(currentSolution)
currentPenalty = currentHardConstPenalty + currentSoftConstPenalty

bestSolution = copy.deepcopy(currentSolution)
bestPenalty = currentPenalty

print('Initial hard constraint: ', currentHardConstPenalty)
print('Initial soft constraint: ', currentSoftConstPenalty)
print('Initial best penalty: ', bestPenalty)

def simulatedAnnealing():
    start_time = time.time()

    temp = 1000
    coolRate = 0.1

    global currentSolution 
    global currentPenalty 

    global bestSolution 
    global bestPenalty 

    while temp > 0:
        candidateSolution = tweak(copy.deepcopy(currentSolution))
        candidateHardConstPenalty = checkHardConstraint(candidateSolution)
        candidateSoftConstPenalty = checkSoftConstraint(candidateSolution)
        candidatePenalty = candidateHardConstPenalty + candidateSoftConstPenalty
                
        randomNumber = random.random()
        SAformula = math.exp(-(candidatePenalty - currentPenalty) / temp)
        
        if candidatePenalty < currentPenalty or randomNumber < SAformula:
            currentSolution = copy.deepcopy(candidateSolution) 
            currentPenalty = candidatePenalty

            if currentPenalty < bestPenalty:
                bestSolution = copy.deepcopy(candidateSolution) 
                bestPenalty = candidatePenalty
        
        temp -= coolRate

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Simulated annealing execution time: {execution_time} seconds")
    return bestSolution

if __name__=="__main__":
    finalSolution = simulatedAnnealing()
    finalHardConstPenalty = checkHardConstraint(finalSolution)
    finalSoftConstPenalty = checkSoftConstraint(finalSolution)
    finalPenalty = finalHardConstPenalty + finalSoftConstPenalty

    print('Final hard constraint penalty: ', finalHardConstPenalty)
    print('Final soft constraint penalty: ', finalSoftConstPenalty)
    print('Final penalty: ', finalPenalty)

    # create xml file
    xmlFile = etree.parse('yach-fal17.xml')
    solution = xmlFile.getroot()
    ClassList = classList(solution)
    StudentClass = studentClass(solution)
    TimetableHash = timetableHash(finalSolution)

    # solution
    root = etree.Element('solution')
    root.set('name', 'yach-fal17')
    root.set('runtime', '1')
    root.set('cores', '1')
    root.set('technique', 'Local Search and Simulated Annealing')
    root.set('author', 'Group 2')
    root.set('institution', 'Universiti Malaysia Sabah')
    root.set('country', 'Malaysia')

    # solution/class
    for i, classId in enumerate(ClassList):
        classElement = etree.SubElement(root, 'class')
        classElement.set('id', classId)

        position = getClassPosition(TimetableHash, classId) 
        if position:
            day = position[0]
            start = position[1]
            end = position[2]
            room = position[3]

        if day == 0:
            days = '1000000'
        elif day == 1:
            days = '0100000' 
        elif day == 2:
            days = '0010000'
        elif day == 3:
            days = '0001000' 
        elif day == 4:
            days = '0000100' 
        elif day == 5:
            days = '0000010' 
        elif day == 6:
            days = '0000001'  

        classElement.set('days', days)
        classElement.set('start', str(start+1))
        classElement.set('weeks', '1111111111111111') #
        classElement.set('room', str(room))

        # solution/class/student
        for studentID, classList in enumerate(StudentClass):
            for sub, subClassList in enumerate(classList):
                if classId in subClassList:
                    studentElement = etree.SubElement(classElement, 'student')
                    studentElement.set('id', str(studentID + 1))

    xml_string = etree.tostring(root, encoding='UTF-8', pretty_print=True)

    with open('solution_group2.xml', 'wb') as file:
        declaration = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        doctype = b'<!DOCTYPE solution PUBLIC "-//ITC 2019//DTD Problem Format/EN" "http://www.itc2019.org/competition-format.dtd">\n\n'
        
        file.write(declaration)
        file.write(doctype)
        file.write(xml_string)
